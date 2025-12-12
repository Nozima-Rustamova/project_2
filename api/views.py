from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.hashers import check_password
from .models import UserModel, PostModel, CommentModel, LikeModel
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer  
from .jwt_provider import generate_tokens, get_user_from_token, refresh_access_token


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = generate_tokens(user)
            return Response({
                "message": "User registered successfully",
                "user": serializer.data,
                "tokens": tokens
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
        
        tokens = generate_tokens(user)
        serializer = UserSerializer(user)
        return Response({
            "message": "Login successful",
            "user": serializer.data,
            "tokens": tokens
        }, status=status.HTTP_200_OK)
    

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        new_access_token = refresh_access_token(refresh_token)
        if new_access_token:
            return Response({
                "access": new_access_token
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)
    

class UserDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user=UserModel.objects.get(id=user_id)
            serializer=UserSerializer(user)
            return Response({
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        

        except Exception as e:
            return Response({"error": str(e)}, 
                            status=status.HTTP_400_BAD_REQUEST)
        


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = get_user_from_token(token)
                if user:
                    serializer = UserSerializer(user)
                    return Response({
                        'user': serializer.data
                    }, status=status.HTTP_200_OK)
                return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"error": "No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = get_user_from_token(token)
                if not user:
                    return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
                
                # Update user fields
                user.profile_info = request.data.get('profile_info', user.profile_info)
                if 'password' in request.data:
                    user.set_password(request.data['password'])
                user.save()
                
                serializer = UserSerializer(user)
                return Response({
                    'message': 'Profile updated successfully',
                    'user': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"error": "No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostListCreateView(APIView):
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get(self, request):
        try:
            posts = PostModel.objects.all().order_by('-created_at')
            serializer = PostSerializer(posts, many=True)
            return Response({
                'posts': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = get_user_from_token(token)
                if not user:
                    return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
                
                content = request.data.get('content', '')
                image = request.data.get('image', None)
                
                post = PostModel.objects.create(
                    author=user,
                    content=content,
                    image=image
                )
                serializer = PostSerializer(post)
                return Response({
                    'message': 'Post created successfully',
                    'post': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({"error": "No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
            serializer = PostSerializer(post)
            return Response({
                'post': serializer.data
            }, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, post_id):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = get_user_from_token(token)
                if not user:
                    return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
                
                post = PostModel.objects.get(id=post_id)
                
                # Check if user is the author
                if post.author.id != user.id:
                    return Response({"error": "You don't have permission to update this post"}, 
                                  status=status.HTTP_403_FORBIDDEN)
                
                post.content = request.data.get('content', post.content)
                if 'image' in request.data:
                    post.image = request.data['image']
                post.save()
                
                serializer = PostSerializer(post)
                return Response({
                    'message': 'Post updated successfully',
                    'post': serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"error": "No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = get_user_from_token(token)
                if not user:
                    return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
                
                post = PostModel.objects.get(id=post_id)
                
                # Check if user is the author
                if post.author.id != user.id:
                    return Response({"error": "You don't have permission to delete this post"}, 
                                  status=status.HTTP_403_FORBIDDEN)
                
                post.delete()
                return Response({
                    'message': 'Post deleted successfully'
                }, status=status.HTTP_200_OK)
            return Response({"error": "No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserPostsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            user = UserModel.objects.get(id=user_id)
            posts = PostModel.objects.filter(author=user).order_by('-created_at')
            serializer = PostSerializer(posts, many=True)
            return Response({
                'posts': serializer.data
            }, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = get_user_from_token(token)
                if not user:
                    return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
                
                post_id = request.data.get('post_id')
                post = PostModel.objects.get(id=post_id)
                
                # Check if like already exists
                existing_like = LikeModel.objects.filter(post=post, user=user).first()
                
                if existing_like:
                    existing_like.delete()
                    return Response({
                        'message': 'Post unliked successfully',
                        'liked': False
                    }, status=status.HTTP_200_OK)
                else:
                    like = LikeModel.objects.create(post=post, user=user)
                    return Response({
                        'message': 'Post liked successfully',
                        'liked': True
                    }, status=status.HTTP_201_CREATED)
            return Response({"error": "No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostLikesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
            likes = LikeModel.objects.filter(post=post)
            serializer = LikeSerializer(likes, many=True)
            return Response({
                'likes': serializer.data,
                'count': likes.count()
            }, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = get_user_from_token(token)
                if not user:
                    return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
                
                post_id = request.data.get('post_id')
                text = request.data.get('text')
                
                if not text:
                    return Response({"error": "Comment text is required"}, status=status.HTTP_400_BAD_REQUEST)
                
                post = PostModel.objects.get(id=post_id)
                comment = CommentModel.objects.create(
                    post=post,
                    author=user,
                    text=text
                )
                serializer = CommentSerializer(comment)
                return Response({
                    'message': 'Comment created successfully',
                    'comment': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({"error": "No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PostCommentsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
            comments = CommentModel.objects.filter(post=post).order_by('-created_at')
            serializer = CommentSerializer(comments, many=True)
            return Response({
                'comments': serializer.data,
                'count': comments.count()
            }, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                user = get_user_from_token(token)
                if not user:
                    return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
                
                comment = CommentModel.objects.get(id=comment_id)
                
                # Check if user is the author
                if comment.author.id != user.id:
                    return Response({"error": "You don't have permission to delete this comment"}, 
                                  status=status.HTTP_403_FORBIDDEN)
                
                comment.delete()
                return Response({
                    'message': 'Comment deleted successfully'
                }, status=status.HTTP_200_OK)
            return Response({"error": "No token provided"}, status=status.HTTP_401_UNAUTHORIZED)
        except CommentModel.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


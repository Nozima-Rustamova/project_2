from httpx import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.hashers import check_password

from api.storage import upload_image
from .models import UserModel, PostModel, CommentModel, LikeModel, FollowModel
from .serializers import UploadPhotoSerializer, UserSerializer, PublicUserSerializer, PostSerializer, CommentSerializer, LikeSerializer, FollowSerializer, ApiResponseSerializer, RegisterSerializer
from .jwt_provider import generate_tokens, get_user_from_token, refresh_access_token, decode_token, blacklist_token
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from .serializers import LoginSerializer, UserSerializer
from .tasks import send_confirmation_email
from .utils import api_response
from .errors import ErrorCode


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'size'
    max_page_size = 100

class RegisterView(APIView):
    permission_classes = [AllowAny]

    parser_classes = [FormParser, MultiPartParser, JSONParser]

    @extend_schema(request=RegisterSerializer, responses={201: ApiResponseSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = generate_tokens(user)
            # enqueue confirmation email (best-effort)
            try:
                send_confirmation_email.delay(user.email, user.username)
            except Exception:
                # don't block registration if the task can't be enqueued
                pass
            return api_response(
                ErrorCode.SUCCESS,
                request=request,
                data={"tokens": tokens},
                status_code=status.HTTP_200_OK
            )
        return api_response(
            ErrorCode.VALIDATION_FAILED,
            request=request,
            data=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

class LoginView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser, JSONParser]

    @extend_schema(request=LoginSerializer, responses={200: ApiResponseSerializer})
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return api_response(
            ErrorCode.INVALID_CREDENTIALS,
            request=request,
            status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return api_response(
                ErrorCode.ACCOUNT_DISABLED,
                request=request,
                status_code=status.HTTP_403_FORBIDDEN
            )

        
        if not user.check_password(password):
            return api_response(
            ErrorCode.INVALID_CREDENTIALS,
            request=request,
            status_code=status.HTTP_401_UNAUTHORIZED
            )

        
        tokens = generate_tokens(user)
        return api_response(
            ErrorCode.SUCCESS,
            request=request,
            data={"tokens": tokens},
            status_code=status.HTTP_200_OK
        )

    

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: ApiResponseSerializer, 400: ApiResponseSerializer})
    def post(self, request):
        refresh_token = request.data.get('refresh')
        new_access_token = refresh_access_token(refresh_token)
        if new_access_token:
            return api_response(ErrorCode.SUCCESS, request=request, message="Access token refreshed", data={"access": new_access_token}, status_code=status.HTTP_200_OK)
        return api_response(ErrorCode.GENERIC_ERROR, request=request, message="Invalid or expired refresh token", status_code=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Logout / revoke a refresh token by blacklisting its jti.

    Expects JSON body: { "refresh": "<refresh_token>" }
    """
    permission_classes = [AllowAny]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: ApiResponseSerializer, 400: ApiResponseSerializer})
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message="Refresh token required", status_code=status.HTTP_400_BAD_REQUEST)

        payload = decode_token(refresh_token)
        if not payload:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message="Invalid token", status_code=status.HTTP_400_BAD_REQUEST)

        success = blacklist_token(payload)
        if success:
            return api_response(ErrorCode.SUCCESS, request=request, message="Logged out (token revoked)", status_code=status.HTTP_200_OK)
        return api_response(ErrorCode.GENERIC_ERROR, request=request, message="Could not blacklist token (maybe expired)", status_code=status.HTTP_400_BAD_REQUEST)
    

class UserDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: PublicUserSerializer, 404: OpenApiTypes.OBJECT}, operation_id='user_retrieve')
    def get(self, request, user_id):
        try:
            user=UserModel.objects.get(id=user_id, is_active=True)
            # Use the public serializer to avoid exposing email/password
            serializer=PublicUserSerializer(user)
            return api_response(ErrorCode.SUCCESS, request=request, message="User retrieved", data={'user': serializer.data}, status_code=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return api_response(ErrorCode.USER_NOT_FOUND, request=request, message="User not found", status_code=status.HTTP_404_NOT_FOUND)
        

        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer, 401: OpenApiTypes.OBJECT}, operation_id='current_user')
    @extend_schema(responses={200: PostSerializer(many=True)}, operation_id='posts_list')
    def get(self, request):
        try:
            serializer = UserSerializer(request.user)
            return api_response(ErrorCode.SUCCESS, request=request, message="Current user", data={'user': serializer.data}, status_code=status.HTTP_200_OK)
        except Exception as e:
            return api_response(ErrorCode.USER_NOT_FOUND, request=request, message="User not found", status_code=status.HTTP_401_UNAUTHORIZED)
        
    def post(self, request):
        user = request.user

        if not user.is_active:
            return api_response(
                ErrorCode.ACCOUNT_DISABLED,
                request=request,
                status_code=status.HTTP_410_GONE
            )

        user.soft_delete()

        return api_response(
            ErrorCode.SUCCESS,
            request=request,
            status_code=status.HTTP_200_OK
        )


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=UserSerializer, responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT}, operation_id='update_profile')
    def put(self, request):
        try:
            user = request.user
            
            # Update user fields
            user.profile_info = request.data.get('profile_info', user.profile_info)
            if 'password' in request.data:
                # validate password before setting
                from .validators import validate_password_strength
                validate_password_strength(request.data['password'], username=user.username, email=user.email)
                user.set_password(request.data['password'])
            user.save()
            
            serializer = UserSerializer(user)
            return api_response(ErrorCode.SUCCESS, request=request, message='Profile updated successfully', data={}, status_code=status.HTTP_200_OK)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


class PostListCreateView(APIView):
    # Provide a serializer_class so schema generators can infer request/response
    serializer_class = PostSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get(self, request):
        try:
            posts = PostModel.objects.filter(author__is_active=True).order_by('-created_at')
            serializer = PostSerializer(posts, many=True)
            return Response({
                'posts': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(request=PostSerializer, responses={201: PostSerializer, 200: OpenApiTypes.OBJECT}, operation_id='posts_create')
    def post(self, request):
        try:
            user = request.user
            if not user.is_active:
                return api_response(
                    ErrorCode.ACCOUNT_DISABLED,
                    request=request,
                    status_code=status.HTTP_403_FORBIDDEN
                )

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
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(responses={200: PostSerializer, 404: OpenApiTypes.OBJECT}, operation_id='posts_retrieve')
    def get(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
            serializer = PostSerializer(post)
            return Response({
                'post': serializer.data
            }, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return api_response(ErrorCode.POST_NOT_FOUND, request=request, message="Post not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


class PostUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=PostSerializer, responses={200: PostSerializer, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='posts_update')
    def put(self, request, post_id):
        try:
            user = request.user
            if not user.is_active:
                return api_response(
                    ErrorCode.ACCOUNT_DISABLED,
                    request=request,
                    status_code=status.HTTP_403_FORBIDDEN
                    )   
            
            post = PostModel.objects.get(id=post_id)
            
            # Check if user is the author
            if post.author.id != user.id:
                return api_response(ErrorCode.GENERIC_ERROR, request=request, message="You don't have permission to update this post", status_code=status.HTTP_403_FORBIDDEN)
            
            post.content = request.data.get('content', post.content)
            if 'image' in request.data:
                post.image = request.data['image']
            post.save()
            
            serializer = PostSerializer(post)
            return Response({
                'message': 'Post updated successfully',
                'post': serializer.data
            }, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return api_response(ErrorCode.POST_NOT_FOUND, request=request, message="Post not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='posts_delete')
    def delete(self, request, post_id):
        try:
            user = request.user
            if not user.is_active:
               return api_response(
                    ErrorCode.ACCOUNT_DISABLED,
                    request=request,
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            post = PostModel.objects.get(id=post_id)
            
            # Check if user is the author
            if post.author.id != user.id:
                return api_response(ErrorCode.GENERIC_ERROR, request=request, message="You don't have permission to delete this post", status_code=status.HTTP_403_FORBIDDEN)
            
            post.delete()
            return Response({
                'message': 'Post deleted successfully'
            }, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return api_response(ErrorCode.POST_NOT_FOUND, request=request, message="Post not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


class UserPostsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='user_posts_list')
    def get(self, request, user_id):
        try:
            user = UserModel.objects.get(id=user_id, is_active=True)
            posts = PostModel.objects.filter(author=user).order_by('-created_at')
            serializer = PostSerializer(posts, many=True)
            return Response({
                'posts': serializer.data
            }, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return api_response(ErrorCode.GENERIC_ERROR, "User not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT, 201: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='like_toggle')
    def post(self, request):
        try:
            user = request.user
            if not user.is_active:
                return api_response(
                    ErrorCode.ACCOUNT_DISABLED,
                    request=request,
                    status_code=status.HTTP_403_FORBIDDEN
                    )
            
            post_id = request.data.get('post_id')
            post = PostModel.objects.get(id=post_id)
            
            # Check if like already exists
            existing_like = LikeModel.objects.filter(post=post, user=user, user__is_active=True).first()
            
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
        except PostModel.DoesNotExist:
            return api_response(ErrorCode.POST_NOT_FOUND, "Post not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


class PostLikesView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='post_likes_list')
    def get(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
            likes = LikeModel.objects.filter(
                post=post, user__is_active=True).order_by('-created_at')
            serializer = LikeSerializer(likes, many=True)
            return Response({
                'likes': serializer.data,
                'count': likes.count()
            }, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return api_response(ErrorCode.POST_NOT_FOUND, "Post not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, request=request, message=str(e), status_code=status.HTTP_400_BAD_REQUEST)


class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CommentSerializer, responses={201: CommentSerializer, 400: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='comment_create')
    def post(self, request):
        try:
            user = request.user
            if not user.is_active:
                return api_response(
                ErrorCode.ACCOUNT_DISABLED,
                request=request,
                status_code=status.HTTP_403_FORBIDDEN
                )
            
            post_id = request.data.get('post_id')
            text = request.data.get('text')
            
            if not text:
                return api_response(ErrorCode.GENERIC_ERROR, "Comment text is required", status_code=status.HTTP_400_BAD_REQUEST)
            
            post = PostModel.objects.get(id=post_id)
            comment = CommentModel.objects.create(
                post=post,
                author=user,
                author__is_active=True,
                text=text
            )
            serializer = CommentSerializer(comment)
            return Response({
                'message': 'Comment created successfully',
                'comment': serializer.data
            }, status=status.HTTP_201_CREATED)
        except PostModel.DoesNotExist:
            return api_response(ErrorCode.POST_NOT_FOUND, "Post not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, str(e), status_code=status.HTTP_400_BAD_REQUEST)


class PostCommentsView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: CommentSerializer(many=True), 404: OpenApiTypes.OBJECT}, operation_id='post_comments_list')
    def get(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
            comments = CommentModel.objects.filter(post=post, author__is_active=True).order_by('-created_at')
            serializer = CommentSerializer(comments, many=True)
            return Response({
                'comments': serializer.data,
                'count': comments.count()
            }, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return api_response(ErrorCode.POST_NOT_FOUND, "Post not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, str(e), status_code=status.HTTP_400_BAD_REQUEST)


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='comment_delete')
    def delete(self, request, comment_id):
        try:
            user = request.user
            
            comment = CommentModel.objects.get(id=comment_id)
            
            # Check if user is the author
            if comment.author.id != user.id:
                return Response({"error": "You don't have permission to delete this comment"}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            comment.delete()
            return Response({
                'message': 'Comment deleted successfully'
            }, status=status.HTTP_200_OK)
        except CommentModel.DoesNotExist:
            return Response({"error": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#FOLLOW SYSTEM

class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT, 201: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='follow_toggle')
    def post(self, request, user_id):
        try:
            follower = request.user
            if not follower.is_active:
                return api_response(
                    ErrorCode.ACCOUNT_DISABLED,
                    request=request,
                    status_code=status.HTTP_403_FORBIDDEN
                    )
            
            # Cannot follow yourself
            if follower.id == user_id:
                return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)
            
            following = UserModel.objects.get(id=user_id, is_active=True)
            
            # Check if already following
            existing_follow = FollowModel.objects.filter(follower=follower, following=following).first()
            
            if existing_follow:
                existing_follow.delete()
                return Response({
                    'message': f'You unfollowed {following.username}',
                    'is_following': False
                }, status=status.HTTP_200_OK)
            else:
                FollowModel.objects.create(follower=follower, following=following)
                return Response({
                    'message': f'You are now following {following.username}',
                    'is_following': True
                }, status=status.HTTP_201_CREATED)
        except UserModel.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserFollowersView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='user_followers')
    def get(self, request, user_id):
        try:
            user = UserModel.objects.get(id=user_id)
            followers = FollowModel.objects.filter(following=user, follower__is_active=True)
            serializer = FollowSerializer(followers, many=True)
            return Response({
                'user': user.username,
                'followers': serializer.data,
                'count': followers.count()
            }, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserFollowingView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='user_following')
    def get(self, request, user_id):
        try:
            user = UserModel.objects.get(id=user_id)
            following = FollowModel.objects.filter(follower=user, following__is_active=True)
            serializer = FollowSerializer(following, many=True)
            return Response({
                'user': user.username,
                'following': serializer.data,
                'count': following.count()
            }, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)





class MyPostsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: OpenApiTypes.OBJECT}, operation_id='my_posts_list')
    def get(self, request):
        try:
            user = request.user
            
            # Get pagination parameters
            page = int(request.GET.get('page', 0))
            size = int(request.GET.get('size', 10))
            
            posts = PostModel.objects.filter(author=user).order_by('-created_at')
            
            # Paginate
            paginator = StandardResultsSetPagination()
            paginator.page_size = size
            paginated_posts = paginator.paginate_queryset(posts, request)
            
            serializer = PostSerializer(paginated_posts, many=True)
            
            return Response({
                'posts': serializer.data,
                'total': posts.count(),
                'page': page,
                'size': size
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ==================== GET LIKE COUNT ====================

class GetLikeCountView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT}, operation_id='get_like_count')
    def get(self, request, post_id):
        try:
            post = PostModel.objects.get(id=post_id)
            like_count = LikeModel.objects.filter(post=post, user__is_active=True).count()
            return Response({
                'post_id': post_id,
                'like_count': like_count
            }, status=status.HTTP_200_OK)
        except PostModel.DoesNotExist:
            return api_response(ErrorCode.POST_NOT_FOUND, "Post not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return api_response(ErrorCode.GENERIC_ERROR, str(e), status_code=status.HTTP_400_BAD_REQUEST)
        
# ==================== UPLOAD PROFILE PHOTO ====================
class UploadProfilePhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UploadPhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        photo = serializer.validated_data["photo"]

        # Upload to Supabase
        photo_url = upload_image(photo, folder="profiles")

        # Save URL
        request.user.photo_url = photo_url
        request.user.save(update_fields=["photo_url"])

        return api_response(
            ErrorCode.SUCCESS,
            request=request,
            data={
                "photo_url": photo_url
            },
            status_code=status.HTTP_200_OK
        )
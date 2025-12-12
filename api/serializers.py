from rest_framework import serializers
from .models import UserModel, PostModel, CommentModel, LikeModel

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'profile_info', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        user = UserModel(
            username=validated_data['username'],
            email=validated_data['email'],
            profile_info=validated_data.get('profile_info', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class PostSerializer(serializers.ModelSerializer):
    author_username=serializers.ReadOnlyField(source='author.username')
    likes_count=serializers.SerializerMethodField()
    comments_count=serializers.SerializerMethodField()

    class Meta:
        model = PostModel
        fields = ['id', 'author', 'author_username', 
                  'likes_count', 'comments_count', 
                  'content', 'image', 'created_at', 'updated_at']
        
    def get_likes_count(self, obj):
        return obj.likes.count()
        
    def get_comments_count(self, obj):
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = ['id', 'post', 'author', 'text', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeModel
        fields = ['id', 'post', 'user', 'created_at']
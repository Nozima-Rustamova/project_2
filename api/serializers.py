from rest_framework import serializers
from .models import UserModel, PostModel, CommentModel, LikeModel, FollowModel
from .validators import validate_password_strength
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .errors import ErrorCode

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'profile_info', 'password']
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {
                'write_only': True,
                'help_text': 'Password must be at least 8 characters and include 1 uppercase letter, 1 lowercase letter, 1 digit and 1 special character.'
            },
            'username': {
                'help_text': 'Unique username for the account.'
            },
            'email': {
                'help_text': 'Valid email address.'
            }
        }
    def create(self, validated_data):
        user = UserModel(
            username=validated_data['username'],
            email=validated_data['email'],
            profile_info=validated_data.get('profile_info', '')
        )
        # password already validated in validate_password
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_password(self, value):
        # Use the shared validator which raises serializers.ValidationError
        username = self.initial_data.get('username')
        email = self.initial_data.get('email')
        validate_password_strength(value, username=username, email=email)
        return value

class PostSerializer(serializers.ModelSerializer):
    author_username=serializers.ReadOnlyField(source='author.username')
    likes_count=serializers.SerializerMethodField()
    comments_count=serializers.SerializerMethodField()

    class Meta:
        model = PostModel
        fields = ['id', 'author', 'author_username', 
                  'likes_count', 'comments_count', 
                  'content', 'image', 'created_at', 'updated_at']
        
    @extend_schema_field(OpenApiTypes.INT)
    def get_likes_count(self, obj) -> int:
        return obj.likes.count()
        
    @extend_schema_field(OpenApiTypes.INT)
    def get_comments_count(self, obj) -> int:
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = CommentModel
        fields = ['id', 'post', 'author', 'author_username', 'text', 'created_at']

class LikeSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = LikeModel
        fields = ['id', 'post', 'user', 'user_username', 'created_at']

class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.ReadOnlyField(source='follower.username')
    following_username = serializers.ReadOnlyField(source='following.username')
    
    class Meta:
        model = FollowModel
        fields = ['id', 'follower', 'follower_username', 'following', 'following_username', 'created_at']


class PublicUserSerializer(serializers.ModelSerializer):
    """Serializer for public user data (no email or password)."""
    class Meta:
        model = UserModel
        # intentionally exclude email and password for public endpoints
        fields = ['id', 'username', 'profile_info']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text='Your username', max_length=150)
    password = serializers.CharField(help_text='Your password', write_only=True)


class ApiResponseSerializer(serializers.Serializer):
    """Standard API response shape used across the project.

    Replaced `success: bool` with `error_code: str` per new API contract.
    """
    error_code = serializers.CharField(help_text='Error code ("000" for success)')
    message = serializers.CharField(allow_blank=True)
    data = serializers.DictField(child=serializers.JSONField(), required=False, allow_null=True)


class RegisterSerializer(UserSerializer):
    """Serializer used for registration requests — excludes read-only fields like id.

    Inherits password validation and create() from UserSerializer.
    """
    class Meta(UserSerializer.Meta):
        fields = ['username', 'email', 'profile_info', 'password']

class UploadPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField()
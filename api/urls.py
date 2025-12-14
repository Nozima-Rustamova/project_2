from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    RefreshTokenView,
    CurrentUserView,
    UpdateProfileView,
    UserDetailView,
    PostListCreateView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    UserPostsView,
    LikeToggleView,
    PostLikesView,
    CommentCreateView,
    PostCommentsView,
    CommentDeleteView,
)

urlpatterns = [
    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    
    # User 
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('users/update/', UpdateProfileView.as_view(), name='update-profile'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/posts/', UserPostsView.as_view(), name='user-posts'),
    
    # Post 
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/update/', PostUpdateView.as_view(), name='post-update'),
    path('posts/<int:post_id>/delete/', PostDeleteView.as_view(), name='post-delete'),
    
    # Like 
    path('likes/toggle/', LikeToggleView.as_view(), name='like-toggle'),
    path('posts/<int:post_id>/likes/', PostLikesView.as_view(), name='post-likes'),
    
    # Comment 
    path('comments/create/', CommentCreateView.as_view(), name='comment-create'),
    path('posts/<int:post_id>/comments/', PostCommentsView.as_view(), name='post-comments'),
    path('comments/<int:comment_id>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
]

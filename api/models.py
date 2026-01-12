from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class UserModel(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    profile_info = models.TextField(blank=True)
    photo_url = models.URLField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def soft_delete(self):
        """User deletes their account"""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "deleted_at"])

    def ban(self):
        """Admin ban (NOT deletion)"""
        self.is_active = False
        self.deleted_at = None
        self.save(update_fields=["is_active", "deleted_at"])

    def restore(self):
        """Restore account"""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=["is_active", "deleted_at"])

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return self.username

class PostModel(models.Model):
    author = models.ForeignKey(
        UserModel,
        on_delete=models.PROTECT,   
        related_name="posts"
    )
    content = models.TextField(blank=True)
    image=models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
     return f"Post by {self.author.username} at {self.created_at}"



class CommentModel(models.Model):
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        UserModel,
        on_delete=models.PROTECT,   
        related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
     return f"Comment by {self.author.username} on {self.post}"


class LikeModel(models.Model):
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(
        UserModel,
        on_delete=models.PROTECT,   
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
    def __str__(self):
          return f"{self.user.username} liked {self.post}"


class FollowModel(models.Model):
    follower = models.ForeignKey(UserModel, on_delete=models.PROTECT, related_name='following')
    following = models.ForeignKey(UserModel, on_delete=models.PROTECT, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"




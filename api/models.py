from django.db import models

class UserModel(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    profile_info=models.TextField(blank=True)

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username
    

class PostModel(models.Model):
    author=models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(blank=True)
    image=models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
     return f"Post by {self.author.username} at {self.created_at}"



class CommentModel(models.Model):
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
     return f"Comment by {self.author.username} on {self.post}"


class LikeModel(models.Model):
    post = models.ForeignKey(PostModel, on_delete=models.CASCADE, related_name='likes')
    user=models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
    def __str__(self):
          return f"{self.user.username} liked {self.post}"




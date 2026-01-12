from django.contrib import admin
from .models import UserModel, PostModel, CommentModel, LikeModel, FollowModel



@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'created_date', 'total_posts', 'total_followers', 'total_following')
    list_display_links = ('id', 'username')
    search_fields = ('username', 'email')
    list_filter = ('username',)
    ordering = ('-id',)
    readonly_fields = ('id', 'password', 'created_date', 'total_posts', 'total_followers', 'total_following')
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'username', 'email', 'profile_info')
        }),
        ('Statistics', {
            'fields': ('total_posts', 'total_followers', 'total_following', 'created_date')
        }),
        ('Security', {
            'fields': ('password',),
            'classes': ('collapse',)
        }),
    )
    
    def created_date(self, obj):
        """Display when user was created (using ID as proxy)"""
        return f"User ID: {obj.id}"
    created_date.short_description = 'Registration Info'
    
    def total_posts(self, obj):
        """Count total posts by user"""
        return obj.posts.count()
    total_posts.short_description = 'Total Posts'
    
    def total_followers(self, obj):
        """Count total followers"""
        return obj.followers.count()
    total_followers.short_description = 'Followers'
    
    def total_following(self, obj):
        """Count total following"""
        return obj.following.count()
    total_following.short_description = 'Following'
    
    # Custom action to create new user
    actions = ['create_sample_user']
    
    def create_sample_user(self, request, queryset):
        """Create a sample user (admin action)"""
        from django.contrib import messages
        username = f"user_{UserModel.objects.count() + 1}"
        email = f"{username}@example.com"
        
        user = UserModel.objects.create(
            username=username,
            email=email,
            profile_info=f"Sample user created via admin"
        )
        user.set_password("password123")
        user.save()
        
        messages.success(request, f"User '{username}' created successfully! Password: password123")
    create_sample_user.short_description = "Create sample user"



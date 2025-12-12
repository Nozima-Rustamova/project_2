# Quick Testing Guide

## Step 1: Run the Server
```bash
python manage.py runserver
```

## Step 2: Test with PowerShell (using curl)

### 1. Register a User
```powershell
$body = @{
    username = "testuser"
    email = "test@test.com"
    password = "test123"
    profile_info = "Test user profile"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register/" -Method POST -Body $body -ContentType "application/json"
```

### 2. Login
```powershell
$body = @{
    username = "testuser"
    password = "test123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" -Method POST -Body $body -ContentType "application/json"
$token = $response.tokens.access
Write-Host "Token: $token"
```

### 3. Get Current User (with authentication)
```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/users/me/" -Method GET -Headers $headers
```

### 4. Create a Post
```powershell
$body = @{
    content = "My first post!"
    image = $null
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/posts/" -Method POST -Body $body -Headers $headers -ContentType "application/json"
```

### 5. Get All Posts
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/posts/" -Method GET
```

### 6. Like a Post
```powershell
$body = @{
    post_id = 1
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/likes/toggle/" -Method POST -Body $body -Headers $headers -ContentType "application/json"
```

### 7. Add a Comment
```powershell
$body = @{
    post_id = 1
    text = "Great post!"
} | ConvertTo-Json

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/comments/create/" -Method POST -Body $body -Headers $headers -ContentType "application/json"
```

## Step 3: Using Postman/Thunder Client (Recommended)

### 1. Install Thunder Client Extension in VS Code
- Open VS Code Extensions (Ctrl+Shift+X)
- Search for "Thunder Client"
- Install it

### 2. Create Collection
1. Click Thunder Client icon in sidebar
2. Create new collection: "Social Media API"

### 3. Add Requests

**Register Request:**
- Method: POST
- URL: http://localhost:8000/api/auth/register/
- Body (JSON):
```json
{
    "username": "testuser",
    "email": "test@test.com",
    "password": "test123",
    "profile_info": "Test user"
}
```

**Login Request:**
- Method: POST
- URL: http://localhost:8000/api/auth/login/
- Body (JSON):
```json
{
    "username": "testuser",
    "password": "test123"
}
```
- After sending, copy the access token

**Get Current User:**
- Method: GET
- URL: http://localhost:8000/api/users/me/
- Headers:
  - Key: Authorization
  - Value: Bearer YOUR_ACCESS_TOKEN

**Create Post:**
- Method: POST
- URL: http://localhost:8000/api/posts/
- Headers: Authorization: Bearer YOUR_ACCESS_TOKEN
- Body (JSON):
```json
{
    "content": "My first post!",
    "image": null
}
```

## Common Issues & Solutions

### Issue: "No module named 'rest_framework'"
**Solution:**
```bash
pip install djangorestframework
```

### Issue: "No module named 'rest_framework_simplejwt'"
**Solution:**
```bash
pip install djangorestframework-simplejwt
```

### Issue: "No module named 'jwt'"
**Solution:**
```bash
pip install PyJWT
```

### Issue: "No module named 'PIL'"
**Solution:**
```bash
pip install Pillow
```

### Issue: CORS errors (if testing from frontend)
**Solution:**
```bash
pip install django-cors-headers
```
Then add to settings.py INSTALLED_APPS:
```python
'corsheaders',
```
And MIDDLEWARE:
```python
'corsheaders.middleware.CorsMiddleware',
```
Add:
```python
CORS_ALLOW_ALL_ORIGINS = True  # For development only
```

## Quick Verification Checklist

- [ ] Server runs without errors: `python manage.py runserver`
- [ ] Can register a user
- [ ] Can login and receive tokens
- [ ] Can access protected route with token
- [ ] Can create a post
- [ ] Can view all posts
- [ ] Can like/unlike a post
- [ ] Can add comments
- [ ] Can delete own posts/comments
- [ ] Cannot delete other users' posts/comments

## Expected Server Output

When server is running correctly, you should see:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
December 12, 2025 - 10:00:00
Django version 6.0, using settings 'sm_backend.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## API Endpoints Summary

### Authentication
- POST /api/auth/register/
- POST /api/auth/login/
- POST /api/auth/refresh/

### Users
- GET /api/users/me/ (auth required)
- PUT /api/users/update/ (auth required)
- GET /api/users/<id>/
- GET /api/users/<id>/posts/

### Posts
- GET /api/posts/
- POST /api/posts/ (auth required)
- GET /api/posts/<id>/
- PUT /api/posts/<id>/update/ (auth required, owner only)
- DELETE /api/posts/<id>/delete/ (auth required, owner only)

### Likes
- POST /api/likes/toggle/ (auth required)
- GET /api/posts/<id>/likes/

### Comments
- POST /api/comments/create/ (auth required)
- GET /api/posts/<id>/comments/
- DELETE /api/comments/<id>/delete/ (auth required, owner only)

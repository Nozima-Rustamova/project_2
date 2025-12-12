# Social Media Backend API Documentation

## Base URL
```
http://localhost:8000/api/
```

---

## Authentication APIs

### 1. Register User
**Endpoint:** `POST /api/auth/register/`

**Request Body:**
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "profile_info": "Hello, I'm John!"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "profile_info": "Hello, I'm John!"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

---

### 2. Login
**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
    "username": "john_doe",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "profile_info": "Hello, I'm John!"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
}
```

---

### 3. Refresh Token
**Endpoint:** `POST /api/auth/refresh/`

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## User APIs

### 4. Get Current User (Requires Authentication)
**Endpoint:** `GET /api/users/me/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "profile_info": "Hello, I'm John!"
    }
}
```

---

### 5. Update Profile (Requires Authentication)
**Endpoint:** `PUT /api/users/update/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "profile_info": "Updated bio!",
    "password": "newpassword123"  // Optional
}
```

**Response (200 OK):**
```json
{
    "message": "Profile updated successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "profile_info": "Updated bio!"
    }
}
```

---

### 6. Get User by ID
**Endpoint:** `GET /api/users/<user_id>/`

**Example:** `GET /api/users/1/`

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "profile_info": "Hello, I'm John!"
    }
}
```

---

### 7. Get User's Posts
**Endpoint:** `GET /api/users/<user_id>/posts/`

**Example:** `GET /api/users/1/posts/`

**Response (200 OK):**
```json
{
    "posts": [
        {
            "id": 1,
            "author": 1,
            "content": "My first post!",
            "image": null,
            "created_at": "2025-12-12T10:30:00Z",
            "updated_at": "2025-12-12T10:30:00Z"
        }
    ]
}
```

---

## Post APIs

### 8. List All Posts
**Endpoint:** `GET /api/posts/`

**Response (200 OK):**
```json
{
    "posts": [
        {
            "id": 1,
            "author": 1,
            "content": "My first post!",
            "image": "/media/post_images/photo.jpg",
            "created_at": "2025-12-12T10:30:00Z",
            "updated_at": "2025-12-12T10:30:00Z"
        }
    ]
}
```

---

### 9. Create Post (Requires Authentication)
**Endpoint:** `POST /api/posts/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "content": "This is my new post!",
    "image": null  // Or image file
}
```

**Response (201 Created):**
```json
{
    "message": "Post created successfully",
    "post": {
        "id": 2,
        "author": 1,
        "content": "This is my new post!",
        "image": null,
        "created_at": "2025-12-12T11:00:00Z",
        "updated_at": "2025-12-12T11:00:00Z"
    }
}
```

---

### 10. Get Post by ID
**Endpoint:** `GET /api/posts/<post_id>/`

**Example:** `GET /api/posts/1/`

**Response (200 OK):**
```json
{
    "post": {
        "id": 1,
        "author": 1,
        "content": "My first post!",
        "image": null,
        "created_at": "2025-12-12T10:30:00Z",
        "updated_at": "2025-12-12T10:30:00Z"
    }
}
```

---

### 11. Update Post (Requires Authentication - Author Only)
**Endpoint:** `PUT /api/posts/<post_id>/update/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "content": "Updated post content"
}
```

**Response (200 OK):**
```json
{
    "message": "Post updated successfully",
    "post": {
        "id": 1,
        "author": 1,
        "content": "Updated post content",
        "image": null,
        "created_at": "2025-12-12T10:30:00Z",
        "updated_at": "2025-12-12T11:30:00Z"
    }
}
```

---

### 12. Delete Post (Requires Authentication - Author Only)
**Endpoint:** `DELETE /api/posts/<post_id>/delete/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "message": "Post deleted successfully"
}
```

---

## Like APIs

### 13. Like/Unlike Post (Requires Authentication)
**Endpoint:** `POST /api/likes/toggle/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "post_id": 1
}
```

**Response (201 Created or 200 OK):**
```json
{
    "message": "Post liked successfully",
    "liked": true
}
```
or
```json
{
    "message": "Post unliked successfully",
    "liked": false
}
```

---

### 14. Get Post Likes
**Endpoint:** `GET /api/posts/<post_id>/likes/`

**Example:** `GET /api/posts/1/likes/`

**Response (200 OK):**
```json
{
    "likes": [
        {
            "id": 1,
            "post": 1,
            "user": 2,
            "created_at": "2025-12-12T10:45:00Z"
        }
    ],
    "count": 1
}
```

---

## Comment APIs

### 15. Create Comment (Requires Authentication)
**Endpoint:** `POST /api/comments/create/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "post_id": 1,
    "text": "Great post!"
}
```

**Response (201 Created):**
```json
{
    "message": "Comment created successfully",
    "comment": {
        "id": 1,
        "post": 1,
        "author": 2,
        "text": "Great post!",
        "created_at": "2025-12-12T11:00:00Z"
    }
}
```

---

### 16. Get Post Comments
**Endpoint:** `GET /api/posts/<post_id>/comments/`

**Example:** `GET /api/posts/1/comments/`

**Response (200 OK):**
```json
{
    "comments": [
        {
            "id": 1,
            "post": 1,
            "author": 2,
            "text": "Great post!",
            "created_at": "2025-12-12T11:00:00Z"
        }
    ],
    "count": 1
}
```

---

### 17. Delete Comment (Requires Authentication - Author Only)
**Endpoint:** `DELETE /api/comments/<comment_id>/delete/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "message": "Comment deleted successfully"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
    "error": "Error message here"
}
```

### 401 Unauthorized
```json
{
    "error": "Invalid token" 
}
```

### 403 Forbidden
```json
{
    "error": "You don't have permission to perform this action"
}
```

### 404 Not Found
```json
{
    "error": "Resource not found"
}
```

---

## Testing with Postman/Thunder Client

### Step 1: Register a User
- Send POST request to `http://localhost:8000/api/auth/register/`
- Copy the access token from response

### Step 2: Test Authentication
- Send GET request to `http://localhost:8000/api/users/me/`
- Add header: `Authorization: Bearer <your_access_token>`

### Step 3: Create a Post
- Send POST request to `http://localhost:8000/api/posts/`
- Add Authorization header
- Add request body with post content

### Step 4: Test Like and Comment
- Use the post_id from previous step
- Send POST to `/api/likes/toggle/` with post_id
- Send POST to `/api/comments/create/` with post_id and text

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Access tokens expire in 60 minutes
- Refresh tokens expire in 7 days
- Image uploads should use multipart/form-data
- All protected routes require Bearer token in Authorization header

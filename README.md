# Social Media Backend API

A Django REST Framework backend for a social media application with JWT authentication, user management, posts, likes, and comments.

## Features

✅ **Authentication System**
- User registration with password hashing
- JWT-based login/logout
- Token refresh functionality
- Secure password storage

✅ **User Management**
- User profiles
- Update profile information
- View user details
- User-specific posts feed

✅ **Post System**
- Create, read, update, delete posts
- Image upload support
- Post feed (chronological order)
- Author-only edit/delete permissions

✅ **Social Features**
- Like/unlike posts
- Comment on posts
- View post likes and comments
- Delete own comments

✅ **Security**
- JWT authentication
- Permission-based access control
- Author-only modification rights
- Token expiration handling

## Tech Stack

- **Framework:** Django 6.0
- **API:** Django REST Framework
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Database:** SQLite (development)
- **Language:** Python 3.x

## Project Structure

```
sm_backend/
├── api/
│   ├── models.py          # User, Post, Comment, Like models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   ├── urls.py            # API endpoints
│   └── jwt_provider.py    # JWT token utilities
├── sm_backend/
│   ├── settings.py        # Django settings
│   └── urls.py            # Main URL configuration
├── manage.py
├── API_DOCUMENTATION.md   # Complete API docs
└── TESTING_GUIDE.md       # Testing instructions
```

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Nozima-Rustamova/project_2.git
cd project_2/sm_backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install django
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install PyJWT
pip install Pillow
```

Or create a `requirements.txt`:
```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run Server
```bash
python manage.py runserver
```

Server will start at: `http://localhost:8000`

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login user | No |
| POST | `/api/auth/refresh/` | Refresh access token | No |

### Users
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/me/` | Get current user | Yes |
| PUT | `/api/users/update/` | Update profile | Yes |
| GET | `/api/users/<id>/` | Get user by ID | No |
| GET | `/api/users/<id>/posts/` | Get user's posts | No |

### Posts
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/posts/` | List all posts | No |
| POST | `/api/posts/` | Create post | Yes |
| GET | `/api/posts/<id>/` | Get post details | No |
| PUT | `/api/posts/<id>/update/` | Update post | Yes (owner) |
| DELETE | `/api/posts/<id>/delete/` | Delete post | Yes (owner) |

### Likes
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/likes/toggle/` | Like/unlike post | Yes |
| GET | `/api/posts/<id>/likes/` | Get post likes | No |

### Comments
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/comments/create/` | Add comment | Yes |
| GET | `/api/posts/<id>/comments/` | Get post comments | No |
| DELETE | `/api/comments/<id>/delete/` | Delete comment | Yes (owner) |

## Quick Start Example

### 1. Register a User
```bash
POST http://localhost:8000/api/auth/register/
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123",
    "profile_info": "Hello, I'm John!"
}
```

### 2. Login
```bash
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
    "username": "johndoe",
    "password": "securepass123"
}
```

### 3. Create a Post (with token)
```bash
POST http://localhost:8000/api/posts/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
    "content": "My first post!",
    "image": null
}
```

## Documentation

- **API Documentation:** See [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Testing Guide:** See [TESTING_GUIDE.md](TESTING_GUIDE.md)

## Models

### UserModel
- username (unique)
- email (unique)
- password (hashed)
- profile_info

### PostModel
- author (ForeignKey to User)
- content
- image (optional)
- created_at, updated_at

### CommentModel
- post (ForeignKey to Post)
- author (ForeignKey to User)
- text
- created_at

### LikeModel
- post (ForeignKey to Post)
- user (ForeignKey to User)
- created_at
- unique_together (post, user)

## Security Features

- Password hashing using Django's built-in hashers
- JWT token authentication
- Token expiration (60 minutes for access, 7 days for refresh)
- Permission-based access control
- Author-only modification rights
- Input validation using DRF serializers

## Testing

### Using Thunder Client (VS Code)
1. Install Thunder Client extension
2. Import API collection
3. Test endpoints sequentially

### Using Postman
1. Import API endpoints
2. Set Authorization header: `Bearer YOUR_TOKEN`
3. Test CRUD operations

### Using PowerShell
See [TESTING_GUIDE.md](TESTING_GUIDE.md) for PowerShell commands

## Development

### Adding New Features
1. Update models in `api/models.py`
2. Create/update serializers in `api/serializers.py`
3. Add views in `api/views.py`
4. Register URLs in `api/urls.py`
5. Run migrations

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Deployment Considerations

- Set `DEBUG = False` in production
- Use environment variables for SECRET_KEY
- Use PostgreSQL/MySQL instead of SQLite
- Configure ALLOWED_HOSTS
- Set up static/media file serving
- Use gunicorn/uwsgi for production server
- Implement rate limiting
- Add CORS headers for frontend integration

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add some feature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open Pull Request

## License

This project is open source and available for educational purposes.

## Author

**Nozima Rustamova**
- GitHub: [@Nozima-Rustamova](https://github.com/Nozima-Rustamova)

## Acknowledgments

- Django Documentation
- Django REST Framework Documentation
- JWT Documentation

## Support

For issues or questions, please open an issue on GitHub.

---

**Note:** This is a backend API project. For frontend integration, use the access token in the Authorization header for protected routes.

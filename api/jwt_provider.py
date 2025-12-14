from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
import jwt
from .models import UserModel


def generate_tokens(user):
    """
    Generate access and refresh tokens for a given user.
    
    Args: UserModel instance
        
    Returns: dict
    """
    refresh = RefreshToken.for_user(user)
    
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def decode_token(token):
    """
    Decode a JWT token and return its payload.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
        return decoded
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return None


def validate_token(token):
    """
    Validate if a token is valid and not expired.
    
    Args:
        token: JWT token string
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    try:
        UntypedToken(token)
        return True
    except (InvalidToken, TokenError) as e:
        print(f"Token validation failed: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return False


def get_user_from_token(token):
    """
    Extract and return the user object from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        UserModel: User object or None if token is invalid or user not found
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    try:
        user_id = payload.get('user_id')
        if user_id is None:
            print("User ID not found in token")
            return None
            
        user = UserModel.objects.get(id=user_id)
        return user
    except UserModel.DoesNotExist:
        print(f"User with ID {user_id} does not exist")
        return None
    except Exception as e:
        print(f"Error retrieving user: {str(e)}")
        return None


def refresh_access_token(refresh_token):
    """
    Generate a new access token from a refresh token.
    
    Args:
        refresh_token: Refresh token string
        
    Returns:
        str: New access token or None if refresh token is invalid
    """
    try:
        refresh = RefreshToken(refresh_token)
        return str(refresh.access_token)
    except (InvalidToken, TokenError) as e:
        print(f"Invalid refresh token: {str(e)}")
        return None
    except Exception as e:
        print(f"Error refreshing token: {str(e)}")
        return None


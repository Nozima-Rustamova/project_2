from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.conf import settings
from django.core.cache import cache
import jwt
from .models import UserModel
import time


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


def is_token_blacklisted(payload):
    """Return True if token represented by payload has been blacklisted."""
    if not payload:
        return False
    jti = payload.get('jti')
    if not jti:
        return False
    return bool(cache.get(f"blacklist:{jti}"))


def blacklist_token(payload):
    """Blacklist a token payload by storing its jti in cache until expiry.

    Returns True if blacklisted successfully or False otherwise.
    """
    if not payload:
        return False
    jti = payload.get('jti')
    exp = payload.get('exp')
    if not jti or not exp:
        return False
    # exp is a Unix timestamp (seconds)
    ttl = int(exp - time.time())
    if ttl <= 0:
        return False
    cache.set(f"blacklist:{jti}", True, ttl)
    return True


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
    # Check blacklist first
    if is_token_blacklisted(payload):
        print("Token is blacklisted")
        return None
    
    try:
        user_id = payload.get('user_id')
        if user_id is None:
            print("User ID not found in token")
            return None
        # Try quick cache hit to reduce DB read
        cache_key = f"user:{user_id}"
        cached = cache.get(cache_key)
        if cached:
            try:
                user = UserModel.objects.get(id=user_id)
                return user
            except UserModel.DoesNotExist:
                return None

        user = UserModel.objects.get(id=user_id)
        # set a short-lived cache flag indicating user exists
        cache.set(cache_key, True, timeout=120)
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


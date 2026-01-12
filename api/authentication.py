from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .jwt_provider import get_user_from_token


class JWTAuthentication(BaseAuthentication):
    
    
    keyword = 'Bearer'
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return None
        
        parts = auth_header.split()
        
        if len(parts) == 0:
            return None
        
        if parts[0].lower() != self.keyword.lower():
            return None
        
        if len(parts) == 1:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')
        
        if len(parts) > 2:
            raise AuthenticationFailed('Invalid token header. Token string should not contain spaces.')
        
        token = parts[1]
        
        return self.authenticate_credentials(token)
    
    def authenticate_credentials(self, token):
        """
        Validate the token and return the user.
        """
        user = get_user_from_token(token)
        
        if not user:
            raise AuthenticationFailed('Invalid or expired token')
        
        return (user, None)
    
    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 Unauthenticated response.
        """
        return self.keyword

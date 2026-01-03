"""
JWT Authentication for microservices
Validates JWT tokens issued by auth-service
"""
import jwt
from rest_framework import authentication, exceptions
from django.conf import settings
import os


class JWTAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT Authentication that validates tokens without database lookup.
    This allows microservices to authenticate requests independently.
    """
    
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
            
        try:
            # Extract token from "Bearer <token>"
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return None
                
            token = parts[1]
            
            # Decode and verify JWT
            secret_key = os.environ.get('SECRET_KEY', settings.SECRET_KEY)
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=['HS256'],
                options={"verify_exp": True}
            )
            
            # Create a simple user object from payload
            user = JWTUser(payload)
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')


class JWTUser:
    """
    Simple user class that represents a user from JWT payload.
    Does not require database access.
    """
    
    def __init__(self, payload):
        self.id = payload.get('user_id')
        self.username = payload.get('username', '')
        self.email = payload.get('email', '')
        self.role = payload.get('role', 'staff')
        self.is_authenticated = True
        self.is_active = True
        
    def __str__(self):
        return self.username
        
    @property
    def is_staff(self):
        return self.role in ['admin', 'manager']
        
    @property
    def is_superuser(self):
        return self.role == 'admin'


class ServiceAuthentication(authentication.BaseAuthentication):
    """
    Authentication for service-to-service communication.
    Uses a shared secret key.
    """
    
    def authenticate(self, request):
        service_key = request.headers.get('X-Service-Key')
        
        if not service_key:
            return None
            
        expected_key = os.environ.get('SERVICE_SECRET_KEY', 'default-service-key')
        
        if service_key != expected_key:
            raise exceptions.AuthenticationFailed('Invalid service key')
            
        # Return a service user
        return (ServiceUser(), None)


class ServiceUser:
    """Represents an internal service making a request"""
    
    def __init__(self):
        self.id = 0
        self.username = 'internal-service'
        self.is_authenticated = True
        self.is_active = True
        self.is_staff = True
        self.is_superuser = True
        self.role = 'service'

from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
import logging
import user_agents

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    ProfileUpdateSerializer,
    PermissionSerializer,
    RoleSerializer,
    UserActivityLogSerializer,
    LoginHistorySerializer,
    AdminResetPasswordSerializer,
)
from .models import Permission, Role, UserActivityLog, LoginHistory

User = get_user_model()
logger = logging.getLogger(__name__)


# ============= UTILITY FUNCTIONS =============

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent_info(request):
    """Parse user agent string"""
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    try:
        ua = user_agents.parse(ua_string)
        return {
            'user_agent': ua_string,
            'device_type': 'Mobile' if ua.is_mobile else 'Tablet' if ua.is_tablet else 'Desktop',
            'browser': f"{ua.browser.family} {ua.browser.version_string}",
            'os': f"{ua.os.family} {ua.os.version_string}",
        }
    except:
        return {
            'user_agent': ua_string,
            'device_type': 'Unknown',
            'browser': 'Unknown',
            'os': 'Unknown',
        }


def log_user_activity(user, action, request=None, description=None, old_data=None, new_data=None, target_user=None):
    """Log user activity"""
    try:
        log_data = {
            'user': user,
            'action': action,
            'description': description,
            'old_data': old_data,
            'new_data': new_data,
            'target_user': target_user,
        }
        
        if request:
            log_data['ip_address'] = get_client_ip(request)
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        UserActivityLog.objects.create(**log_data)
    except Exception as e:
        logger.error(f"Error logging user activity: {str(e)}")


def log_login_attempt(user, status, request, failure_reason=None):
    """Log login attempt"""
    try:
        ua_info = get_user_agent_info(request)
        
        LoginHistory.objects.create(
            user=user,
            status=status,
            ip_address=get_client_ip(request),
            user_agent=ua_info['user_agent'],
            device_type=ua_info['device_type'],
            browser=ua_info['browser'],
            os=ua_info['os'],
            failure_reason=failure_reason,
        )
    except Exception as e:
        logger.error(f"Error logging login attempt: {str(e)}")


# ============= AUTH VIEWS =============

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login view that returns user info with tokens"""
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    try:
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
                'message': 'Validation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            refresh['username'] = user.username
            refresh['email'] = user.email
            refresh['role'] = user.role
            
            # Log activity
            log_user_activity(user, 'user_create', request, 'User registered')
            
            logger.info(f"User registered: {user.username}")
            
            return Response({
                'success': True,
                'message': 'Registration successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Registration failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    
    if not username or not password:
        return Response({
            'success': False,
            'message': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Try to find user by username or email
        user = User.objects.filter(username=username).first()
        if not user:
            user = User.objects.filter(email=username).first()
        
        if not user:
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if account is locked
        if user.is_locked:
            log_login_attempt(user, 'blocked', request, 'Account locked')
            return Response({
                'success': False,
                'message': f'Account is locked. Try again after {user.locked_until.strftime("%Y-%m-%d %H:%M:%S")}'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check password
        if not user.check_password(password):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = timezone.now() + timezone.timedelta(minutes=30)
                log_user_activity(user, 'account_locked', request, 'Account locked due to too many failed login attempts')
            
            user.save()
            
            log_login_attempt(user, 'failed', request, 'Invalid password')
            
            return Response({
                'success': False,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            log_login_attempt(user, 'failed', request, 'Account disabled')
            return Response({
                'success': False,
                'message': 'Account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_ip = get_client_ip(request)
        user.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        refresh['email'] = user.email
        refresh['role'] = user.role
        refresh['full_name'] = user.full_name
        
        # Log successful login
        log_login_attempt(user, 'success', request)
        log_user_activity(user, 'login', request, 'User logged in')
        
        logger.info(f"User logged in: {user.username}")
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        })
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Login failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """User logout endpoint"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Log logout
        log_user_activity(request.user, 'logout', request, 'User logged out')
        
        return Response({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get or update current user profile"""
    user = request.user
    
    if request.method == 'GET':
        return Response({
            'success': True,
            'user': UserSerializer(user).data
        })
    
    # Store old data for audit
    old_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone_number': user.phone_number,
    }
    
    serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        
        # Log activity
        new_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
        }
        log_user_activity(user, 'profile_update', request, 'Profile updated', old_data, new_data)
        
        return Response({
            'success': True,
            'message': 'Profile updated',
            'user': UserSerializer(user).data
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password"""
    serializer = ChangePasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    
    if not user.check_password(serializer.validated_data['old_password']):
        return Response({
            'success': False,
            'message': 'Current password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    # Log activity
    log_user_activity(user, 'password_change', request, 'Password changed')
    
    return Response({
        'success': True,
        'message': 'Password changed successfully'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """Upload user avatar"""
    if 'avatar' not in request.FILES:
        return Response({
            'success': False,
            'message': 'No avatar file provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    user.avatar = request.FILES['avatar']
    user.save()
    
    # Log activity
    log_user_activity(user, 'avatar_upload', request, 'Avatar uploaded')
    
    return Response({
        'success': True,
        'message': 'Avatar uploaded',
        'avatar_url': user.avatar_url
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    """Validate JWT token"""
    return Response({
        'valid': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'role': request.user.role,
            'full_name': request.user.full_name,
        }
    })


# ============= USER MANAGEMENT (ADMIN) =============

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users (admin only)"""
    
    queryset = User.objects.all().order_by('-created_at')
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Log activity
        log_user_activity(
            request.user, 'user_create', request,
            f'Created user: {user.username}',
            target_user=user
        )
        
        return Response({
            'success': True,
            'message': 'User created successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        old_data = UserSerializer(user).data
        
        serializer = self.get_serializer(user, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        new_data = UserSerializer(user).data
        
        # Log activity
        log_user_activity(
            request.user, 'user_update', request,
            f'Updated user: {user.username}',
            old_data, new_data,
            target_user=user
        )
        
        return Response({
            'success': True,
            'message': 'User updated successfully',
            'user': UserSerializer(user).data
        })
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        
        # Log activity before deletion
        log_user_activity(
            request.user, 'user_delete', request,
            f'Deleted user: {username}',
            target_user=user
        )
        
        user.delete()
        
        return Response({
            'success': True,
            'message': f'User {username} deleted successfully'
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user account"""
        user = self.get_object()
        user.is_active = True
        user.save()
        
        log_user_activity(
            request.user, 'user_activate', request,
            f'Activated user: {user.username}',
            target_user=user
        )
        
        return Response({
            'success': True,
            'message': 'User activated successfully'
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user account"""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        log_user_activity(
            request.user, 'user_deactivate', request,
            f'Deactivated user: {user.username}',
            target_user=user
        )
        
        return Response({
            'success': True,
            'message': 'User deactivated successfully'
        })
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Reset user password (admin action)"""
        user = self.get_object()
        
        serializer = AdminResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data['new_password'])
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()
        
        log_user_activity(
            request.user, 'password_reset', request,
            f'Reset password for user: {user.username}',
            target_user=user
        )
        
        return Response({
            'success': True,
            'message': 'Password reset successfully'
        })
    
    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock a locked user account"""
        user = self.get_object()
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()
        
        log_user_activity(
            request.user, 'account_unlocked', request,
            f'Unlocked user account: {user.username}',
            target_user=user
        )
        
        return Response({
            'success': True,
            'message': 'User account unlocked successfully'
        })
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Change user role"""
        user = self.get_object()
        old_role = user.role
        new_role = request.data.get('role')
        custom_role_id = request.data.get('custom_role_id')
        
        if new_role:
            user.role = new_role
        
        if custom_role_id:
            try:
                custom_role = Role.objects.get(id=custom_role_id)
                user.custom_role = custom_role
            except Role.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Role not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        user.save()
        
        log_user_activity(
            request.user, 'role_change', request,
            f'Changed role for user: {user.username} from {old_role} to {new_role}',
            {'role': old_role},
            {'role': new_role},
            target_user=user
        )
        
        return Response({
            'success': True,
            'message': 'User role changed successfully',
            'user': UserSerializer(user).data
        })


# ============= PERMISSION & ROLE MANAGEMENT =============

class PermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing permissions"""
    
    queryset = Permission.objects.all().order_by('category', 'name')
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = Permission.objects.all().order_by('category', 'name')
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing roles"""
    
    queryset = Role.objects.all().order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        
        if role.is_system:
            return Response({
                'success': False,
                'message': 'Cannot delete system role'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        role.delete()
        
        return Response({
            'success': True,
            'message': 'Role deleted successfully'
        })


# ============= ACTIVITY LOG & LOGIN HISTORY =============

class UserActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user activity logs"""
    
    queryset = UserActivityLog.objects.all()
    serializer_class = UserActivityLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = UserActivityLog.objects.all()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')


class LoginHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing login history"""
    
    queryset = LoginHistory.objects.all()
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        queryset = LoginHistory.objects.all()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_activity_logs(request):
    """Get current user's activity logs"""
    logs = UserActivityLog.objects.filter(user=request.user).order_by('-created_at')[:50]
    serializer = UserActivityLogSerializer(logs, many=True)
    
    return Response({
        'success': True,
        'logs': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_login_history(request):
    """Get current user's login history"""
    history = LoginHistory.objects.filter(user=request.user).order_by('-created_at')[:50]
    serializer = LoginHistorySerializer(history, many=True)
    
    return Response({
        'success': True,
        'history': serializer.data
    })


# ============= GOOGLE OAUTH VIEWS =============

@api_view(['GET'])
@permission_classes([AllowAny])
def google_login_url(request):
    """Get Google OAuth login URL"""
    from django.conf import settings
    
    client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
    redirect_uri = settings.GOOGLE_OAUTH2_REDIRECT_URI
    
    if not client_id:
        return Response({
            'success': False,
            'message': 'Google OAuth not configured'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Google OAuth URL
    google_auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth'
        f'?client_id={client_id}'
        f'&redirect_uri={redirect_uri}'
        '&response_type=code'
        '&scope=openid%20email%20profile'
        '&access_type=offline'
        '&prompt=consent'
    )
    
    return Response({
        'success': True,
        'url': google_auth_url
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def google_callback(request):
    """Handle Google OAuth callback - exchange code for tokens and user info"""
    import requests as http_requests
    from django.conf import settings
    
    code = request.data.get('code')
    
    if not code:
        return Response({
            'success': False,
            'message': 'Authorization code is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Exchange code for tokens
        token_response = http_requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
        )
        
        if token_response.status_code != 200:
            logger.error(f"Google token error: {token_response.text}")
            return Response({
                'success': False,
                'message': 'Failed to get access token from Google'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        # Get user info from Google
        user_info_response = http_requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if user_info_response.status_code != 200:
            logger.error(f"Google user info error: {user_info_response.text}")
            return Response({
                'success': False,
                'message': 'Failed to get user info from Google'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        google_user = user_info_response.json()
        email = google_user.get('email')
        google_id = google_user.get('id')
        name = google_user.get('name', '')
        picture = google_user.get('picture', '')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email not provided by Google'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find or create user
        with transaction.atomic():
            user = User.objects.filter(email=email).first()
            
            if user:
                # Update existing user's Google info
                user.google_id = google_id
                if picture and not user.avatar:
                    user.avatar_url = picture
                user.last_login = timezone.now()
                user.save()
                
                is_new_user = False
            else:
                # Create new user from Google account
                username = email.split('@')[0]
                # Ensure unique username
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Split name
                name_parts = name.split(' ', 1)
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                user = User.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    google_id=google_id,
                    avatar_url=picture,
                    is_active=True,
                    role='staff',  # Default role
                )
                user.set_unusable_password()  # No password for Google users
                user.save()
                
                is_new_user = True
            
            # Check if account is locked
            if user.is_locked:
                return Response({
                    'success': False,
                    'message': f'Account is locked. Try again after {user.locked_until.strftime("%Y-%m-%d %H:%M:%S")}'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if account is active
            if not user.is_active:
                return Response({
                    'success': False,
                    'message': 'Account is disabled'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            refresh['username'] = user.username
            refresh['email'] = user.email
            refresh['role'] = user.role
            
            # Log activity
            log_user_activity(
                user, 
                'google_login', 
                request, 
                f'User logged in via Google {"(new account)" if is_new_user else ""}'
            )
            log_login_attempt(user, 'success', request)
            
            logger.info(f"Google login successful: {user.username}")
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'is_new_user': is_new_user,
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            })
            
    except Exception as e:
        logger.error(f"Google login error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Google login failed',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
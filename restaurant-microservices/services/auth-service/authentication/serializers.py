from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Permission, Role, UserActivityLog, LoginHistory

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer to include user info"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model"""
    
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'description', 'category', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description', 'permissions', 
                  'permission_ids', 'is_system', 'is_active', 'user_count', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'is_system', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        return obj.users.count()
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        role.permissions.set(permission_ids)
        return role
    
    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if permission_ids is not None:
            instance.permissions.set(permission_ids)
        
        return instance


class UserSerializer(serializers.ModelSerializer):
    """Full user serializer"""
    
    full_name = serializers.ReadOnlyField()
    avatar_url = serializers.ReadOnlyField()
    custom_role_detail = RoleSerializer(source='custom_role', read_only=True)
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                  'role', 'custom_role', 'custom_role_detail', 'phone_number', 
                  'avatar', 'avatar_url', 'date_of_birth', 'address', 
                  'is_active', 'is_staff', 'is_superuser', 'permissions',
                  'last_login', 'last_login_ip', 'failed_login_attempts',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'last_login', 'last_login_ip', 'failed_login_attempts', 
                           'created_at', 'updated_at']
    
    def get_permissions(self, obj):
        permissions = obj.get_all_permissions()
        return [p.code for p in permissions]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users (admin only)"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 
                  'last_name', 'role', 'custom_role', 'phone_number', 'date_of_birth', 
                  'address', 'is_active', 'is_staff']
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users (admin only)"""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'role', 'custom_role', 
                  'phone_number', 'date_of_birth', 'address', 'is_active', 'is_staff']


class RegisterSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'phone_number']
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Profile update serializer"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                  'date_of_birth', 'address']


class UserActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for UserActivityLog"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    target_user_username = serializers.CharField(source='target_user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = UserActivityLog
        fields = ['id', 'user', 'user_username', 'action', 'action_display', 
                  'description', 'ip_address', 'user_agent', 'old_data', 'new_data',
                  'target_user', 'target_user_username', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoginHistorySerializer(serializers.ModelSerializer):
    """Serializer for LoginHistory"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LoginHistory
        fields = ['id', 'user', 'user_username', 'status', 'status_display',
                  'ip_address', 'user_agent', 'location', 'device_type', 
                  'browser', 'os', 'failure_reason', 'created_at']
        read_only_fields = ['id', 'created_at']


class AdminResetPasswordSerializer(serializers.Serializer):
    """Admin reset password serializer"""
    
    new_password = serializers.CharField(required=True, validators=[validate_password])
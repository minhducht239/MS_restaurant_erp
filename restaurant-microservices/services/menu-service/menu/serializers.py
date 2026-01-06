from rest_framework import serializers
from .models import MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for MenuItem"""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'price', 'category',
            'image', 'image_url', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class MenuItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating menu items with image upload"""
    
    image = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'image', 'is_available']
    
    def validate_image(self, value):
        """Validate image field - allow empty string as null"""
        if value == '' or value is None:
            return None
        return value
    
    def to_internal_value(self, data):
        """Override to handle empty image string"""
        # Handle case where image is an empty string or 'null' string
        if 'image' in data:
            image_value = data.get('image')
            if image_value == '' or image_value == 'null' or image_value is None:
                # Remove image from data so it won't be updated
                if hasattr(data, 'pop'):
                    data.pop('image', None)
                elif isinstance(data, dict):
                    data = {k: v for k, v in data.items() if k != 'image'}
        return super().to_internal_value(data)

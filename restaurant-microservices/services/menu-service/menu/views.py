from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import MenuItem
from .serializers import MenuItemSerializer, MenuItemCreateSerializer


class MenuItemViewSet(viewsets.ModelViewSet):
    """ViewSet for Menu Items"""
    
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_available']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['category', 'name']
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MenuItemCreateSerializer
        return MenuItemSerializer
    
    def create(self, request, *args, **kwargs):
        """Override create to handle image upload properly"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"=== CREATE MENU ITEM ===")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Request FILES: {request.FILES}")
        logger.info(f"Request DATA keys: {list(request.data.keys())}")
        
        # Copy data to handle image properly
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # Check if image is in FILES
        if 'image' in request.FILES:
            logger.info(f"Image file found: {request.FILES['image'].name}, size: {request.FILES['image'].size}")
            data['image'] = request.FILES['image']
        elif 'image' in data:
            # Remove empty or string image values
            image_value = data.get('image')
            if not image_value or isinstance(image_value, str):
                logger.info(f"Removing invalid image value: {image_value}")
                del data['image']
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Get the created instance and return with full serializer
        instance = serializer.instance
        response_serializer = MenuItemSerializer(instance, context={'request': request})
        
        logger.info(f"Menu item created successfully: {instance.id}")
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Override update to handle image field properly"""
        import logging
        logger = logging.getLogger(__name__)
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        logger.info(f"=== UPDATE MENU ITEM {instance.id} ===")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Request FILES: {request.FILES}")
        logger.info(f"Request DATA keys: {list(request.data.keys())}")
        
        # Copy data to handle image properly
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # Handle image field
        if 'image' in request.FILES:
            logger.info(f"New image file found: {request.FILES['image'].name}")
            data['image'] = request.FILES['image']
        elif 'image' in data:
            image_value = data.get('image')
            # Remove image if it's a string URL, empty string, or None
            if not image_value or isinstance(image_value, str):
                logger.info(f"Removing invalid image value: {image_value}")
                del data['image']
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Refresh instance to get updated data
        instance.refresh_from_db()
        
        # Return full serializer data
        logger.info(f"Menu item updated successfully: {instance.id}")
        return Response(MenuItemSerializer(instance, context={'request': request}).data)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get only available menu items"""
        items = MenuItem.objects.filter(is_available=True)
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get menu items grouped by category"""
        categories = {}
        for choice in MenuItem.CATEGORY_CHOICES:
            category_code = choice[0]
            category_name = choice[1]
            items = MenuItem.objects.filter(category=category_code, is_available=True)
            categories[category_name] = MenuItemSerializer(items, many=True, context={'request': request}).data
        
        return Response(categories)
    
    @action(detail=True, methods=['post'])
    def toggle_availability(self, request, pk=None):
        """Toggle item availability"""
        item = self.get_object()
        item.is_available = not item.is_available
        item.save()
        return Response({
            'success': True,
            'is_available': item.is_available
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def categories(request):
    """Get all available categories"""
    return Response([
        {'code': code, 'name': name}
        for code, name in MenuItem.CATEGORY_CHOICES
    ])

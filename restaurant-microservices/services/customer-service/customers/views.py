from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from decimal import Decimal
from .models import Customer
from .serializers import CustomerSerializer

def calculate_loyalty_points(total):
    """Calculate loyalty points: 1 point per 10,000 VND"""
    return int(float(total) // 10000)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone']
    ordering_fields = ['loyalty_points', 'total_spent', 'created_at']
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def by_phone(self, request):
        phone = request.query_params.get('phone')
        if not phone:
            return Response({'error': 'Phone required'}, status=400)
        
        customer = Customer.objects.filter(phone=phone).first()
        if customer:
            return Response(CustomerSerializer(customer).data)
        return Response({'error': 'Not found'}, status=404)
    
    @action(detail=False, methods=['get'])
    def top_customers(self, request):
        limit = int(request.query_params.get('limit', 10))
        customers = Customer.objects.order_by('-loyalty_points')[:limit]
        return Response(CustomerSerializer(customers, many=True).data)

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow service-to-service calls
def update_from_bill(request):
    """Update customer from billing service"""
    phone = request.data.get('phone')
    customer_name = request.data.get('customer_name', 'Khách hàng')
    total = Decimal(str(request.data.get('total', 0)))
    
    if not phone:
        return Response({'error': 'Phone required'}, status=400)
    
    customer, created = Customer.objects.get_or_create(
        phone=phone,
        defaults={'name': customer_name, 'loyalty_points': 0, 'total_spent': Decimal('0')}
    )
    
    if not created and customer_name:
        customer.name = customer_name
    
    points = calculate_loyalty_points(total)
    customer.loyalty_points += points
    customer.total_spent += total
    customer.visit_count += 1
    customer.last_visit = timezone.now().date()
    customer.save()
    
    return Response({
        'success': True,
        'customer': CustomerSerializer(customer).data,
        'points_added': points
    })

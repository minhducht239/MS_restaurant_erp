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
    
    @action(detail=True, methods=['get'])
    def loyalty_history(self, request, pk=None):
        """Get loyalty history (bills) for a customer"""
        customer = self.get_object()
        
        # Gọi billing service để lấy bills của customer
        try:
            import requests
            import os
            
            billing_service_url = os.environ.get(
                'BILLING_SERVICE_URL',
                'http://billing-service:8000'
            )
            
            response = requests.get(
                f"{billing_service_url}/api/bills/bills/",
                params={'phone': customer.phone},
                timeout=10
            )
            
            if response.status_code == 200:
                bills_data = response.json()
                bills = bills_data.get('results', []) if 'results' in bills_data else bills_data
                
                return Response({
                    'customer': CustomerSerializer(customer).data,
                    'history': bills,
                    'total_transactions': len(bills)
                })
            else:
                return Response({
                    'customer': CustomerSerializer(customer).data,
                    'history': [],
                    'total_transactions': 0,
                    'error': 'Failed to fetch bills'
                })
                
        except Exception as e:
            print(f"Error fetching customer bills: {e}")
            return Response({
                'customer': CustomerSerializer(customer).data,
                'history': [],
                'total_transactions': 0,
                'error': str(e)
            })

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow service-to-service calls
def update_from_bill(request):
    """Update customer from billing service"""
    phone = request.data.get('phone')
    customer_name = request.data.get('customer_name', 'Khách hàng')
    total = Decimal(str(request.data.get('total', 0)))
    original_total = Decimal(str(request.data.get('original_total', total)))
    points_used = int(request.data.get('points_used', 0))  # Điểm đã dùng
    should_earn_points = request.data.get('should_earn_points', True)  # Có cộng điểm không
    
    print(f"🔍 DEBUG Customer Service: phone={phone}, should_earn_points={should_earn_points}, points_used={points_used}, original_total={original_total}")
    
    if not phone:
        return Response({'error': 'Phone required'}, status=400)
    
    customer, created = Customer.objects.get_or_create(
        phone=phone,
        defaults={'name': customer_name, 'loyalty_points': 0, 'total_spent': Decimal('0')}
    )
    
    if not created and customer_name:
        customer.name = customer_name
    
    # Tính điểm mới dựa trên original_total (trước khi trừ điểm)
    points_earned = 0
    if should_earn_points:
        points_earned = calculate_loyalty_points(original_total)
    
    print(f"🔍 DEBUG: points_earned={points_earned}, old_points={customer.loyalty_points}")
    
    # Cập nhật điểm: trừ điểm đã dùng, cộng điểm mới (nếu should_earn_points = True)
    customer.loyalty_points = max(0, customer.loyalty_points - points_used + points_earned)
    customer.total_spent += total
    customer.visit_count += 1
    customer.last_visit = timezone.now().date()
    customer.save()
    
    print(f"🔍 DEBUG: new_points={customer.loyalty_points}")
    
    return Response({
        'success': True,
        'customer': CustomerSerializer(customer).data,
        'points_used': points_used,
        'points_earned': points_earned,
        'points_balance': customer.loyalty_points
    })

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from datetime import timedelta
import requests
import os

from .models import Bill, BillItem
from .serializers import BillSerializer, BillCreateSerializer, BillDetailSerializer


class BillViewSet(viewsets.ModelViewSet):
    """ViewSet for Bills"""
    
    queryset = Bill.objects.all().order_by('-created_at')
    serializer_class = BillSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['date', 'phone']
    search_fields = ['customer', 'phone']
    ordering_fields = ['date', 'total', 'created_at']
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BillDetailSerializer
        if self.action == 'create':
            return BillCreateSerializer
        return BillSerializer
    
    def perform_create(self, serializer):
        bill = serializer.save()
        
        # Notify customer service to update loyalty points
        if bill.phone:
            self._update_customer_loyalty(bill)
    
    def _update_customer_loyalty(self, bill):
        """Call customer service to update loyalty points"""
        try:
            customer_service_url = os.environ.get(
                'CUSTOMER_SERVICE_URL', 
                'http://customer-service:8000'
            )
            
            requests.post(
                f"{customer_service_url}/api/customers/update-from-bill/",
                json={
                    'phone': bill.phone,
                    'customer_name': bill.customer,
                    'total': float(bill.total),
                    'bill_id': bill.id
                },
                headers={'X-Service-Key': os.environ.get('SERVICE_SECRET_KEY', 'default-service-key')},
                timeout=5
            )
        except Exception as e:
            print(f"Failed to update customer loyalty: {e}")
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get billing statistics"""
        today = timezone.now().date()
        
        # Today's stats
        today_bills = Bill.objects.filter(date=today)
        today_total = today_bills.aggregate(Sum('total'))['total__sum'] or 0
        today_count = today_bills.count()
        
        # This month stats
        month_start = today.replace(day=1)
        month_bills = Bill.objects.filter(date__gte=month_start)
        month_total = month_bills.aggregate(Sum('total'))['total__sum'] or 0
        month_count = month_bills.count()
        
        # Average bill value
        avg_bill = Bill.objects.aggregate(Avg('total'))['total__avg'] or 0
        
        return Response({
            'today': {
                'total': float(today_total),
                'count': today_count
            },
            'month': {
                'total': float(month_total),
                'count': month_count
            },
            'average_bill_value': round(float(avg_bill), 2),
            'total_bills': Bill.objects.count()
        })
    
    @action(detail=False, methods=['get'])
    def monthly_revenue(self, request):
        """Get monthly revenue for current year"""
        current_year = timezone.now().year
        
        monthly_data = Bill.objects.filter(
            date__year=current_year
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('total'),
            count=Count('id')
        ).order_by('month')
        
        result = [0] * 12
        for entry in monthly_data:
            month_index = entry['month'].month - 1
            result[month_index] = float(entry['total'])
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def weekly_revenue(self, request):
        """Get daily revenue for current week"""
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        result = [0] * 7
        
        daily_data = Bill.objects.filter(
            date__gte=start_of_week,
            date__lte=today
        ).annotate(
            day=TruncDate('date')
        ).values('day').annotate(
            total=Sum('total')
        )
        
        for entry in daily_data:
            day_index = entry['day'].weekday()
            result[day_index] = float(entry['total'])
        
        return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_stats(request):
    """Dashboard statistics endpoint"""
    total_orders = Bill.objects.count()
    total_revenue = Bill.objects.aggregate(Sum('total'))['total__sum'] or 0
    avg_order = Bill.objects.aggregate(Avg('total'))['total__avg'] or 0
    
    # Monthly data
    current_year = timezone.now().year
    monthly_data = [0] * 12
    
    bills_by_month = Bill.objects.filter(
        date__year=current_year
    ).values('date__month').annotate(
        total=Sum('total')
    )
    
    for entry in bills_by_month:
        month_index = entry['date__month'] - 1
        monthly_data[month_index] = float(entry['total'])
    
    return Response({
        'totalOrders': total_orders,
        'totalRevenue': float(total_revenue),
        'averageOrderValue': round(float(avg_order)),
        'monthlyData': monthly_data
    })

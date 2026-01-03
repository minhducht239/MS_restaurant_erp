from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from .models import Staff
from .serializers import StaffSerializer

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['name', 'phone']
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_staff = Staff.objects.filter(is_active=True).count()
        total_salary = Staff.objects.filter(is_active=True).aggregate(Sum('salary'))['salary__sum'] or 0
        by_role = {}
        for role, name in Staff.ROLE_CHOICES:
            by_role[role] = Staff.objects.filter(role=role, is_active=True).count()
        return Response({'total_staff': total_staff, 'total_salary': float(total_salary), 'by_role': by_role})
    
    @action(detail=False, methods=['get'])
    def roles(self, request):
        return Response([{'code': code, 'name': name} for code, name in Staff.ROLE_CHOICES])

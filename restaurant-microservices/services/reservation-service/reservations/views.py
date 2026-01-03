from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Reservation
from .serializers import ReservationSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['date', 'status']
    search_fields = ['name', 'phone']
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        reservation = self.get_object()
        reservation.status = 'confirmed'
        reservation.save()
        return Response({'success': True, 'status': reservation.status})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        reservation.status = 'cancelled'
        reservation.save()
        return Response({'success': True, 'status': reservation.status})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        reservation = self.get_object()
        reservation.status = 'completed'
        reservation.save()
        return Response({'success': True, 'status': reservation.status})
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        reservations = Reservation.objects.filter(date=today).exclude(status='cancelled')
        return Response(ReservationSerializer(reservations, many=True).data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        today = timezone.now().date()
        reservations = Reservation.objects.filter(
            date__gte=today, 
            status__in=['pending', 'confirmed']
        ).order_by('date', 'time')[:20]
        return Response(ReservationSerializer(reservations, many=True).data)

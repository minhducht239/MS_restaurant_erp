from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Table, TableOrder, TableOrderItem
from .serializers import TableSerializer, TableOrderSerializer, TableOrderItemSerializer


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'floor']
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        table = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Table.STATUS_CHOICES):
            table.status = new_status
            table.save()
            return Response({'success': True, 'status': table.status})
        return Response({'error': 'Invalid status'}, status=400)
    
    @action(detail=True, methods=['post'])
    def create_order(self, request, pk=None):
        table = self.get_object()
        
        # Check if table already has active order
        if table.orders.filter(is_completed=False).exists():
            return Response({'error': 'Table already has active order'}, status=400)
        
        order = TableOrder.objects.create(
            table=table,
            created_by_id=request.user.id if hasattr(request.user, 'id') else None,
            created_by_name=getattr(request.user, 'username', ''),
            notes=request.data.get('notes', '')
        )
        
        # Update table status
        table.status = 'occupied'
        table.save()
        
        return Response(TableOrderSerializer(order).data, status=201)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        table = self.get_object()
        order = table.orders.filter(is_completed=False).first()
        
        if not order:
            return Response({'error': 'No active order'}, status=400)
        
        item = TableOrderItem.objects.create(
            order=order,
            menu_item_id=request.data.get('menu_item_id'),
            name=request.data.get('name'),
            quantity=request.data.get('quantity', 1),
            price=request.data.get('price'),
            notes=request.data.get('notes', '')
        )
        
        return Response(TableOrderItemSerializer(item).data, status=201)
    
    @action(detail=True, methods=['post'])
    def complete_order(self, request, pk=None):
        table = self.get_object()
        order = table.orders.filter(is_completed=False).first()
        
        if not order:
            return Response({'error': 'No active order'}, status=400)
        
        order.is_completed = True
        order.save()
        
        table.status = 'available'
        table.save()
        
        return Response({
            'success': True,
            'order': TableOrderSerializer(order).data,
            'total': order.get_total()
        })
    
    @action(detail=False, methods=['get'])
    def by_floor(self, request):
        result = {}
        for floor_code, floor_name in Table.FLOOR_CHOICES:
            tables = Table.objects.filter(floor=floor_code)
            result[floor_name] = TableSerializer(tables, many=True).data
        return Response(result)


class TableOrderViewSet(viewsets.ModelViewSet):
    queryset = TableOrder.objects.all()
    serializer_class = TableOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['table', 'is_completed']

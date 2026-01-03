from django.db import models


class Table(models.Model):
    STATUS_CHOICES = (
        ('available', 'Trống'),
        ('occupied', 'Đã có khách'),
        ('reserved', 'Đã đặt trước'),
    )
    
    FLOOR_CHOICES = (
        (0, 'Tầng 1'),
        (1, 'Tầng 2'),
        (2, 'Tầng 3'),
    )
    
    name = models.CharField(max_length=50, verbose_name="Tên bàn")
    capacity = models.IntegerField(default=4, verbose_name="Sức chứa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    floor = models.IntegerField(choices=FLOOR_CHOICES, default=0, verbose_name="Tầng")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    class Meta:
        db_table = 'tables_table'
        ordering = ['floor', 'name']


class TableOrder(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by_id = models.IntegerField(null=True)  # Reference to auth service
    created_by_name = models.CharField(max_length=100, blank=True)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    
    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())
    
    class Meta:
        db_table = 'tables_tableorder'
        ordering = ['-created_at']


class TableOrderItem(models.Model):
    order = models.ForeignKey(TableOrder, on_delete=models.CASCADE, related_name='items')
    menu_item_id = models.IntegerField(null=True)  # Reference to menu service
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_subtotal(self):
        return self.quantity * self.price
    
    class Meta:
        db_table = 'tables_tableorderitem'

from django.db import models


class Bill(models.Model):
    """Bill/Invoice model"""
    
    customer = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=15, blank=True, default='')
    date = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=0)
    original_total = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)  # Tổng tiền trước giảm giá
    table_id = models.IntegerField(null=True, blank=True)  # Reference to table service
    table_name = models.CharField(max_length=50, blank=True, default='')
    staff_id = models.IntegerField(null=True, blank=True)  # Reference to staff service
    staff_name = models.CharField(max_length=100, blank=True, default='')
    # Loyalty points
    customer_id = models.IntegerField(null=True, blank=True)  # Reference to customer service
    points_used = models.IntegerField(default=0)  # Điểm đã dùng
    points_discount = models.DecimalField(max_digits=10, decimal_places=0, default=0)  # Số tiền giảm từ điểm
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Bill #{self.id} - {self.customer} - {self.date}"
    
    class Meta:
        db_table = 'billing_bill'
        ordering = ['-created_at']


class BillItem(models.Model):
    """Bill Item model"""
    
    bill = models.ForeignKey(Bill, related_name='items', on_delete=models.CASCADE)
    menu_item_id = models.IntegerField(null=True)  # Reference to menu service
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    
    @property
    def subtotal(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.item_name} x{self.quantity}"
    
    class Meta:
        db_table = 'billing_billitem'

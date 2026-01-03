from django.db import models


class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('cancelled', 'Đã hủy'),
        ('completed', 'Hoàn thành'),
    )
    
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    people = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    table_id = models.IntegerField(null=True, blank=True)  # Reference to table service
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.date} {self.time}"
    
    class Meta:
        db_table = 'reservation_reservation'
        ordering = ['date', 'time']

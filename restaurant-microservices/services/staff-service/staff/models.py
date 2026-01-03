from django.db import models

class Staff(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Quản lý'),
        ('cashier', 'Thu ngân'),
        ('chef', 'Đầu bếp'),
        ('waiter', 'Phục vụ'),
        ('janitor', 'Vệ sinh'),
    )

    name = models.CharField(max_length=100, verbose_name="Tên nhân viên")
    phone = models.CharField(max_length=15, verbose_name="Số điện thoại")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Chức vụ")
    salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Lương")
    hire_date = models.DateField(verbose_name="Ngày vào làm")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"
    
    class Meta:
        db_table = 'staff_staff'
        ordering = ['-created_at']

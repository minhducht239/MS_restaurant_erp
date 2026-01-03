from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    phone = models.CharField(max_length=15, unique=True, db_index=True)
    loyalty_points = models.IntegerField(default=0, db_index=True)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0, db_index=True)
    last_visit = models.DateField(null=True, blank=True, db_index=True)
    visit_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers_customer'
        ordering = ['-loyalty_points', '-total_spent']
    
    def __str__(self):
        return f"{self.name} ({self.phone})"
    
    def get_loyalty_tier(self):
        if self.loyalty_points >= 500: return 'Platinum'
        elif self.loyalty_points >= 200: return 'Gold'
        elif self.loyalty_points >= 100: return 'Silver'
        elif self.loyalty_points >= 50: return 'Bronze'
        return 'Standard'

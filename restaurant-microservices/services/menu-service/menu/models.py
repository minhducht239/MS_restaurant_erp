from django.db import models


class MenuItem(models.Model):
    """Menu Item model"""
    
    CATEGORY_CHOICES = (
        ('food', 'Food'),
        ('drink', 'Drink'),
        ('dessert', 'Dessert'),
        ('appetizer', 'Appetizer'),
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.price}"
    
    class Meta:
        db_table = 'menu_menuitem'
        ordering = ['category', 'name']

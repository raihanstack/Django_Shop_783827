from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.cart.models import Cart


class User(AbstractUser):
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username

    def get_active_cart(self):
        """Get or create active cart for user"""
        cart, created = Cart.objects.get_or_create(
            user=self,
            defaults={'session_id': None}
        )
        return cart

    def get_orders(self):
        """Get user's orders ordered by creation date"""
        return self.orders.all().order_by('-created_at')
    

class Config(models.Model):
    site_title = models.CharField(max_length=255, default="Shop")
    header_top = models.CharField(max_length=255, default='header top offer')


    class Meta:
        verbose_name_plural = "Configs"

    def __str__(self):
        return f'{self.site_title} - Config'

    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    whatsapp_number = models.CharField(max_length=20, null=True, blank=True)
    messanger_url = models.URLField(null=True, blank=True)
    facebook_page_url = models.URLField( null=True, blank=True)

    delivery_cost = models.IntegerField(default=0)
    delivery_cost_dhaka = models.IntegerField(default=0)

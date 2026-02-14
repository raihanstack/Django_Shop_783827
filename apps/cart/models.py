from django.db import models
from django.core.validators import MinValueValidator
from apps.product.models import Product, Size, Color



class Cart(models.Model):
    user = models.OneToOneField('main.User', on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    session_id = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart - {self.user.username if self.user else self.session_id}"

    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())

    def get_total_price(self):
        """Calculate total price of all items in cart"""
        return sum(item.get_total_price() for item in self.items.all())

    def clear_cart(self):
        """Remove all items from cart"""
        self.items.all().delete()

    def add_item(self, product, quantity=1, size=None, color=None):
        """Add item to cart or update quantity if exists"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            size=size,
            color=color,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.product.price * self.quantity

    def can_add_quantity(self, additional_quantity=1):
        """Check if additional quantity can be added"""
        return self.product.can_order(self.quantity + additional_quantity)


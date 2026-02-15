from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.html import format_html
from django.db.models import Count
from django.contrib.admin import SimpleListFilter
from apps.product.models import Product, Category, Size, Color, Image
from apps.order.models import Order, OrderItem  # Keeping only Order and OrderItem
from .models import User, Config

# Hide default admin sections
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Site)
except admin.sites.NotRegistered:
    pass

try:
    from robots.models import Rule
    admin.site.unregister(Rule)
except Exception:
    pass

# Custom Admin Site Configuration
admin.site.site_header = "Admin Dashboard"
admin.site.site_title = "Admin"

# ---------------- Custom Filters ----------------
class StockLevelFilter(SimpleListFilter):
    title = 'Stock Level'
    parameter_name = 'stock_level'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock'),
            ('low_stock', 'Low Stock (< 10)'),
            ('out_of_stock', 'Out of Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock_quantity__gt=0)
        elif self.value() == 'low_stock':
            return queryset.filter(stock_quantity__lt=10, stock_quantity__gt=0)
        elif self.value() == 'out_of_stock':
            return queryset.filter(stock_quantity=0)

class OrderStatusFilter(SimpleListFilter):
    title = 'Order Status'
    parameter_name = 'order_status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Active Orders'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.exclude(status__in=['delivered', 'cancelled'])
        elif self.value() == 'completed':
            return queryset.filter(status='delivered')
        elif self.value() == 'cancelled':
            return queryset.filter(status='cancelled')

# ---------------- Inline Admin Classes ----------------
class SizeInline(admin.TabularInline):
    model = Size
    extra = 1
    fields = ('name',)

class ColorInline(admin.TabularInline):
    model = Color
    extra = 1
    fields = ('name', 'hex_code')

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ('image_preview', 'image', 'alt_text', 'is_primary')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = "Preview"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'size', 'color', 'item_total')
    readonly_fields = fields

    def item_total(self, obj):
        return f"${obj.get_total_price():.2f}"
    item_total.short_description = "Total"

# ---------------- Admin Classes ----------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone', 'first_name', 'last_name', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            order_count=Count('orders')
        )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            product_count=Count('products')
        )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'primary_image_preview', 'name', 'category', 'price', 'stock_status', 'stock_quantity',
        'is_active', 'is_featured'
    )
    list_filter = ('is_active', 'category', StockLevelFilter, 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'primary_image_preview')
    list_editable = ('price', 'stock_quantity', 'is_active', 'is_featured')
    list_per_page = 10
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'sku', 'is_active', 'is_featured')
        }),
        ('Content', {
            'fields': ('short_description', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity')
        }),
        ('Media', {
            'fields': ('primary_image_preview',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ImageInline, SizeInline, ColorInline]

    def stock_status(self, obj):
        if obj.stock_quantity == 0:
            return format_html('<span style="color: red; font-weight: bold;">Out of Stock</span>')
        elif obj.stock_quantity < 10:
            return format_html('<span style="color: orange; font-weight: bold;">Low Stock</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">In Stock</span>')
    stock_status.short_description = "Stock Status"

    def primary_image_preview(self, obj):
        primary_image = obj.get_primary_image()
        if primary_image:
            return format_html(
                '<img src="{}" style="width: 64px; height: 64px; object-fit: cover;" />',
                primary_image.image.url
            )
        return "No Primary Image"
    primary_image_preview.short_description = "Primary Image"

    actions = ['mark_as_active', 'mark_as_inactive', 'add_stock']

    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} products marked as active.')
    mark_as_active.short_description = "Mark selected products as active"

    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} products marked as inactive.')
    mark_as_inactive.short_description = "Mark selected products as inactive"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('order_number', 'created_at', 'user_info', 'status', 'total_amount', 'total_items')
    list_filter = ('status', OrderStatusFilter, 'created_at')
    search_fields = ('order_number', 'user__username', 'address__email')
    readonly_fields = ('user', 'order_number', 'user_info', 'total_amount', 'subtotal', 'total_items', 'created_at', 'shipping_cost', 'address')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]

    def user_info(self, obj):
        if obj.address:
            return f"{obj.address.name} ({obj.address.email if obj.address.email else 'No Email'})"
        elif obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "Guest Order"
    user_info.short_description = "Customer"

    def total_items(self, obj):
        return obj.get_total_items()
    total_items.short_description = "Items"

    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} orders marked as confirmed.')
    mark_as_confirmed.short_description = "Mark selected orders as confirmed"

    def mark_as_shipped(self, request, queryset):
        orders = queryset.filter(status__in=['confirmed', 'processing'])
        updated = 0
        for order in orders:
            order.mark_as_shipped()
            updated += 1
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status='shipped').update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ('order_number', 'product', 'quantity', 'size', 'color', 'item_total')
    list_filter = ('order__status', 'order__created_at', 'product__category')
    search_fields = ('order__order_number', 'product__name')

    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = "Order"

    def item_total(self, obj):
        return f"${obj.get_total_price():.2f}"
    item_total.short_description = "Total"

# ---------------- Config model ----------------
admin.site.register(Config)

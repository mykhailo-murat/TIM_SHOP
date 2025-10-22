from django.contrib import admin
from orders.models import Order, OrderItem
from django.utils.safestring import mark_safe


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('image_preview', 'product', 'size', 'quantity', 'price', 'get_total_price')
    readonly_fields = ('image_preview', 'get_total_price')
    can_delete = False

    def image_preview(self, obj):
        if obj.product.main_image:
            return mark_safe(f'<img src="{obj.product.main_image_url}" style="max-height: 100px; object-fit: cover;">')
        return mark_safe('<span style="color: gray;">No Image </span>')

    image_preview.short_description = 'Image'

    def get_total_price(self, obj):
        try:
            return obj.get_total_price()
        except TypeError as e:
            return mark_safe(f'<span style="color: gray;">{e}</span>')

    get_total_price.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email', 'total_price', 'payment_provider', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at', 'payment_provider', 'first_name', 'last_name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'payment_provider', 'total_price', 'stripe_payment_intent_id')
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Info', {
            'fields': ('user', 'email', 'first_name', 'last_name', 'company', 'address1', 'address2', 'city', 'country', 'postal_code', 'phone',
                       'special_instructions', 'total_price')
        }),
        ('Payment and Status', {
            'fields': ('payment_provider', 'status', 'stripe_payment_intent_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + (
                'user', 'email', 'first_name', 'last_name', 'company', 'address1', 'address2', 'city', 'country', 'postal_code', 'phone',)
        return self.readonly_fields

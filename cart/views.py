from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db import transaction
from main.models import Product, ProductSize
from .models import Cart, CartItem
from .forms import AddToCartForm, UpdateCartItemForm
from django.template.response import TemplateResponse
import json


class CartMixin:
    def get_cart(self, request):
        if hasattr(self, 'cart'):
            return request.cart

        if not request.session.session_key:
            request.session.create()

        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)

        request.session['cart_id'] = cart.id
        request.session.modified = True
        return cart


class AddToCartView(CartMixin, View):
    @transaction.atomic
    def post(self, request, slug):
        cart = self.get_cart(request)
        product = get_object_or_404(Product, slug=slug)

        form = AddToCartForm(request.POST, product=product)
        if not form.is_valid():
            return JsonResponse({
                'error': 'Invalid data',
                'errors': form.errors,
            }, status=400)
        size_id = form.cleaned_data.get('size_id')
        if size_id:
            product_size = get_object_or_404(ProductSize, id=size_id, product=product)
        else:
            product_size = product.product_sizes.filter(stock__gt=0).first()
            if not product_size:
                return JsonResponse({
                    'error': 'Product size not found',
                }, status=400)

        quantity = form.cleaned_data['quantity']
        if product_size.stock < quantity:
            return JsonResponse({
                'error': f'Only {product_size.stock} stock is allowed for this product',
            }, status=400)
        existing_item = cart.items.filter(
            product=product,
            product_size=product_size,
        ).first()

        if existing_item:
            total_quantity = existing_item.quantity + quantity
            if total_quantity > product_size.stock:
                return JsonResponse({
                    'error': f'Product size {product_size.stock} exceeds stock',
                }, status=400)

        cart_item = cart.add_product(product, product_size, quantity)

        request.session['cart_id'] = cart.id
        request.session.modified = True

        if request.headers.get('HX-Request'):
            return redirect('cart:cart_modal')  # no redirect just open
        else:
            return JsonResponse({
                'success': True,
                'total_items': cart.total_items,
                'message': f'Successfully added {product.name} to cart',
                'cart_item_id': cart_item.id,
            })


class UpdateCartItemView(CartMixin, View):
    @transaction.atomic
    def post(self, request, item_id):
        cart = self.get_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        quantity = int(request.POST.get('quantity', 1))

        if quantity < 0:
            return JsonResponse({
                'error': 'Quantity cannot be negative',
            }, status=400)
        if quantity == 0:
            cart_item.delete()
        else:
            if quantity > cart_item.product_size.stock:
                return JsonResponse({
                    'error': f'Only {cart_item.product_size.stock} stock is allowed for this product',
                }, status=400)
            cart_item.quantity = quantity
            cart_item.save()
        request.session['cart_id'] = cart.id
        request.session.modified = True

        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',
                'product_size__size',
            ).order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_modal.html', context=context)


class RemoveCartItemView(CartMixin, View):
    def post(self, request, item_id):
        cart = self.get_cart(request)
        try:
            cart_item = cart.items.get(id=item_id)
            cart_item.delete()
            request.session['cart_id'] = cart.id
            request.session.modified = True

            context = {
                'cart': cart,
                'cart_items': cart.items.select_related(
                    'product',
                    'product_size__size',
                ).order_by('-added_at')
            }
            return TemplateResponse(request, 'cart/cart_modal.html', context=context)
        except CartItem.DoesNotExist:
            return JsonResponse({
                'error': 'Item does not exist',
            }, status=400)


class CartCountView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        return JsonResponse({
            'total_items': cart.total_items,
            'subtotal': cart.subtotal,
        })


class CartClearView(CartMixin, View):
    def post(self, request):
        cart = self.get_cart(request)
        cart.clear()
        request.session['cart_id'] = cart.id
        request.session.modified = True

        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'cart/cart_modal.html', {
                'cart': cart
            })
        return JsonResponse({
            'success': True,
            'message': f'Successfully cleared',
        })


class CartSummaryView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',
                'product_size__size',
            ).order_by('-added_at')
        }
        return TemplateResponse(request, 'cart/cart_summary.html', context=context)


class CartModalView(CartMixin, View):
    def get(self, request):
        cart = self.get_cart(request)
        context = {
            'cart': cart,
            'cart_items': cart.items.select_related(
                'product',
                'product_size__size',
            ).order_by('-added_at')
        }

        return TemplateResponse(request, 'cart/cart_modal.html', context=context)



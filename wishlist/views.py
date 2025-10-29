from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Wishlist
from main.models import Product
from django.template.response import TemplateResponse


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        wishlist_item.delete()

    html = render_to_string('wishlist/partials/wishlist_button.html', {
        'product': product,
    }, request=request)

    return HttpResponse(html)


@login_required
def wishlist_page(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    if request.headers.get('HX-Request'):
        return render(request, 'wishlist/wishlist_page.html', {'items': items})
    return TemplateResponse(request, 'wishlist/wishlist_page_full.html', {'items': items})

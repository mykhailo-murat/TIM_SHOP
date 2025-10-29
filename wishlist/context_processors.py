from .models import Wishlist


def wishlist_ids(request):
    if request.user.is_authenticated:
        ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        return {'wishlist_ids': list(ids)}
    return {'wishlist_ids': []}

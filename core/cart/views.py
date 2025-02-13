from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from shop.models import ProductProxy
from .cart import Cart

# type hinting
from django.http import HttpRequest


def cart_view(request: HttpRequest):
    cart = Cart(request)
    context = {'cart': cart}
    return render(request, 'cart/cart_view.html', context)


def cart_add(request: HttpRequest):
    cart = Cart(request)
    
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        
        product = get_object_or_404(ProductProxy, id=product_id)
        
        cart.add(product=product, quantity=product_qty)
        
        cart_qty = cart.__len__()
        
        response = JsonResponse({'qty': cart_qty, "product": product.title})
        return response

def cart_delete(request: HttpRequest):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        product_id = request.POST.get('product_id')

        # ✅ Додаємо перевірку, щоб уникнути ValueError
        if not product_id or not product_id.isdigit():
            return JsonResponse({'error': 'Invalid product ID'}, status=400)

        product_id = int(product_id)

        if str(product_id) not in cart.cart:
            return JsonResponse({'error': 'Product not found in cart'}, status=404)

        cart.delete(product_id)

        cart_qty = cart.__len__()
        cart_total = cart.get_total_price()

        return JsonResponse({'qty': cart_qty, 'total': cart_total})

def cart_clear(request: HttpRequest):
    cart = Cart(request)
    
    if request.method == 'POST':
        cart.clear()
        
        response = JsonResponse({'status': 'success'})
        return response


def cart_update(request: HttpRequest):
    cart = Cart(request)
    
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        
        cart.update(product=product_id, new_quantity=product_qty)
        
        cart_qty = cart.__len__()
        cart_total = cart.get_total_price()
        
        response = JsonResponse({'qty': cart_qty, 'total': cart_total})
        return response

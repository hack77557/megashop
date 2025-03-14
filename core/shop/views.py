from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import ListView
from django.contrib import messages

from .models import Category, ProductProxy

# type hinting imports
from django.http import HttpRequest, HttpResponse
from django.db.models import SlugField


#def products_view(request: HttpRequest) -> HttpResponse:
#    products = ProductProxy.objects.all()
#    context = {'products': products}
#    return render(request, 'shop/products.html', context)
class ProductListView(ListView):
    model = ProductProxy
    context_object_name = "products"
    paginate_by = 15
    
    def get_template_names(self) -> list[str]:
        if self.request.htmx:
            return "shop/components/product_list.html"
        return "shop/products.html"


def product_detail_view(request: HttpRequest, slug: SlugField) -> HttpResponse:
    product = get_object_or_404(
        ProductProxy.objects.select_related('category'), slug=slug
    )

    if request.method == 'POST':
        if request.user.is_authenticated:
            if product.reviews.filter(created_by=request.user).exists():
                messages.error(
                    request, "You have already made a review for this product."
                )
            else:
                rating = request.POST.get('rating', 3)
                content = request.POST.get('content', '')
                if content:
                    product.reviews.create(
                        rating=rating, content=content, created_by=request.user, product=product
                    )
                    return redirect(request.path)
        else:
            messages.error(
                request, "You need to be logged in to make a review."
            )
        
    context = {'product': product}
    return render(request, 'shop/product_detail.html', context)


def category_list(request: HttpRequest, slug: SlugField):
    category = get_object_or_404(Category, slug=slug)
    products = ProductProxy.objects.select_related('category').filter(category=category)
    context = {"category": category, "products": products}
    return render(request, 'shop/category_list.html', context)
'''
def get_all_descendants(category):
    descendants = []
    children = category.children.all()
    for child in children:
        descendants.append(child)
        descendants.extend(get_all_descendants(child))
    return descendants

def category_list(request: HttpRequest, slug: SlugField):
    category = get_object_or_404(Category, slug=slug)
    all_categories = [category] + get_all_descendants(category)
    products = ProductProxy.objects.select_related('category').filter(category__in=all_categories)
    context = {"category": category, "products": products}
    return render(request, 'shop/category_list.html', context)
'''

def search_products(request: HttpRequest):
    query = request.GET.get('q')
    products = ProductProxy.objects.filter(title__icontains=query).distinct()
    context = {'products': products}
    if not query or not products:
        return redirect('shop:products')
    return render(request, 'shop/products.html', context)




#from rest_framework.generics import RetrieveAPIView
from rest_framework import generics
from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductDetailtSerializer

from api.permissions import IsAdminOrReadOnly




from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ProductProxy




# Категорії
class CategoryListAPIView(generics.ListAPIView):
    #queryset = Category.objects.all().order_by('name')  # Впорядкування за назвою
    queryset = Category.objects.all().order_by('id')  # Додаємо сортування
    serializer_class = CategorySerializer
    #permission_classes = [IsAdminOrReadOnly]  # Перевірка прав доступу

class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    #permission_classes = [IsAdminOrReadOnly]  # Перевірка прав доступу

# Продукти
class ProductListAPIView(generics.ListAPIView):
    #queryset = Product.objects.all()
    #queryset = ProductProxy.objects.all()
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    ####################################################    permission_classes = [IsAuthenticated]  # Перевірка прав доступу №№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№
    def get(self, request, *args, **kwargs):
        print(f"User: {request.user}")  # Логування
        return super().get(request, *args, **kwargs)
'''
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
'''
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.prefetch_related('product_attributes__attribute', 'images')  # Оптимізація запитів
    serializer_class = ProductDetailtSerializer
    lookup_field = "pk"
    #permission_classes = [IsAdminOrReadOnly]  # Перевірка прав доступу


from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

class ProductImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product')  # Отримуємо ID продукту
        product = get_object_or_404(Product, id=product_id)

        images = request.FILES.getlist('images')  # Отримуємо список завантажених файлів

        for image in images:
            ProductImage.objects.create(product=product, image=image)

        return Response({"message": "Images uploaded successfully"}, status=status.HTTP_201_CREATED)
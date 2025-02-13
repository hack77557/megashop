# from typing import Any
# from django.core.management.base import BaseCommand
# from faker import Faker

# from shop.models import Category, Product

# fake = Faker()


# class Command(BaseCommand):
    
#     def handle(self, *args: Any, **options: Any) -> str | None:
#         fake = Faker()
#         # Create 30 fake products
#         for _ in range(30):
#             product_title = fake.company()
#             product_brand = fake.company()
#             product_description = fake.paragraph(nb_sentences=2)
#             product_price = fake.pydecimal(
#                 left_digits=3, right_digits=2, min_value=1, max_value=999.99
#             )
#             product = Product(
#                 category=Category.objects.first(),
#                 title=product_title,
#                 brand=product_brand,
#                 description=product_description,
#                 slug=fake.slug(),
#                 price=product_price,
#                 available=True,
#                 created_at=fake.date_time(),
#                 updated_at=fake.date_time(),
#                 discount=fake.pyint(min_value=0, max_value=20),
#             )
#             product.save()
#         self.stdout.write(f'Products in DB: {Product.objects.count()}')


##########################################

from typing import Any
from django.core.management.base import BaseCommand
from faker import Faker
from shop.models import Category, Product

fake = Faker()

class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        fake = Faker()
        
        # Check if there is at least one category; if not, create a default one
        category = Category.objects.first()
        if not category:
            category = Category.objects.create(name="Default Category")
        
        # Create 30 fake products
        for _ in range(1000000):
            product_title = fake.company()
            product_brand = fake.company()
            product_description = fake.paragraph(nb_sentences=2)
            product_price = fake.pydecimal(
                left_digits=3, right_digits=2, min_value=1, max_value=999.99
            )
            
            # Create product with a valid category
            product = Product(
                category=category,  # Make sure the category is not None
                title=product_title,
                brand=product_brand,
                description=product_description,
                slug=fake.slug(),
                price=product_price,
                available=True,
                created_at=fake.date_time(),
                updated_at=fake.date_time(),
                discount=fake.pyint(min_value=0, max_value=20),
            )
            product.save()
        
        self.stdout.write(f'Products in DB: {Product.objects.count()}')

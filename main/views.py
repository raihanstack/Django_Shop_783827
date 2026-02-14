from django.shortcuts import render
from apps.product.models import Product
from .models import Config


def index(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)
    context = {
        "featured_products": featured_products
    }
    return render(request, 'index.html', context)

def about(request):
    about_page = Config.objects.first().about_page
    return render(request, 'main/about.html', {"about_page": about_page})

def contact(request):

    return render(request, 'main/contact.html')
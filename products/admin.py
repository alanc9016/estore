from django.contrib import admin

# Register your models here.
from .models import Product, Material, Image

admin.site.register(Product)
admin.site.register(Material)
admin.site.register(Image)

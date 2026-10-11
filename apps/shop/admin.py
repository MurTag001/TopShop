from django.contrib import admin

from .models import Category, Product, Tag, Manufacturer

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Manufacturer)
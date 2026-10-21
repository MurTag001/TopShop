from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Category, Product, Tag, Manufacturer

admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Manufacturer)

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('name', 'price')
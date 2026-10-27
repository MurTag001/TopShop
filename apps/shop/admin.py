from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Category, Product, Tag, Manufacturer, Review, Comment

admin.site.register(Category)
# admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(Manufacturer)

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ('name', 'price')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_active', 'created_at')
    list_filter = ('rating', 'is_active', 'created_at')
    search_fields = ('text', 'user__username', 'product__name')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('text', 'user__username')
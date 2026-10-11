from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home_page_view, name="home_page"),
    path('products/', views.product_list_view, name="product_list"),
    path('products/category/<slug:category_slug>/', views.category_products_view, name="category_products"),
    path('products/tag/<slug:tag_slug>/', views.tag_products_view, name="tag_products"),
    path('products/add/', views.product_add_view, name='product_add'),
    path('products/<slug:product_slug>/', views.shop_detail_view, name='product_detail'),
    path('products/<slug:product_slug>/edit/', views.product_edit_view, name="product_edit"),
    path('products/<slug:product_slug>/remove/', views.product_remove_view, name="product_remove"),
]
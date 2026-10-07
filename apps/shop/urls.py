from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home_page_view, name="home_page"),
    path('products/', views.product_list_view, name="product_list"),
    path('products/add/', views.product_add_view, name='product_add'),
    path('products/<slug:product_slug>/', views.shop_detail_view, name='product_detail'),
    path('products/<slug:product_slug>/edit/', views.product_edit_view, name="product_edit"),
    path('products/<slug:product_slug>/remove/', views.product_remove_view, name="product_remove"),
]
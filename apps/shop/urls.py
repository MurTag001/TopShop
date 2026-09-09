from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home_page_view, name="home_page"),
    path('products/', views.product_list_view, name="product_list"),
    path('products/<int:product_id>/', views.shop_detail_view, name='product_detail'),
    path('products/add/', views.product_add_view, name='product_add'),
]
from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.HomePageView.as_view(), name="home_page"),
    path('products/', views.ProductListView.as_view(), name="product_list"),
    path('products/category/<slug:category_slug>/', views.CategoryProductsView.as_view(), name="category_products"),
    path('products/tag/<slug:tag_slug>/', views.TagProductsView.as_view(), name="tag_products"),
    path('manufacturers/<slug:manufacturer_slug>/', views.ManufacturerProductsView.as_view(), name='manufacturer_products'),
    path('products/add/', views.ProductAddView.as_view(), name='product_add'),
    path('products/<slug:product_slug>/', views.ShopDetailView.as_view(), name='product_detail'),
    path('products/<slug:product_slug>/edit/', views.ProductEditView.as_view(), name="product_edit"),
    path('products/<slug:product_slug>/remove/', views.ProductRemoveView.as_view(), name="product_remove"),
]
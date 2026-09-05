from django.urls import path

from . import views

urlpatterns = [
    path('', views.home_page_view),
    path('products/', views.product_list_view)
]
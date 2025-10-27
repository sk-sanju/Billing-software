from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.home, name='home'),

    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/edit/<int:pk>/', views.customer_edit, name='customer_edit'),
    path('customers/delete/<int:pk>/', views.customer_delete, name='customer_delete'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),

    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/add/', views.invoice_add, name='invoice_add'),
    path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),

    # Payments
    path('payments/add/<int:invoice_id>/', views.payment_add, name='payment_add'),

    path('invoices/download/<int:pk>/', views.download_invoice_pdf, name='download_invoice_pdf'),

]

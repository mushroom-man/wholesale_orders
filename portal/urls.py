# -*- coding: utf-8 -*-
"""
Created on Mon Jan  5 16:25:13 2026

@author: John
"""

from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.client_login, name='login'),
    path('logout/', views.client_logout, name='logout'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/new/', views.new_order, name='new_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('standing-orders/', views.standing_orders, name='standing_orders'),
]
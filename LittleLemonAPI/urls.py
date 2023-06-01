from django.urls import path
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleItemView.as_view()),
    path('groups/manager/users', views.manager),
    path('groups/manager/users/<int:id>', views.single_manager),
    path('groups/delivery-crew/users', views.delivery_crew),
    path('groups/delivery-crew/users/<int:id>', views.single_delivery_crew),
    path('cart/menu-items', views.cart),
    path('categories', views.CategoryView.as_view()),
    path('orders', views.order),
    path('orders/<int:id>', views.orderitem),
]
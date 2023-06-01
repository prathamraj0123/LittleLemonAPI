from rest_framework import serializers
from .models import MenuItem, Cart, Order, OrderItem, Category
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
        
class CartSerializer(serializers.ModelSerializer):
    # Serializer changes for class based cart
    
    # user = serializers.SerializerMethodField('_user')
    # unit_price = serializers.DecimalField(read_only=True, decimal_places=2, max_digits=6, source='menuitem.price')
    # price = serializers.DecimalField(read_only=True, decimal_places=2, max_digits=6)
    # # price = serializers.SerializerMethodField(read_only=True, max_digits=6, decimal_places=2)
    class Meta:
        model = Cart
        fields = ['user','menuitem', 'quantity', 'unit_price', 'price']
        
    # Get current user for generic view, to make user not available while createview, but visible in listview  
    
    # def _user(self, obj):
    #     request = self.context.get('request', None)
    #     if request:
    #         return request.user.id
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
        
        
class OrderMenuItemSerializer(serializers.ModelSerializer):
    menuitem = serializers.StringRelatedField()
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
        

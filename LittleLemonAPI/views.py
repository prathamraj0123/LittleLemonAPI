from rest_framework import generics
from rest_framework.response import Response
from .models import MenuItem, Cart, Category, OrderItem, Order
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, CategorySerializer, OrderItemSerializer, OrderSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser, IsAuthenticated, DjangoModelPermissionsOrAnonReadOnly
from django.contrib.auth.models import User, Group
from .custompermissions import IsManagerOrIsAdmin
import datetime


# Anyone can view/list category
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes=[DjangoModelPermissionsOrAnonReadOnly]


# Manager/Admin can Lists/Create menu-items  
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes=[DjangoModelPermissionsOrAnonReadOnly]
    ordering_fields = ['price']
    filterset_fields = ['price']
    search_fields = ['title', 'category__title']


# Manager/Admin can view/update/delete single item         
class SingleItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes=[DjangoModelPermissionsOrAnonReadOnly]
  
    
# Admin can view/add manager         
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def manager(request):
    # If POST method
    if request.method == 'POST':
        # Get username
        username = request.data['username']
        # If username exists
        if username:
            # Get user if username exits in user model 
            user = get_object_or_404(User, username=username)
            # Get manager group instance
            managers = Group.objects.get(name='Manager')
            # Add user to the group instance
            managers.user_set.add(user)
            # Return success message
            return Response({"message": 'added'}, status.HTTP_201_CREATED)
        
    # If GET method 
    else:
        # Get all users with manager role
        users = User.objects.filter(groups__name='Manager')
        # Serialize all users
        serialized_user = UserSerializer(users, many=True)
        # Return serialized users
        return Response(serialized_user.data)


# Admin can view/remove a single manager                  
@api_view(["GET", "DELETE"])
@permission_classes([IsAdminUser])
def single_manager(request, id):
    # If GET method
    if request.method == 'GET':
        # Get user if id exist in user model and user is in Manager group
        user = get_object_or_404(User, pk=id, groups__name='Manager')
        # Serialize user
        serialized_user = UserSerializer(user)
        # Return serialized user
        return Response(serialized_user.data, status.HTTP_200_OK)
    
    # If POST method
    elif request.method == 'DELETE':
        # Get user if id exist in user model
        user = get_object_or_404(User, pk=id)
        # Get manager group instance
        managers = Group.objects.get(name='Manager')
        # Remove user from the group instance
        managers.user_set.remove(user)
        # Return success message
        return Response({"message": 'removed'}, status.HTTP_200_OK)


# Admin/Manager can view/add delivery crew     
@api_view(['GET', 'POST'])
@permission_classes([IsManagerOrIsAdmin])
def delivery_crew(request):
    # If POST method
    if request.method == 'POST':
        # Get username
        username = request.data['username']
        # If username exists
        if username:
            # Get user if username exits in user model 
            user = get_object_or_404(User, username=username)
            # Get delivery-crew group instance
            delivery = Group.objects.get(name='delivery-crew')
            # Add user to the group instance
            delivery.user_set.add(user)
            # Return success message
            return Response({"message": 'added'}, status.HTTP_201_CREATED) 
    
    # If GET method       
    else:
        # Get all users with delivery-crew role
        users = User.objects.filter(groups__name='delivery-crew')
        # Serialize all users
        serialized_user = UserSerializer(users, many=True)
        # Return serialized users
        return Response(serialized_user.data)
     

# Admin/Manager can view/remove a single delivery crew 
@api_view(["GET", "DELETE"])
@permission_classes([IsManagerOrIsAdmin])
def single_delivery_crew(request, id):
    # If GET method
    if request.method == 'GET':   
        # Get user if id exist in user model and user is in delivery-crew group 
        user = get_object_or_404(User, pk=id, groups__name='delivery-crew')
        # Serialize user
        serialized_user = UserSerializer(user)
        # Return serialized user
        return Response(serialized_user.data, status.HTTP_200_OK)
    
    # If POST method
    elif request.method == 'DELETE':
        # Get user if id exist in user model
        user = get_object_or_404(User, pk=id)
        # Get delivery-crew group instance
        delivery = Group.objects.get(name='delivery-crew')
        # Remove user from the group instance
        delivery.user_set.remove(user)
        # Return success message
        return Response({"message": 'removed'}, status.HTTP_200_OK)


# Authenticated User can view/delete all items. And add new item in cart.        
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart(request):
    # If GET method
    if request.method == 'GET':
        # Get cart items form cart model for current user
        cart_items = Cart.objects.filter(user=request.user)
        # Serialize cart items
        serialized_cart_items = CartSerializer(cart_items, many=True)
        # Return serialized response
        return Response(serialized_cart_items.data)
    
    # If POST method
    if request.method == 'POST':
        # Get POST data
        data = request.data        
        # If menuitem does not exists
        if data.get('menuitem') == None:
            # Return error
            return Response({"message":"menuitem missing"}, status.HTTP_400_BAD_REQUEST)        
        # If quantity does not exists
        if data.get('quantity') == None:
            # Return error
            return Response({"message":"quantity missing"}, status.HTTP_400_BAD_REQUEST)
        # If quantity exists
        else:
            # Check if quantity is valid
            try:
                quantity = int(data["quantity"])
            except:
                return Response({"message":"invalid quantity"}, status.HTTP_400_BAD_REQUEST)
          
            if quantity <= 0:
                return Response({"message":"invalid quantity"}, status.HTTP_400_BAD_REQUEST)                  
        # If user exists in data
        if data.get('user') != None:
            try:
                userid = int(data["user"])
            except:
                return Response({"message":"invalid quantity"}, status.HTTP_400_BAD_REQUEST)
            # If user is not current user          
            if userid != request.user.id:
                # Return error
                return Response({"message":"Incorrect UserId"}, status.HTTP_400_BAD_REQUEST)
        # If user not exists add current user data
        else:
            data["user"] = request.user.id   
        # Get item if menuitem id in menu model
        item = get_object_or_404(MenuItem, pk=data["menuitem"])
        # Add neccesary fields in data i.e. unit_price, price
        data["unit_price"] = float(item.price)
        data["price"] = round(quantity*item.price,2)        
        # Deserialize to check consistent/valid data and save data to cart model
        serialized_cart_items = CartSerializer(data=data)
        serialized_cart_items.is_valid(raise_exception=True)
        serialized_cart_items.save()
        # Return success message
        return Response(serialized_cart_items.data, status.HTTP_201_CREATED)
            
    # If DELETE method 
    if request.method == 'DELETE':
        # Get cart item of current user
        cart_items = Cart.objects.filter(user=request.user)
        # If cart item exists
        if cart_items:
            # Iterate over items
            for item in cart_items:
                # Delete cart items
                item.delete()
            # Return success message
            return Response({"message": "Cart deleted"}, status.HTTP_200_OK)
        # If no cart item 
        else:
            # Return cart already empty message
            return Response({'message':'Cart already empty'}, status.HTTP_204_NO_CONTENT)
        

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order(request):
    if request.method == 'GET':
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            orders = Order.objects.all()
            serialized_orders = OrderSerializer(orders, many=True)
            return Response(serialized_orders.data)   
        elif request.user.groups.filter(name='delivery-crew').exists():
            orders = Order.objects.filter(delivery_crew=request.user)
            serialized_orders = OrderSerializer(orders, many=True)
            return Response(serialized_orders.data)        
        else:
            orders = Order.objects.filter(user=request.user)
            serialized_orders = OrderSerializer(orders, many=True)
            return Response(serialized_orders.data)        
    
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return Response({"message":"cart empty"}, status.HTTP_400_BAD_REQUEST)
        total = 0
        for item in cart_items:
            total = total + item.price   
        date = datetime.date.today()
        order = Order.objects.create(user=request.user, total=total, date=date)
        order.save()
        for item in cart_items:
            orderitem = OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, unit_price=item.unit_price, price=item.price)
            orderitem.save()
            item.delete()
        return Response({"message":"order placed"}, status.HTTP_201_CREATED)
            
            
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def orderitem(request, id):
    if request.method == 'GET':
        if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
            order = get_object_or_404(Order, pk=id)
            serialized_order = OrderSerializer(order)
            return Response(serialized_order.data)  
        
        elif request.user.groups.filter(name='delivery-crew').exists():
            order = get_object_or_404(Order, pk=id, delivery_crew=request.user)
            serialized_order = OrderSerializer(order)
            return Response(serialized_order.data)   
        
        order = get_object_or_404(Order, pk=id, user=request.user)
        orderitem = OrderItem.objects.filter(order=order)
        serialized_orderitem = OrderItemSerializer(orderitem, many=True)
        return Response(serialized_orderitem.data)
    
    if request.user.groups.filter(name='Manager').exists() or request.user.is_superuser:
        if request.method == 'PUT' or request.method == 'PATCH':
            data = request.data
            serialized_order = OrderSerializer(data=data)
            serialized_order.is_valid(raise_exception=True)               
            order = get_object_or_404(Order, pk=id)

            if int(data['user']) != order.user.pk:
                return Response({"message": "user cannot be changed"}, status.HTTP_400_BAD_REQUEST)
                
            if float(data['total']) != order.total:
                return Response({"message": "total cannot me changed"}, status.HTTP_400_BAD_REQUEST)
                
            if data['date'] != str(order.date):
                return Response({"message": "date cannot be changed"}, status.HTTP_400_BAD_REQUEST)
                
            # delivery_crew = User.objects.filter(groups__name='delivery-crew')
            # for crew in delivery_crew:
            #     if data['delivery_crew'] == crew.pk:
            #         order.delivery_crew = crew
            #         order.save()
            #         break
            delivery_crew = get_object_or_404(User, pk=data['delivery_crew'], groups__name='delivery-crew')
            order.delivery_crew = delivery_crew
            order.save()
            # else:
            #     return Response({"message": "delivery crew does not exist"}, status.HTTP_400_BAD_REQUEST)
                    
            if order.delivery_crew == None and int(data['status']) == 1:
                return Response({"message": "delivery crew does not exist"}, status.HTTP_400_BAD_REQUEST)
                
            if data['status'] in [0, 1]:
                    order.status = data['status']
                    order.save()
            else:
                return Response({"message": "Invalid status code"}, status.HTTP_400_BAD_REQUEST)
                             
            return Response({"message": "order updated"}, status.HTTP_200_OK)               
            
        if request.method == 'DELETE':
            order = get_object_or_404(Order, pk=id)
            order.delete()
            return Response({"message": "order deleted"}, status.HTTP_200_OK)
    
    if request.user.groups.filter(name='delivery-crew').exists():   
        if request.method == 'PATCH':
            data = request.data
            serialized_order = OrderSerializer(data=data)
            serialized_order.is_valid(raise_exception=True)               
            order = get_object_or_404(Order, pk=id)
            if order.delivery_crew.pk != request.user.id:
                return Response({"message": "Unauthorized"}, status.HTTP_403_FORBIDDEN)
            if int(data['user']) != order.user.pk:
                return Response({"message": "user cannot be changed"}, status.HTTP_403_FORBIDDEN)
                
            if float(data['total']) != order.total:
                return Response({"message": "total cannot me changed"}, status.HTTP_403_FORBIDDEN)
                
            if data['date'] != str(order.date):
                return Response({"message": "date cannot be changed"}, status.HTTP_403_FORBIDDEN)
                
            if int(data['delivery_crew']) != order.delivery_crew.pk:
                return Response({"message": "You don't have permission to change deliver_crew"}, status.HTTP_403_FORBIDDEN)
                
            if data['status'] in [0, 1]:
                    order.status = data['status']
                    order.save()
            else:
                return Response({"message": "Invalid status code"}, status.HTTP_400_BAD_REQUEST)
                             
            return Response({"message": "order updated"}, status.HTTP_200_OK)

    return Response({"message": "Request cannot be processed"}, status.HTTP_403_FORBIDDEN)
            
        
 
        
        
# def convert_int(value):
#     try:
#         value = int(value)
#         return value
#     except:
#         return Response({"message":"Invalid input"}, status.HTTP_400_BAD_REQUEST)
    
# def convert_float(value):
#     try:
#         value = float(value)
#         return value
#     except:
#         return Response({"message":"Invalid input"}, status.HTTP_400_BAD_REQUEST)



    # if request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='delivery-crew').exists():
    #     if request.method == 'PATCH':
            
        

                 
# class OrderItemView(generics.ListCreateAPIView):
#     def get_queryset(self):
#         request = self.request
#         if request.method == 'GET':
#             return OrderItem.objects.filter(user=request.user)
#     serializer_class = OrderItemSerializer
#     permission_classes = [IsAuthenticated]
    
        
# class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
#     serializer_class = CartSerializer
#     permission_classes=[IsAuthenticated]
#     def get_queryset(self):
#         request = self.request
#         if request.method == 'GET':
#             return Cart.objects.filter(user=request.user)
#         if request.method == 'DELETE':
#             return Cart.objects.filter(user=request.user)
        
#     def perform_create(self, serializer):
#         item = serializer.validated_data
#         menuitem = item["menuitem"]
#         if item["quantity"] <=0:
#             return Response({"message":"quantity not valid"}, status.HTTP_422_UNPROCESSABLE_ENTITY)
#         price = round(menuitem.price*item["quantity"],2)
#         serializer.save(price=price, unit_price=menuitem.price, user=self.request.user)
        
#     # def perform_destroy(self, serializer):
#     #     item = serializer.validate_data
#     #     return Response(item)
#     # def perform_destroy(self, instance):
#     #     return super().perform_destroy(instance)
        
        

    
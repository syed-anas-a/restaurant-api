from rest_framework import status, generics
from rest_framework.views import APIView
from .models import MenuItem, Cart, Order
from .serializers import MenuItemSerializer, CartSerializer, OrderSerializer, OrderStatusSerializer, OrderManagerUpdateSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from .permissions import IsManager
from django.contrib.auth.models import User, Group
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


# Create your views here.

# Group views
class UserGroupManagement(APIView):
    
    permission_classes = [IsManager]

    def get_group(self, group_name):
        group_map = {
            "manager": "Manager",
            "delivery-crew": "Delivery Crew",
        }

        try:
            return Group.objects.get(name=group_map[group_name])
        except (KeyError, Group.DoesNotExist):
            raise NotFound("Group not found!!")

    def get(self, request, group_name):
        group = self.get_group(group_name)
        users = group.user_set.all()
        data = [{"id": user.id, "username": user.username} for user in users]
        return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request, group_name):
        user_id = request.data.get("user_id")
        group = self.get_group(group_name)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found!!")
        group.user_set.add(user)
        return Response({"message": "User added"}, status=status.HTTP_201_CREATED)
    
    def delete(self, request, group_name, userId):
        group = self.get_group(group_name)
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        group.user_set.remove(user)
        return Response({"message": "User removed!!"}, status=status.HTTP_200_OK)


def ensure_customer(user):
    if user.groups.filter(name='Manager').exists() or \
       user.groups.filter(name='Delivery Crew').exists():
        raise PermissionDenied("Only customers can place orders.")

# Menu-item views
class MenuItemList(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer 

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        elif self.request.method == 'POST':
            return [IsManager()]
        return [IsAuthenticated()]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ['title', 'category']
    filterset_fields = ['category', 'featured']
    ordering_fields = ['price', 'title']
    

class MenuItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsManager()]
        return [IsAuthenticatedOrReadOnly()]
    
# Cart View
class CartList(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        ensure_customer(user)
        return Cart.objects.filter(user=user)

    def perform_create(self, serializer):
        ensure_customer(self.request.user)
        serializer.save()

    def delete(self, request, *args, **kwargs):
        ensure_customer(request.user)
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)
    

# Order views
class OrderList(generics.ListCreateAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user


        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()

        if user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)

        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        ensure_customer(self.request.user)
        serializer.save()

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    search_fields = ['id', 'user__username']
    filterset_fields = ['status', 'date']
    ordering_fields = ['date', 'order_value']



class OrderDetail(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return OrderSerializer

        user = self.request.user
        if user.groups.filter(name='Delivery Crew').exists():
            return OrderStatusSerializer

        if user.groups.filter(name='Manager').exists():
            return OrderManagerUpdateSerializer

        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()

        if user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=user)

        return Order.objects.filter(user=user)

    def destroy(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        user = request.user
        if not (
            user.groups.filter(name='Manager').exists() or
            user.groups.filter(name='Delivery Crew').exists()
        ):
            raise PermissionDenied("You do not have permission to update orders.")

        return super().update(request, *args, **kwargs)


    
    

    


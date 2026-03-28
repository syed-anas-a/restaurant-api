from .models import MenuItem, Cart, Order, OrderItem
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerialzer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type':'password'})
    
    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"
        read_only_fields = ['user', 'price']

    def create(self, validated_data):
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']
        user = self.context['request'].user

        validated_data['user'] = user
        validated_data['price'] = menuitem.price * quantity

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            menuitem=menuitem,
            defaults={
                'quantity': quantity,
                'price': validated_data['price']
            }
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * cart_item.menuitem.price
            cart_item.save()

        return cart_item
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        read_only_fields = ['order']
    
from django.db import transaction

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'delivery_crew', 'status', 'order_value', 'date']

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("Cart is empty.")

        order = Order.objects.create(user=user, order_value=0)

        total = 0

        for cart_item in cart_items:
            item_total = cart_item.quantity * cart_item.menuitem.price

            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                price=item_total
            )

            total += item_total

        order.order_value = total
        order.save()

        cart_items.delete()

        return order
    
class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class OrderManagerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['delivery_crew', 'status']

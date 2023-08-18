from rest_framework import serializers
from EApp.models import CustomUser,Product,Order,Category,ItemsInCart,OrderedItem
from .models import PromotionalEmail


class UserManageSerializer(serializers.ModelSerializer):
    Registration_date=serializers.DateTimeField(source='date_joined',read_only=True)

    class Meta:
        model=CustomUser
        fields=['id','username','email','Registration_date','is_active']

class UserDeactivateSerializer(serializers.ModelSerializer):

    class Meta:
        model=CustomUser
        fields=['is_active']

class  OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        exclude=['categories','quantity']

class OrderedItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='item_ordered.product_name', read_only=True)
    class Meta:
        model=OrderedItem
        fields=['product_name','ordered_quantity','ordered_price']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['username','email']

class AdminOrderSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    ordered_items=OrderedItemSerializer(many=True, read_only=True)
    class Meta:
        model=Order
        fields=['id','user','ordered_items','total_amount','date_of_order','status','Address']

class EditOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields=['status']





class PromotionalEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model=PromotionalEmail
        fields=['subject','content']
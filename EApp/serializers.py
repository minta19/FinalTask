from rest_framework import serializers
from .models import CustomUser,Product,Order,Category,ItemsInCart
from AdminBoard.serializers import OrderedItemSerializer

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=['email','username','password']
        extra_kwargs={'password':{'write_only':True}}

    def create(self,validated_data):
        user=CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],

        )
            
        return user

class ProductAddSerialzer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'


class CategoryAddSerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['category_name']

class CategoryViewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','category_name']

class ProductListSerializer(serializers.ModelSerializer):
    categories=serializers.StringRelatedField(many=True)
    stock_availability = serializers.SerializerMethodField()
    class Meta:
        model=Product
        fields=['id','product_name','price','product_image','stock_availability','categories']

    def get_stock_availability(self,obj): 
        return obj.quantity if obj.quantity > 0 else "Out of Stock"
    
class ProductDetailSerializer(serializers.ModelSerializer):
    stock_availability = serializers.SerializerMethodField()
    categories=serializers.StringRelatedField(many=True)
    class Meta:
        model=Product
        fields=['id','product_name','description','price','product_image','categories','stock_availability']

    def get_stock_availability(self,obj):
        return obj.quantity if obj.quantity > 0 else "Out of Stock"
        

class UserPasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

class ProductCartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['product_name','price','quantity','product_image']

class CartItemSerializer(serializers.ModelSerializer):
    product=ProductCartSerializer(read_only=True)
    total_cost=serializers.SerializerMethodField()
    class Meta:
        model=ItemsInCart
        fields=['id','product','Number_of_items','total_cost']

    def get_total_cost(self,obj):
        return obj.Number_of_items * obj.product.price

class CartProductDetailSerializer(serializers.ModelSerializer):
    product=ProductDetailSerializer(read_only=True)
    total_cost=serializers.SerializerMethodField()
    class Meta:
        model=ItemsInCart
        fields=['product','Number_of_items','total_cost']
    
    def get_total_cost(self,obj):
        return obj.Number_of_items * obj.product.price

class EditNumberOfItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=ItemsInCart
        fields=['Number_of_items']


class OrderPlacementSerilaizer(serializers.Serializer):
   cartitem_id=serializers.ListField(child=serializers.IntegerField())
   Address=serializers.CharField()

   def validate(self, attrs):
        cartitem_id=attrs.get('cartitem_id')

        for cart_item_id in cartitem_id:
            try:
              cart_item=ItemsInCart.objects.get(id=cart_item_id)
            except ItemsInCart.DoesNotExist:
               raise serializers.ValidationError("Invalid cart_item_id")
        
            if cart_item.Number_of_items <= 0:
               raise serializers.ValidationError("Cart item quantity must be greater than zero.")
        
            if cart_item.Number_of_items > cart_item.product.quantity:
                raise serializers.ValidationError("No sufficient product available")

        return attrs 
   
class OrderHistorySerializer(serializers.ModelSerializer):
    ordered_items=OrderedItemSerializer(many=True, read_only=True)
    class Meta:
        model=Order
        fields=['id','ordered_items','total_amount','date_of_order','status','Address']

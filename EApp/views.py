from .serializers import (SignupSerializer,ProductAddSerialzer,UserPasswordResetConfirmSerializer,ProductListSerializer,CartItemSerializer,
                          CartProductDetailSerializer,EditNumberOfItemSerializer,OrderPlacementSerilaizer,OrderHistorySerializer,ProductDetailSerializer)

from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import EmailMessage,send_mail
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import PermissionDenied
from django.template.loader import get_template
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .models import Category,Product,Order,CustomUser,ItemsInCart,OrderedItem
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from .paginations import customPagination
from django.utils.html import strip_tags

class Signup(APIView):
    
  def post(self,request):
    serializer=SignupSerializer(data=request.data)
    if serializer.is_valid():
      user=serializer.save()
      try:
         subject='WELCOME TO E-COMMERCE PLATFORM'
         from_email=settings.DEFAULT_FROM_EMAIL
         receiptant_list=[user.email]
         ctx={'username':user.username}
         message=get_template('welcome.html').render(ctx)
         email=EmailMessage(subject,message,from_email,receiptant_list)
         email.content_subtype="html"
         email.send()
                
         return Response({'MESSAGE':'USER CREATED'}, status=status.HTTP_201_CREATED)
      except Exception as e:
                return Response({
                    'ERROR': 'Failed to send email.',
                    'Recipient': receiptant_list,
                    'Content': 'Mail contains Password Reset Link'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
  
class UserPasswordResetView(APIView):
  def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'No account found with this email.'}, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)

        reset_link = f'http://example.com/reset-password/?uid={urlsafe_base64_encode(force_bytes(user.pk))}&token={token}'
        subject = 'Password Reset'
        message = render_to_string('pass_reset.html', {
            'reset_link': reset_link,
            'user': user,
        })
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email],html_message=message)
        except Exception as e:
            return Response({
                'detail': 'An error occurred while sending the password reset email.',
                'recipient_email': user.email,
                'email_content': 'Mail confirming successful registration of the account'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'detail': 'Password reset email sent.'}, status=status.HTTP_200_OK)

class UserPasswordResetConfirmView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserPasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        confirm_password = serializer.validated_data['confirm_password']

        if new_password != confirm_password:
            return Response({'detail': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            User = get_user_model()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({'MESSAGE': 'Password reset successful.'}, status=status.HTTP_200_OK)
        else:
            return Response({'WARNING': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)

class ProductList(generics.ListAPIView):
  
  serializer_class=ProductListSerializer
  pagination_class=customPagination
  queryset=Product.objects.all().order_by('?')
  filter_backends=[filters.DjangoFilterBackend]
  filterset_fields={'categories__category_name': ['exact', 'icontains'],'price':['exact'],'product_name': ['exact', 'icontains'],}
  
  def get_queryset(self):
     queryset= super().get_queryset()
     
     min_price=self.request.query_params.get('min_price')
     if min_price:
        queryset=queryset.filter(price__gte=min_price)
     max_price=self.request.query_params.get('max_price')
     if max_price:
        queryset=queryset.filter(price__lte=max_price)
     return queryset
 

class ProductRetrieve(generics.RetrieveAPIView):
   authentication_classes=[JWTAuthentication]
   serializer_class=ProductDetailSerializer
   queryset=Product.objects.all()

class CartItemsListView(generics.ListAPIView):
   permission_classes=[IsAuthenticated]
   authentication_classes=[JWTAuthentication]
   serializer_class=CartItemSerializer

   def get_queryset(self):
      user=self.request.user
      queryset=ItemsInCart.objects.filter(user=user)
      return queryset
   
class CartItemRetrieve(generics.RetrieveAPIView):
   permission_classes=[IsAuthenticated]
   authentication_classes=[JWTAuthentication]
   serializer_class=CartProductDetailSerializer
   queryset=ItemsInCart.objects.all()


class AddItemToCart(generics.CreateAPIView):
   permission_classes=[IsAuthenticated]
   authentication_classes=[JWTAuthentication]

   def create(self, request, *args, **kwargs):
      user=request.user
      product_id=request.data.get('product_id')
      Number_of_items=int(request.data.get('Number_of_items',1))
      
      try:
         product=Product.objects.get(pk=product_id)
      except Product.DoesNotExist:
         return Response({'detail': 'Product not available.'}, status=status.HTTP_400_BAD_REQUEST)
      
      if product.quantity <=0:
         return Response({"Message":"The product is out of stock . Cannot be added to the cart"},status=status.HTTP_400_BAD_REQUEST)
      try:
         shopping_cart = ItemsInCart.objects.get(user=user,product=product,Number_of_items=Number_of_items)
         return Response({"message": "The item already exists in the cart."}, status=status.HTTP_400_BAD_REQUEST)
      except ItemsInCart.DoesNotExist:
         shopping_cart = ItemsInCart.objects.create(user=user,product=product,Number_of_items=Number_of_items)
         shopping_cart.save()

         return Response({'detail': 'Product added to cart successfully.'}, status=status.HTTP_201_CREATED)

class CartItemUpdate(generics.UpdateAPIView):
   permission_classes=[IsAuthenticated]
   authentication_classes=[JWTAuthentication]
   serializer_class=EditNumberOfItemSerializer
   def get_queryset(self):
        user = self.request.user
        return ItemsInCart.objects.filter(user=user)
   
   def patch(self, request, *args, **kwargs):
      item_in_cart=self.get_object()
      count_of_items=int(request.data.get('Number_of_items',1))

      if count_of_items<=0:
         return Response({"Message":"Count of items need to more than zero"})
      
      item_in_cart.Number_of_items=count_of_items
      item_in_cart.save()
      print(count_of_items)
      serializer=self.get_serializer(item_in_cart)
      return Response(serializer.data)
   
class CartItemDelete(generics.DestroyAPIView):
   permission_classes=[IsAuthenticated]
   authentication_classes=[JWTAuthentication] 
   queryset=ItemsInCart.objects.all()
   serializer_class=CartItemSerializer
   
   def delete(self, request, *args, **kwargs):
      item_in_cart=self.get_object()
      item_in_cart.delete()
      return Response({"message": "Item removed from the cart."}, status=status.HTTP_204_NO_CONTENT)

     
class OrderPlacement(generics.CreateAPIView):
   permission_classes=[IsAuthenticated]
   authentication_classes=[JWTAuthentication]
   serializer_class=OrderPlacementSerilaizer
   queryset=Order.objects.all()

   def post(self, request, *args, **kwargs):
      serializer=self.get_serializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      cartitem_id=serializer.validated_data['cartitem_id']
      Address = serializer.validated_data['Address']
      Payment = serializer.validated_data.get('Payment', 'Cash on Delivery')
      
      total_amount=0
      ordered_products=[]
      user_cart_items = ItemsInCart.objects.filter(user=request.user, id__in=cartitem_id)

      if len(user_cart_items) != len(cartitem_id):
            return Response({'detail': 'items are not in your cart.'}, status=status.HTTP_400_BAD_REQUEST)

      for cart_item in user_cart_items:
         ordered_quantity = cart_item.Number_of_items
         ordered_price = cart_item.product.price
         total_amount += ordered_price * ordered_quantity
         
         ordered_product = OrderedItem(
                order_ref=None,  
                item_ordered=cart_item.product,
                ordered_quantity=ordered_quantity,
                ordered_price=ordered_price
            )
         ordered_products.append(ordered_product)
         

         product = cart_item.product
         product.quantity -= ordered_quantity
         product.save()

     
      order=Order.objects.create(user=request.user,total_amount=total_amount,status='Processing',Address=Address)
      
      for ordered_product in ordered_products:
         ordered_product.order_ref=order
         ordered_product.save()
      
      context={'order':order,'user':request.user,'ordered_products':ordered_products}
      user_recipient_list = [request.user.email]
      admin_recipient_list = ['admin@gmail.com']

      try:
            subject = 'Order Confirmation'
            from_email = settings.DEFAULT_FROM_EMAIL
            user_html_message = render_to_string('order.html', context)
            user_text_message = strip_tags(user_html_message)
            admin_html_message = render_to_string('admin_order.html', context)
            admin_text_message = strip_tags(admin_html_message)
            send_mail(subject, message=user_text_message, from_email=from_email, recipient_list=user_recipient_list, html_message=user_html_message)
            send_mail(subject, message=admin_text_message, from_email=from_email, recipient_list=admin_recipient_list, html_message=admin_html_message)
      except Exception as e:
            return Response({
                'Message':'Order placed',
                'error_message': 'An error occurred while sending the order confirmation email to the user and admin',
                'recipient_list': user_recipient_list + admin_recipient_list,
                'email_content': 'Email contains details of the order placed by the user'
            }, status=500)
      
      return Response({"Message":"order placed"})

class OrderHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderHistorySerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user).order_by('-date_of_order')
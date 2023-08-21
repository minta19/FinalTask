from django.shortcuts import render
from EApp.serializers import (CategoryAddSerializer,CategoryViewSerializer,ProductAddSerialzer,ProductListSerializer,ProductDetailSerializer)
from rest_framework import generics,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from EApp.models import Category,Product,Order,CustomUser,ItemsInCart
from .serializers import UserManageSerializer,UserDeactivateSerializer,AdminOrderSerializer,EditOrderStatusSerializer,PromotionalEmailSerializer
from EApp.paginations import customPagination
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import PromotionalEmail
from rest_framework.exceptions import APIException
from django_filters import rest_framework as filters


class AdminLogin(APIView):
  def post(self,request):
    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(email=email, password=password)

    if user is not None and user.is_staff:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({'access_token': access_token}, status=status.HTTP_200_OK)
    else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
class AdminCategoryAdd(generics.ListCreateAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=CategoryAddSerializer
    authentication_classes=[JWTAuthentication]
    queryset=Category.objects.all()


    def post(self, request, *args, **kwargs):
        resposne= super().post(request, *args, **kwargs)
        return Response({"Message":"Category Added"})
    
class CategoryView(generics.ListAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=CategoryViewSerializer
    authentication_classes=[JWTAuthentication]
    queryset=Category.objects.all()

class CategoryEdit(generics.RetrieveUpdateAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=CategoryViewSerializer
    authentication_classes=[JWTAuthentication]
    queryset=Category.objects.all()
    
       
class AdminProductAdd(generics.CreateAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=ProductAddSerialzer
    authentication_classes=[JWTAuthentication]

    def post(self, request, *args, **kwargs):
        response= super().post(request, *args, **kwargs)
        return Response({"Message":"Product Added"})

class AdminProductEdit(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=ProductAddSerialzer
    authentication_classes=[JWTAuthentication]
    queryset=Product.objects.all()

    def delete(self, request, *args, **kwargs):
        response= super().delete(request, *args, **kwargs)
        return Response({"Message":"PRODUCT REMOVED FROM THE SITE"})

class AdminProductView(generics.ListAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=ProductListSerializer
    authentication_classes=[JWTAuthentication]
    queryset=Product.objects.all()
    pagination_class=customPagination
    filter_backends=[filters.DjangoFilterBackend]
    filterset_fields={'categories__category_name': ['exact', 'icontains'],'price':['exact']}

    def get_queryset(self):
     queryset= super().get_queryset()
     
     min_price=self.request.query_params.get('min_price')
     if min_price:
        queryset=queryset.filter(price__gte=min_price)
     max_price=self.request.query_params.get('max_price')
     if max_price:
        queryset=queryset.filter(price__lte=max_price)
     return queryset
 


class AdminProductRetrieve(generics.RetrieveAPIView):
   permission_classes=[IsAuthenticated,IsAdminUser]
   authentication_classes=[JWTAuthentication]
   serializer_class=ProductDetailSerializer
   queryset=Product.objects.all()


class UserListView(generics.ListAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=UserManageSerializer
    authentication_classes=[JWTAuthentication]
    queryset=CustomUser.objects.all()


class AdminOrderView(generics.ListAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=AdminOrderSerializer
    authentication_classes=[JWTAuthentication]
    queryset=Order.objects.all().order_by('-date_of_order')
    pagination_class=customPagination

    
class UserRetrieve(generics.RetrieveAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=UserManageSerializer
    authentication_classes=[JWTAuthentication]
    queryset=CustomUser.objects.all()

class UserDeactivate(generics.UpdateAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    serializer_class=UserDeactivateSerializer
    authentication_classes=[JWTAuthentication]
    queryset=CustomUser.objects.all()


class UserDelete(generics.DestroyAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    queryset=CustomUser.objects.all()

    def delete(self, request, *args, **kwargs):
        response= super().delete(request, *args, **kwargs)
        return Response({"MESSAGE":"User Account  Deleted"})

class EmailSendingError(APIException):
    status_code = 500
    default_detail = 'Error sending email.'

class OrderStatusEdit(generics.UpdateAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    queryset=Order.objects.all()
    serializer_class=EditOrderStatusSerializer

    def patch(self, request, *args, **kwargs):
        order_obj = self.get_object()
        serializer = self.get_serializer(order_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        order_obj=serializer.save()
        try:
            if 'status' in serializer.validated_data:
                updated_status = serializer.validated_data['status']
                subject=f"ORDER STATUS UPDATE OF ORDER #{order_obj.id}"
                context = {'order': order_obj, 'updated_status': updated_status}
                html_message = render_to_string('order_status.html', context)
                text_message = strip_tags(html_message)
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [order_obj.user.email]
                send_mail(subject, text_message, from_email, recipient_list, html_message=html_message)
        except Exception as e:
            return Response({
                "Error": "Failed to send email.",
                "Recipient": recipient_list,
                "Content": subject
            }, status=500)

        return Response({"Message":"Status Updated"})
    

class PromotionalEmailView(generics.CreateAPIView):
    permission_classes=[IsAdminUser,IsAuthenticated]
    authentication_classes=[JWTAuthentication]
    queryset=PromotionalEmail.objects.all()
    serializer_class=PromotionalEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subject = serializer.validated_data['subject']
        content = serializer.validated_data['content']
        sender_email = settings.DEFAULT_FROM_EMAIL

        recipients=CustomUser.objects.filter(is_superuser=False).values_list('email',flat=True)
        html_message = render_to_string('promo_email.html', {'content': content})
        plain_message = strip_tags(html_message)
        error_response = {
                    "detail": "Error sending promotional emails.",
                    "subject": subject,
                    "content": content,
                    "recipients": recipients,
                    }
        for recipient_email in recipients:
            try:
                send_mail(subject, plain_message, sender_email, [recipient_email],html_message=html_message, fail_silently=False)
            except Exception as e:
                error_response["error_message"] = str(e)   
                raise EmailSendingError(detail=error_response)

        return Response({"MESSAGE":"PROMO EMAILS SENT"})
    


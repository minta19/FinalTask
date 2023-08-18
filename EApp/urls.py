from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,TokenVerifyView
)
from .views import (Signup,ProductList,UserPasswordResetView,UserPasswordResetConfirmView,ProductRetrieve,AddItemToCart,
                    CartItemsListView,CartItemRetrieve,CartItemUpdate,CartItemDelete,OrderPlacement,OrderHistoryView)
urlpatterns=[
    path('login/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/token/refresh',TokenRefreshView.as_view(),name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('signup/',Signup.as_view(),name='user_signup'),
    path('products/',ProductList.as_view(),name='list_of_products'),
    path('password/reset/',UserPasswordResetView.as_view(),name='password_reset'),
    path('password/reset/confirm/',UserPasswordResetConfirmView.as_view(),name='reset_confirm'),
    path('retrieve/<int:pk>/',ProductRetrieve.as_view(),name='product_detail_view'),
    path('tocart/',AddItemToCart.as_view(),name='to_cart'),
    path('Incart/',CartItemsListView.as_view(),name='in_cart'),
    path('detail-cart/',CartItemRetrieve.as_view(),name='cart_detail'),
    path('count_update/<int:pk>/',CartItemUpdate.as_view(),name='cart_update'),
    path('cart/item/delete/<int:pk>/',CartItemDelete.as_view(),name='cart_item_delete'),
    path('order/place/',OrderPlacement.as_view(),name='order_place'),
    path('order/history/',OrderHistoryView.as_view(),name='order_history'),



    
]
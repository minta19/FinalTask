from django.urls import path
from .views import (AdminLogin,AdminCategoryAdd,AdminProductAdd,AdminProductView,CategoryView,CategoryEdit,AdminProductEdit,UserListView,
                    UserDeactivate,UserRetrieve,UserDelete,AdminOrderView,OrderStatusEdit,PromotionalEmailView,AdminProductRetrieve)

urlpatterns=[
    path('login/',AdminLogin.as_view(),name='admin_login'),
    path('category/',AdminCategoryAdd.as_view(),name='category_add'),
    path('categories/',CategoryView.as_view(),name='category_view'),
    path('categoryedit/<int:pk>/',CategoryEdit.as_view(),name='category_edit'),
    path('products/',AdminProductView.as_view(),name='product_admin_view'),
    path('Add/',AdminProductAdd.as_view(),name='product_add'),
    path('product/detail/<int:pk>/',AdminProductRetrieve.as_view(),name='product_detail'),
    path('edit/<int:pk>',AdminProductEdit.as_view(),name='product_edit'),
    path('User/',UserListView.as_view(),name='user_list'),
    path('Acc/retrieve/<int:pk>',UserRetrieve.as_view(),name='user_retrieve'),
    path('Acc/Deactivate/<int:pk>',UserDeactivate.as_view(),name='user_deactivate'),
    path('Acc/remove/<int:pk>',UserDelete.as_view(),name='User_delete'),
    path('order/',AdminOrderView.as_view(),name='order'),
    path('order/status/<int:pk>/',OrderStatusEdit.as_view(),name='order_status'),
    path('promo/emails/',PromotionalEmailView.as_view(),name='promo_emails')


]

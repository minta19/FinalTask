from django.contrib import admin

from .models import CustomUser,Category,Product,Order,ItemsInCart,OrderedItem

admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(ItemsInCart)
admin.site.register(OrderedItem)
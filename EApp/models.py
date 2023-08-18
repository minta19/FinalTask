from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email=models.EmailField(unique=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
     

    def __str__(self) -> str:
        return self.username
    
class Category(models.Model):
    category_name=models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.category_name
    
class Product(models.Model):
    product_name=models.CharField(max_length=255)
    description=models.TextField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    quantity=models.PositiveIntegerField()
    product_image=models.ImageField(upload_to='images/')
    categories=models.ManyToManyField(Category)

    def __str__(self) -> str:
        return self.product_name
    
class Order(models.Model):
    status_choices=(
        ('Processing','Processing'),
        ('Shipped','Shipped'),
        ('Delivered','Delievered')
    )
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='ordered_user')
    ordered_product=models.ManyToManyField(Product)
    total_amount=models.DecimalField(max_digits=10,decimal_places=2)
    date_of_order=models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=status_choices)
    Address=models.TextField(default="")
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class ItemsInCart(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_items')
    Number_of_items=models.PositiveIntegerField(default=1)
    order=models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,blank=True,related_name='cart_items')
    def __str__(self):
        return f"{self.user.username}'s Cart Item: {self.product.product_name}"
    
class OrderedItem(models.Model):
    order_ref = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='ordered_items')
    item_ordered = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_quantity = models.PositiveIntegerField()
    ordered_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.order_ref.id} - {self.item_ordered.product_name}"
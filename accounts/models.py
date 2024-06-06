from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from product.models import Product,Coupon,ColorVarient
from django.core.validators import MaxValueValidator, MinValueValidator
from base.models import BaseModel
# Create your models here.

class User(AbstractUser):
    username = None
    first_name = None
    last_name= None
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=12,unique=True)
    is_phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6,null=True)
    otp_time = models.DateTimeField(blank=True,null=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']
    objects = UserManager()


class Address(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="address")
    name = models.CharField(max_length=200)
    addressline = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    state = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)
    email = models.EmailField(max_length=200)



class BillAddress(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="billaddress")
    name = models.CharField(max_length=200)
    addressline = models.CharField(max_length=200)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    zipcode = models.IntegerField()
    state = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)
    email = models.EmailField(max_length=200)

STATUS_CHOICES = (
    ('Pending','Pending'),
    ('Accepted','Accepted'),
    ('Packed','Packed'),
    ('On The Way','On The Way'),
    ('Delivered','Delivered'),
    ('Cancel','Cancel')
)



class OrderPlaced(BaseModel):
    invoice_no = models.CharField(max_length=40)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL,null=True)
    bill_address = models.ForeignKey(BillAddress, on_delete=models.SET_NULL,null=True)
    ordered_date = models.DateTimeField(auto_now_add=True)
    merchantTransactionId = models.CharField(max_length=200)
    transactionId = models.CharField(max_length=200)
    paid_amount = models.CharField(max_length=200)
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')


class PursedProduct(BaseModel):
    order = models.ForeignKey(OrderPlaced, on_delete=models.SET_NULL,null=True,related_name='orderplaced')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,null=True)
    color_varient = models.ForeignKey(ColorVarient, on_delete=models.SET_NULL,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1)
    ordered_date = models.DateTimeField(auto_now_add=True)
    paid_amount = models.CharField(max_length=200)



class ShipToken(models.Model):
    token = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

 
class Subscribe(BaseModel):
    email = models.EmailField()


class ProductReview(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,null=True,blank=True,related_name="product_reviews")
    rating = models.SmallIntegerField( default=0,validators=[MaxValueValidator(5),MinValueValidator(1)])
    comment = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)


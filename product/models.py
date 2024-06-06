from django.db import models
from base.models import BaseModel
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg
# Create your models here.


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True,blank=True)
    is_publish = models.BooleanField(default=True)
    category_image = models.ImageField(upload_to='categories')

    def save(self,*arg,**kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*arg,**kwargs)

    def __str__(self):
        return self.category_name



class SubCategory(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,null=True,blank=True,related_name="sub_category")
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,null=True,blank=True)
    is_publish = models.BooleanField(default=True)
    category_image = models.ImageField(upload_to='categories')

    def save(self,*arg,**kwargs):
        self.slug = slugify(self.category_name)
        super(SubCategory, self).save(*arg,**kwargs)

    def __str__(self):
        return self.category_name


class Brands(BaseModel):
    brands_name = models.CharField(max_length=100)
    is_publish = models.BooleanField(default=True)
    slug = models.SlugField(unique=True,null=True,blank=True)
    brands_image = models.ImageField(upload_to='categories')

    def save(self,*arg,**kwargs):
        self.slug = slugify(self.brands_name)
        super(Brands, self).save(*arg,**kwargs)

    def __str__(self):
        return self.brands_name


class ColorVarient(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.color_name

class SizeVarient(BaseModel):
    size_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.size_name


class Product(BaseModel):
    product_name = models.CharField(max_length=200)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL,null=True,blank=True,related_name="products")
    brands = models.ForeignKey(Brands, on_delete=models.SET_NULL,null=True,blank=True,related_name="productbrand")
    mrp_price = models.IntegerField()
    dis_price = models.IntegerField()
    product_description = RichTextField()
    length = models.IntegerField()
    breadth = models.IntegerField()
    height = models.IntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    is_publish = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True,null=True,blank=True)
    color_varient = models.ManyToManyField(ColorVarient ,blank=True)
    size_varient = models.ManyToManyField(SizeVarient ,blank=True)
    # fake_review = models.IntegerField(null=True,blank=True)
    # fake_rating = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)

    def save(self,*arg,**kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*arg,**kwargs)

    def __str__(self):
        return self.product_name

    
    def get_product_price_by_size(self,size):
        return self.price + SizeVarient.objects.get(size_name=size).price

    def total_reviews(self):
        return self.product_reviews.all().count()
        

    @property
    def average_rating(self):
        return self.product_reviews.aggregate(Avg('rating'))['rating__avg']
    
    

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name="product_images")
    image = models.ImageField(upload_to="product")

    def __str__(self):
        return self.product.product_name


class BestSaler(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='best_sale_products')
    
    def __str__(self):
        return self.product.product_name



class HotSaler(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='hot_sale_products')
    
    def __str__(self):
        return self.product.product_name




class Onsale(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='on_sale_products')
    sale_discount_price = models.FloatField()

    def __str__(self):
        return self.product.product_name


class DealOfTheDay(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='dealoftheday')
    sale_discount_price = models.FloatField()
    offer_date = models.DateTimeField()

    def __str__(self):
        return self.product.product_name


class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=100)
    minimun_amount = models.IntegerField(default=500)




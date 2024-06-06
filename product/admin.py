from django.contrib import admin
from . models import *
# Register your models here.
admin.site.register(Category)
admin.site.register(Onsale)
admin.site.register(Coupon)
admin.site.register(DealOfTheDay)

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name','dis_price']
    inlines = [ProductImageAdmin]

@admin.register(ColorVarient)
class ColorVarientAdmin(admin.ModelAdmin):
    list_display = ['color_name','price']
    model = ColorVarient

@admin.register(SizeVarient)
class SizeVarientAdmin(admin.ModelAdmin):
    list_display = ['size_name','price']
    model = SizeVarient

admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Brands)
admin.site.register(BestSaler)
admin.site.register(HotSaler)
admin.site.register(SubCategory)
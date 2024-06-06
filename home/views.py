from django.shortcuts import render,redirect
from product.models import Product,BestSaler,HotSaler,DealOfTheDay,SubCategory,Brands
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from blog.models  import Blogpost
from . models import Contact
from django.contrib import messages
from accounts.views import genshiptoken
from accounts.models import ShipToken
import datetime
from django.utils import timezone
import requests
import json
from django.core.serializers.json import DjangoJSONEncoder
# Create your views here.


def home(request):
    # tokendate = ShipToken.objects.get(id=1).date
    # currentdate = datetime.datetime.now().date()
    # diff = timezone.now() -tokendate
    # if diff.days > 9:
    #     rurl = "https://apiv2.shiprocket.in/v1/external/auth/login"
    #     headers =  {"Content-Type":"application/json"}
    #     data ={
    #             "email":"ghostingtech@gmail.com" ,
    #             "password": "Ghosting@108",
    #         }
    #     response =requests.post(rurl,data=json.dumps(data, cls=DjangoJSONEncoder), headers=headers)
    #     print(response.json())
    #     print(response.json()['token'])
        
    #     ship =ShipToken(
    #         token = response.json()['token'],
    #         id= 1,
    #         date = timezone.now()
    #     )
    #     ship.save()
    product = Product.objects.filter(is_publish=True)
    bestsaler = BestSaler.objects.all()
    hotsaler = HotSaler.objects.all()
    blog = Blogpost.objects.all()[:5]
    brands = Brands.objects.filter(is_publish=True)
    dealoftheday = DealOfTheDay.objects.filter().first()
    context={'product':product,'bestsaler':bestsaler,'hotsaler':hotsaler,'dealoftheday':dealoftheday,'blog':blog,'brands':brands}
    return render(request, 'index.html',context)


def shop(request):
    category = request.GET.get('category')
    subcategory = request.GET.get('subcategory')
    brands = request.GET.get('brand')
    price = request.GET.get('price')
    filter_price1 = request.GET.get('min_price')
    filter_price2 = request.GET.get('max_price')
    order = request.GET.get('order')
    print(order)
    if filter_price1 =='':
        filter_price1=0
    if filter_price2:
        product=Product.objects.filter(dis_price__range=(int(filter_price1),int(filter_price2))).filter(is_publish=True)
    elif category:
        product = Product.objects.filter(sub_category__category__category_name=category).filter(is_publish=True)
    elif subcategory:
        product = Product.objects.filter(sub_category__category_name=subcategory).filter(is_publish=True)
    elif brands:
        product = Product.objects.filter(brands__brands_name=brands).filter(is_publish=True)
    elif order:
        if order == "htol":
            product = Product.objects.filter(is_publish=True).order_by('-dis_price')
        elif order == "ltoh":
            product = Product.objects.filter(is_publish=True).order_by('dis_price')
        elif order == "newness":
            product = Product.objects.filter(is_publish=True).order_by('-created_at')
        else:
            product = Product.objects.filter(is_publish=True)
    else:
        product = Product.objects.filter(is_publish=True)
    allbrands = Brands.objects.filter(is_publish=True)
    hotsaler =HotSaler.objects.all()
    context = {'product':product,'hotsaler':hotsaler,'allbrands':allbrands}
    return render(request,'shop.html',context)


def product_detail(request,slug):
    print(slug)
    product = Product.objects.get(slug=slug)
    similar_product = Product.objects.filter(sub_category=product.sub_category).filter(is_publish=True)
    context = {'product':product,'similar_product':similar_product}
    return render(request,'product-details.html',context)



def add_to_cart(request):
    uid = request.GET.get('uid')
    quantity = request.GET.get('quantity')
    product = Product.objects.get(uid=uid)
    cart = request.session.get('cart')  
    if cart:
        desc = cart.get(uid)
        if desc:
            print('product in cart')
            cart[uid] = quantity
        else:
            print('product not in cart')
            cart[uid] = quantity
    else:
        cart ={}  
        cart[uid]=quantity
    request.session['cart']=cart
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_to_wishlist(request,uid):
    product = Product.objects.get(uid=uid)
    (product)
    wishlist_desc = ""
    wishlist = request.session.get('wishlist')  
    if wishlist:
        desc = wishlist.get(uid)
        if desc:
            wishlist[desc]: wishlist_desc
        else:
            wishlist[uid] = wishlist_desc
    else:
        wishlist ={}  
        wishlist[uid]=wishlist_desc
    request.session['wishlist']=wishlist
    # return redirect('shop')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def buynow(request,uid):
    product = Product.objects.get(uid=uid)
    (product)
    quantity = 1
    cart = request.session.get('cart')  
    if cart:
        desc = cart.get(uid)
        if desc:
            cart[desc]: quantity
        else:
            cart[uid] = quantity
    else:
        cart ={}  
        cart[uid]=quantity
    request.session['cart']=cart
    return redirect('shopping_cart')



def shopping_cart(request): 
    return render(request,'shopping-cart.html')


def deletesessioncart(request,uid):
    cart = request.session['cart']
    del cart[str(uid)]
    request.session["cart"] = cart
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def deletesessionwishlist(request,uid):
    wishlist = request.session['wishlist']
    del wishlist[str(uid)]
    request.session["wishlist"] = wishlist
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def wishlist(request):
    return render(request,'wishlist.html')


def about(request):
    return render(request,'about-us.html')


def contact(request):
    if request.method =='POST':
        name = request.POST['name']
        email = request.POST['email']
        desc = request.POST['message']
        # mobile = request.POST['mobile']
        contact = Contact(name=name,email=email,desc=desc)
        contact.save()
        messages.success(request,"you message is sended successfully")
    return render(request,'contact-us.html')


def privacy(request):
    return render(request,'privacy.html')


def refunds(request):
    return render(request,'refunds.html')


def shipping_policy(request):
    return render(request,'shipping-policy.html')


def terms(request):
    return render(request,'terms.html')


def search(request):
    category = request.GET.get('s')
    query = request.GET.get('q')
    if category:
        product = Product.objects.filter(product_name__icontains=query,category__category_name=query)
    else:
        product = Product.objects.filter(product_name__icontains=query)
    context = {'product':product}
    return render(request,'search.html',context)


def get_search(request):
    category = request.GET.get('s')
    query = request.GET.get('q')
    payload =[]
    if category:
        product = Product.objects.filter(product_name__icontains=query,category__category_name=category)
    else:
        product = Product.objects.filter(product_name__icontains=query)
    print(product)
    for obj in product:
        payload.append({
            "name": obj.product_name,
            "slug":obj.slug
        })
    print('response')
    return JsonResponse({
        "status":200,
        "payload":payload
    })


def error_404_view(request, exception):
    return render(request, '404.html')
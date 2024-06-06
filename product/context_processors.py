from .models import Category,Product
from home.models import Contact

def company(request):
    return{
        "company_logo":"/static/assets/images/logo/logoGems.webp",
        "company_name":"Gautam Gems",
        "company_desc":"""Gautam Gems: Where Handcrafted Elegance Resides.
                        Discover Unique Pieces from Global Artisans.
                        Your Home, Our Craftsmanship. Elevate Your Space with Timeless Beauty.""",
        "address":"Ashok Nagar Road no 14 Kankarbagh",
        "mobile":"1234567890",
        "email":"gems@stone.com",
        "developer_website":"https://ghosting.in/",
        "developer_name":"Ghosting Tech",
        "developer_logo":"/static/assets/images/GHOSTING.png"
    }
  


def categories_context(request):
    categories = Category.objects.filter(is_publish=True)
    return {'categories':categories}



def contact_context(request):
    contact_message = Contact.objects.all()
    return {'contact_message':contact_message}


def product_in_cart(request):
    cart = request.session.get('cart') 
    product = []
    totalamount = 0
    if cart:
        for k in cart:
            try:
                queryset =Product.objects.get(uid=k)
                queryset.quantity = cart[k]
                if queryset.quantity:
                    totalamount = totalamount + (queryset.dis_price*int(queryset.quantity))
                else:
                    pass
                product.append(queryset)  
            except Product.DoesNotExist:
                pass
    return {'product_in_cart':product,'totalamount':totalamount,'cart_count':len(product)}



def product_in_wishlist(request):
    wishlist = request.session.get('wishlist') 
    product = []
    totalamount = 0
    if wishlist:
        for k in wishlist:
            queryset =Product.objects.get(uid=k)
            queryset.wishlist_desc = wishlist[k]
            totalamount = totalamount + queryset.dis_price
            product.append(queryset)  
    return {'product_in_wishlist':product,'wishlist_count':len(product)}



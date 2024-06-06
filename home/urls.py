from django.urls import path
from .import views

urlpatterns=[ 
    path('',views.home,name='home'),
    path('shop',views.shop,name='shop'),
    path('product-detail/<slug>',views.product_detail,name='product_detail'),
    path('add-to-cart',views.add_to_cart,name='add_to_cart'),
    path('wishlist',views.wishlist,name='wishlist'),
    path('add-to-wishlist/<uid>',views.add_to_wishlist,name='add_to_wishlist'),
    path('deletesessioncart/<uid>',views.deletesessioncart,name='deletesessioncart'),
    path('deletesessionwishlist/<uid>',views.deletesessionwishlist,name='deletesessionwishlist'),
    path('buynow/<uid>',views.buynow,name='buynow'),
    path('shopping-cart',views.shopping_cart,name='shopping_cart'),
    path('about',views.about,name='about'),
    path('contact',views.contact,name='contact'),
    path('privacy',views.privacy,name='privacy'),
    path('refunds',views.refunds,name='refunds'),
    path('shipping-policy',views.shipping_policy,name='shipping_policy'),
    path('terms',views.terms,name='terms'),
    path('search',views.search,name='search'),
    path('get-search',views.get_search),
]
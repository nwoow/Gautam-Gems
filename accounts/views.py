from django.shortcuts import render,redirect
from . models import *
from . helpers import send_otp_to_phone
from home.models import Contact
from product.models import Coupon,Product,SubCategory,Brands,Category,ProductImage,BestSaler,HotSaler,DealOfTheDay
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib import messages
import requests
import base64
import json
import hashlib
import datetime
import random
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from django.core.serializers.json import DjangoJSONEncoder
from threading import Timer
from num2words import num2words
from django.utils import timezone
from datetime import timedelta
# Create your views here.



def genshiptoken(request):
    rurl = "https://apiv2.shiprocket.in/v1/external/auth/login"
    headers =  {"Content-Type":"application/json"}
    data ={
            "email":"ghostingtech@gmail.com" ,
            "password": "Ghosting@108",
        }
    response =requests.post(rurl,data=json.dumps(data, cls=DjangoJSONEncoder), headers=headers)
    print(response.json())
    print(response.json()['token'])
    
    ship =ShipToken(
        token = response.json()['token'],
        id= 1,
        date = timezone.now()
    )
    ship.save()


# def testshiprocket(request):
#     shipping_url = config('SHIP_URL')
#     shiptoken = ShipToken.objects.get(id=1)
#     headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {shiptoken.token}"}
#     data ={
#             "order_id": "11111",
#             "order_date": "2024-09-09 11:11",
#             "pickup_location": "Primary",
#             "channel_id": "",
#             "comment": "Decorline",
#             "billing_customer_name": "Naruto",
#             "billing_last_name": "Uzumaki",
#             "billing_address": "House 221B, Leaf Village",
#             "billing_address_2": "Near Hokage House",
#             "billing_city": "New Delhi",
#             "billing_pincode": "110002",
#             "billing_state": "Delhi",
#             "billing_country": "India",
#             "billing_email": "naruto@uzumaki.com",
#             "billing_phone": "7903465074",
#             "shipping_is_billing": True,
#             "shipping_customer_name": "",
#             "shipping_last_name": "",
#             "shipping_address": "",
#             "shipping_address_2": "",
#             "shipping_city": "",
#             "shipping_pincode": "",
#             "shipping_country": "India",
#             "shipping_state": "",
#             "shipping_email": "",
#             "shipping_phone": "",
#             "order_items": [
#                 {
#                     "name": "This is product title",
#                     "sku": "chakra123",
#                     "units": 1,
#                     "selling_price": 100,
#                     "discount": "",
#                     "tax": "",
#                     "hsn": 44
#                 }
#                 ],
#             "payment_method": "Prepaid",
#             "shipping_charges": 0,
#             "giftwrap_charges": 0,
#             "transaction_charges": 0,
#             "total_discount": 0,
#             "sub_total": 100,
#             "length": 10,
#             "breadth": 15,
#             "height": 20,
#             "weight": 2.5
#             }
#     response =requests.post(shipping_url,data=json.dumps(data, cls=DjangoJSONEncoder), headers=headers)
#     print(response.text)


def userlogin(request):
    if request.method == 'POST':
        phone_number = request.POST.get('mobile')  
        try:
            user_obj = User.objects.get(phone_number=phone_number) 
            user_obj.otp =send_otp_to_phone(phone_number)
            user_obj.otp_time = timezone.now()
            user_obj.save()
            return redirect('otpverify',phone_number)
        except User.DoesNotExist:
            messages.error(request, "Please check mobile no")
            return HttpResponseRedirect(request.path_info)
    return render(request, 'login.html')


def otpverify(request,mobile):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        try:
            user_obj = User.objects.get(phone_number=mobile)
        except Exception as e:
            messages.error(request, "Please check mobile no")
            context = {'mobile':mobile}
            return render(request, 'otpverify.html',context)
        if user_obj.otp == otp:
            time_diff = timezone.now() - user_obj.otp_time
            delta = timedelta(hours=0, minutes=10, seconds=0)
            if time_diff >= delta:
                messages.error(request, "Otp expired")
                return HttpResponseRedirect(request.path_info)  
            login(request, user_obj)  
            return redirect('/')  
        else:
            messages.error(request, "Invalid OTP")
            return HttpResponseRedirect(request.path_info)              
    context = {'mobile':mobile}
    return render(request, 'otpverify.html',context)


def adminlogin(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        user_obj = User.objects.filter(phone_number=mobile)
        if not user_obj.exists():
            messages.error(request, "Account not found/exits")
            return HttpResponseRedirect(request.path_info)
        user_obj = authenticate(phone_number=mobile,password=password)
        if user_obj:
            login(request, user_obj)
            messages.success(request, "login successfully")
            if user_obj.is_staff == True:
                return redirect('dashboard')
            return redirect('/')
        messages.error(request, "Invalid Creadationls")
        return HttpResponseRedirect(request.path_info)
    return render(request,'adminpannel/adminlogin.html')



def shipping(invoice_nos):
    shipping_url = config('SHIP_URL')
    shiptoken = ShipToken.objects.get(id=1)
    print(shiptoken.token)
    headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {shiptoken.token}"}
    carts = OrderPlaced.objects.get(invoice_no=invoice_nos)
    i=1
    for cart_item in carts.orderplaced.all():
        print(cart_item)
        data ={
            "order_id": carts.invoice_no+str(1),
            "order_date": carts.ordered_date.strftime("%Y-%m-%d %H:%M"),
            "pickup_location": "Primary",
            "channel_id": "",
            "comment": "Decorline",
            "billing_customer_name": carts.user.full_name,
            "billing_last_name": "",
            "billing_address": carts.bill_address.addressline,
            "billing_address_2": carts.bill_address.locality,
            "billing_city": carts.bill_address.city,
            "billing_pincode": carts.bill_address.zipcode,
            "billing_state": carts.bill_address.state,
            "billing_country": "India",
            "billing_email": carts.bill_address.email,
            "billing_phone": carts.bill_address.phone,
            "shipping_is_billing": False,
            "shipping_customer_name": carts.user.full_name,
            "shipping_last_name": "",
            "shipping_address": carts.address.addressline,
            "shipping_address_2": carts.address.locality,
            "shipping_city": carts.address.city,
            "shipping_pincode": carts.address.zipcode,
            "shipping_country": "India",
            "shipping_state": carts.address.state,
            "shipping_email": carts.address.email,
            "shipping_phone": carts.address.phone,
            "order_items": [
                {
                    "name": cart_item.product.product_name,
                    "sku": "chakra123",
                    "units": cart_item.quantity,
                    "selling_price": cart_item.product.dis_price,
                    "discount": "",
                    "tax": "",
                    "hsn": 44
                }
                ],
            "payment_method": "Prepaid",
            "shipping_charges": 0,
            "giftwrap_charges": 0,
            "transaction_charges": 0,
            "total_discount": 0,
            "sub_total": cart_item.product.dis_price,
            "length": cart_item.product.length,
            "breadth": cart_item.product.breadth,
            "height": cart_item.product.height,
            "weight": cart_item.product.weight
            }
        i =i+1
        response =requests.post(shipping_url,data=json.dumps(data, cls=DjangoJSONEncoder), headers=headers)
        print(response.text)



def register(request):
    if request.method=='POST':
        full_name = request.POST['full_name']
        mobile = request.POST['mobile']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
        if password != cpassword:
            messages.error(request,'Password not matched')
            return redirect('register')
        user_obj = User.objects.filter(phone_number=mobile)
        if user_obj.exists():
            messages.error(request,'Mobile number already exits')
            return redirect('register')
        user_obj = User.objects.create(full_name=full_name,phone_number=mobile,password=password)
        user_obj.set_password(password)
        user_obj.save()
        user_obj = authenticate(phone_number=mobile,password=password)
        if user_obj:
            login(request, user_obj)
            messages.success(request, "login successfully")
            return redirect('/')
        messages.success(request, 'Registration successfully')
        return redirect('userlogin')
    return render(request,'register.html')


@login_required(login_url="userlogin")
def updateprofile(request):
    if request.method=='POST':
        full_name = request.POST.get('full_name')      
        email = request.POST.get('email')
        curpassword = request.POST.get('curpassword')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')        
        user_obj = request.user

        if full_name:
            user_obj.full_name = full_name
      
        if email:
            user_obj.email= email
        if password:
            if user.password:
                if user.password == curpassword:
                    user_obj.set_password(password)
            else:
                user_obj.set_password(password)
        user_obj.save()
        messages.success(request,'Account updated successfully')
        return redirect('account_info')



def userlogout(request):
    logout(request)
    return redirect('/')



def checkout(request):
    if request.method == "POST":
        name = request.POST['name']
        address = request.POST['address']
        locality = request.POST['locality']
        city = request.POST['city']
        zipcode = request.POST['zipcode']
        state = request.POST['state']
        phone = request.POST['mobile']
        email = request.POST['email']
        checkbox = request.POST.get('checkbox')
        billname = request.POST.get('billname')
        billadd = request.POST.get('billaddress')
        billlocality = request.POST.get('billlocality')
        billcity = request.POST.get('billcity')
        billzipcode = request.POST.get('billzipcode')
        billstate = request.POST.get('billstate')
        billphone = request.POST.get('billmobile')
        billemail = request.POST.get('billemail')
        print(checkbox,'check')
        user_obj = User.objects.filter(phone_number=phone)
        if user_obj.exists():
            messages.error(request,'already have account please login')
            if request.user.is_anonymous:
                return redirect('userlogin')
        else:    
            user_obj = User.objects.create(full_name=name,phone_number=phone)
            user_obj.save()
        print(request.user)
        if request.user.is_anonymous:
            if user_obj:
                login(request, user_obj)
                messages.success(request, "login successfully")
        if checkbox is None:
            try:
                shipaddress= Address.objects.get(user=request.user)
                shipaddress.name = name
                shipaddress.addressline = address
                shipaddress.locality = locality
                shipaddress.city = city
                shipaddress.zipcode = zipcode
                shipaddress.state = state
                shipaddress.phone= phone
                shipaddress.email =email
                shipaddress.save()
            except Address.DoesNotExist:
                shipaddress= Address(user=request.user,name=name,addressline=address,locality=locality,city=city,zipcode=zipcode,
                                 state=state,phone=phone,email=email) 
                shipaddress.save()
            try:
                billaddress = BillAddress.objects.get(user=request.user)
                billaddress.name = name
                billaddress.addressline = address
                billaddress.locality = locality
                billaddress.city = city
                billaddress.zipcode = zipcode
                billaddress.state = state
                billaddress.phone= phone
                billaddress.email =email
                billaddress.save()
            except BillAddress.DoesNotExist:
                billaddress = BillAddress(user=request.user,name=name,addressline=address,locality=locality,city=city,zipcode=zipcode,
                                    state=state,phone=phone,email=email)
                billaddress.save()     
        else:
            try:
                shipaddress = Address.objects.get(user=request.user)         
                shipaddress.name = name
                shipaddress.addressline = address
                shipaddress.locality = locality
                shipaddress.city = city
                shipaddress.zipcode = zipcode
                shipaddress.state = state
                shipaddress.phone= phone
                shipaddress.email =email
                shipaddress.save()
            except Address.DoesNotExist:
                shipaddress = Address(user=request.user,name=name,addressline=address,locality=locality,city=city,zipcode=zipcode,
                                 state=state,phone=phone,email=email)
                shipaddress.save()
            try:
                billaddress= BillAddress.objects.get(user=request.user)
                billaddress.name = billname
                billaddress.addressline = billadd
                billaddress.locality = billlocality
                billaddress.city = billcity
                billaddress.zipcode = billzipcode
                billaddress.state = billstate
                billaddress.phone= billphone
                billaddress.email =billemail
                billaddress.save()
            except BillAddress.DoesNotExist:
                billaddress= BillAddress(user=request.user,name=billname,addressline=billadd,locality=billlocality,city=billcity,zipcode=billzipcode,
                                    state=billstate,phone=billphone,email=billemail)
                billaddress.save()
        cart = request.session.get('cart') 
        product = []
        totalamount = 0
        if cart:
            for k in cart:
                queryset =Product.objects.get(uid=k)
                queryset.quantity = cart[k]
                if queryset.quantity:
                    totalamount = totalamount + (queryset.dis_price*int(queryset.quantity))
                else:
                    pass
                product.append(queryset) 
        print(totalamount)
        data = {
            "merchantId":config('MERCHANT_ID'),
            "merchantTransactionId": 'MT'+ phone + str(random.randint(10000, 99999)),
            "merchantUserId":'MU'+ phone,
            "amount": totalamount*100,
            "redirectUrl": "https://decorline.in/accounts/paymentresponse",
            "redirectMode": "POST",
            "callbackUrl": "https://decorline.in/accounts/paymentcallback",
            "mobileNumber": phone,
            "paymentInstrument": {
            "type": "PAY_PAGE"
            }
            }
        json_data = json.dumps(data)
        encoded_dict = json_data.encode('utf-8')
        encoded_data =base64.b64encode(encoded_dict)
        string = base64.b64encode(encoded_dict) + ("/pg/v1/pay" ).encode('utf-8') +(config('SALT_KEY')).encode('utf-8') 
        url = f"{config('PAYMENT_URL')}/pg/v1/pay"
        print(encoded_data.decode('utf-8'))
        payload = {"request":encoded_data.decode('utf-8')}
        sha_con =hashlib.sha256(string).hexdigest()
        xverify = (sha_con)+ '###' +'1'
        print(xverify)
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-VERIFY":xverify
        }
        response = requests.post(url,json=payload, headers=headers,)
        print(response)
        response =response.json()
        print(response)
        if response['success']== False:
            return HttpResponse('payment faild')
        paymenturl =response['data']['instrumentResponse']['redirectInfo']['url']
        merchantTransactionId = response['data']['merchantTransactionId']  
        orderplaced =   OrderPlaced(
            user=request.user,address=shipaddress,bill_address=billaddress,     
            status="Pending",merchantTransactionId=merchantTransactionId,
            paid_amount=totalamount,
            is_paid=False,
            )
        orderplaced.save()
        print(orderplaced)
        for p in product:
            payout = PursedProduct(
                order = orderplaced,
                product = p,quantity = p.quantity,      
                paid_amount=p.dis_price*int(p.quantity),
                )
            payout.save()
        return redirect(paymenturl)

    print(request.user)
    if request.user.is_anonymous:
        address = {}
        billaddress = {}   
    else:
        address = Address.objects.filter(user = request.user).first
        billaddress = BillAddress.objects.filter(user = request.user).first
    context = {'address':address,'billaddress':billaddress}
    return render(request,'checkout.html',context)



@csrf_exempt
def check_status(merchantTransactionIds):
    print('functions called')
    url = f"{config('PAYMENT_URL')}/pg/v1/status/{config('MERCHANT_ID')}/{merchantTransactionIds}"
    string = f"/pg/v1/status/{config('MERCHANT_ID')}/{merchantTransactionIds}{config('SALT_KEY')}"
    enc = string.encode('utf-8')
    sha_con =hashlib.sha256(enc).hexdigest()
    xverify = (sha_con)+ '###' +'1'
    print(xverify)
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "X-VERIFY": xverify,
        "X-MERCHANT-ID": config('MERCHANT_ID')
    }
    response = requests.get(url, headers=headers)
    response =response.json()
    mydata =response['data']
    if mydata['code'] == "PAYMENT_SUCCESS":
        print("payment succes")     
        try:
            cart = OrderPlaced.objects.get(merchantTransactionId=mydata['data']['merchantTransactionId'],is_paid=False)
        except Cart.DoesNotExist:
            pass
        total_cart = OrderPlaced.objects.filter(is_paid=True).count()
        # if cart.coupon:
        #     coupon = Coupon.objects.get(coupon_code=cart.coupon.coupon_code)
        #     coupon.is_expired = True
        #     coupon.save()
        invoice = '0000' + str(total_cart + 1)
        lent = len(invoice)
        invoice_nos = "ODN" + invoice[lent-4:]
        cart.invoice_no = invoice_nos
        cart.transactionId = mydata['data']['transactionId']
        cart.paid_amount = int(mydata['data']['amount'])/100
        cart.ordered_date = datetime.datetime.now()
        cart.is_paid = True 
        cart.save()   
        shipping(invoice_nos)
        del request.session['cart']
        return HttpResponse("payment success")
        


@csrf_exempt
def paymentcallback(request):
    received_json_data=json.loads(request.body)
    print(received_json_data)
    decoded_data = base64.b64decode(received_json_data['response'])
    print(decoded_data)
    mydata = json.loads(decoded_data)
    print(mydata['success'])
    merchantTransactionIds = mydata['data']['merchantTransactionId']
    transactionIds = mydata['data']['transactionId']
    if mydata['code'] == "PAYMENT_SUCCESS":
        print("payment succes")     
        try:
            cart = OrderPlaced.objects.get(merchantTransactionId=merchantTransactionIds,is_paid=False)
        except Cart.DoesNotExist:
            pass
        total_cart = OrderPlaced.objects.filter(is_paid=True).count()
        # if cart.coupon:
        #     coupon = Coupon.objects.get(coupon_code=cart.coupon.coupon_code)
        #     coupon.is_expired = True
        #     coupon.save()
        invoice = '0000' + str(total_cart + 1)
        lent = len(invoice)
        invoice_nos = "ORN" + invoice[lent-4:]
        cart.invoice_no = invoice_nos
        cart.transactionId = transactionIds
        cart.paid_amount = int(mydata['data']['amount'])/100
        cart.ordered_date = datetime.datetime.now()
        cart.is_paid = True 
        cart.save()             
        shipping(invoice_nos)
        del request.session['cart']
        return HttpResponse("payment success")
    elif mydata['code'] == "PAYMENT_PENDING":
        t = Timer(25.0, check_status,[merchantTransactionIds])
        t.start()
    else:
        return HttpResponse("payment Fail")



@csrf_exempt
def paymentresponse(request):
    return render(request,'thankyou.html')


@login_required(login_url="userlogin")
def myaccount(request): 
    return render(request,'accounts/my-account.html')


@login_required(login_url="userlogin")
def orderdet(request):
    order = OrderPlaced.objects.filter(user=request.user,is_paid=True)
    context = {'order':order}
    return render(request,'accounts/order.html',context)


def download(request):
    return render(request,'accounts/download.html')


def address(request):
    address = Address.objects.filter(user = request.user).first
    billaddress = BillAddress.objects.filter(user = request.user).first
    context = {'address':address,'billaddress':billaddress}
    return render(request,'accounts/address.html',context)


@login_required(login_url="userlogin")
def addaddress(request):
    if request.method == "POST":
        name = request.POST['name']
        address = request.POST['address']
        locality = request.POST['locality']
        city = request.POST['city']
        zipcode = request.POST['zipcode']
        state = request.POST['state']
        phone = request.POST['mobile']
        email = request.POST['email']
        shipaddress = Address(user=request.user,name=name,addressline=address,locality=locality,city=city,zipcode=zipcode,
                                 state=state,phone=phone,email=email)
        shipaddress.save()
        return redirect('address')
    return render(request,'accounts/addaddress.html')


@login_required(login_url="userlogin")
def addbilladdress(request):
    if request.method == "POST":
        name = request.POST['name']
        address = request.POST['address']
        locality = request.POST['locality']
        city = request.POST['city']
        zipcode = request.POST['zipcode']
        state = request.POST['state']
        phone = request.POST['mobile']
        email = request.POST['email']
        billaddress = BillAddress(user=request.user,name=name,addressline=address,locality=locality,city=city,zipcode=zipcode,
                                 state=state,phone=phone,email=email)
        billaddress.save()
        return redirect('address')
    
    return render(request,'accounts/addbilladdress.html')



@login_required(login_url="userlogin")
def editaddress(request,uid):
    if request.method == "POST":
        name = request.POST['name']
        saddress = request.POST['address']
        locality = request.POST['locality']
        city = request.POST['city']
        zipcode = request.POST['zipcode']
        state = request.POST['state']
        phone = request.POST['mobile']
        email = request.POST['email']

        address = Address.objects.get(uid=uid)

        address.name = name
        address.addressline = saddress
        address.locality = locality
        address.city = city
        address.zipcode = zipcode
        address.state = state
        address.phone= phone
        address.email =email
        address.save()
   
    address = Address.objects.get(uid=uid)
    context = {'address':address}
    return render(request,'accounts/editaddress.html',context)


@login_required(login_url="userlogin")
def editbilladdress(request,uid):
    if request.method == "POST":
        name = request.POST['name']
        address = request.POST['address']
        locality = request.POST['locality']
        city = request.POST['city']
        zipcode = request.POST['zipcode']
        state = request.POST['state']
        phone = request.POST['mobile']
        email = request.POST['email']

        billaddress = BillAddress.objects.get(uid=uid)

        billaddress.name = name
        billaddress.addressline = address
        billaddress.locality = locality
        billaddress.city = city
        billaddress.zipcode = zipcode
        billaddress.state = state
        billaddress.phone= phone
        billaddress.email =email
        billaddress.save()
   
    billaddress = BillAddress.objects.get(uid=uid)
    context = {'billaddress':billaddress}
    return render(request,'accounts/editbilladdress.html',context)


@login_required(login_url="userlogin")
def account_info(request):
    return render(request,'accounts/account-info.html')



@login_required(login_url="userlogin")
def dashboard(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    pending_count = OrderPlaced.objects.filter(status='Pending',is_paid=True).count()
    packed_count = OrderPlaced.objects.filter(status='Packed',is_paid=True).count()
    onway_count = OrderPlaced.objects.filter(status='On The Way',is_paid=True).count()
    delivered_count = OrderPlaced.objects.filter(status='Delivered',is_paid=True).count()
    cancel_count = OrderPlaced.objects.filter(status='Cancel',is_paid=True).count()

    sub_category = SubCategory.objects.all()
    brands = Brands.objects.all()
    products = Product.objects.all()
    subscribe = Subscribe.objects.all()
    context = {
        'pending_count':pending_count,'packed_count':packed_count,
        'onway_count':onway_count,'delivered_count':delivered_count,'cancel_count':cancel_count,
        'sub_category':sub_category,'brands':brands,'products':products,"subscribe":subscribe
        }
    return render(request,'adminpannel/index.html',context)


@login_required(login_url="userlogin")
def addcategory(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    if request.method == "POST":
        title = request.POST['title']
        image = request.FILES['images']
        category = Category(category_name=title,category_image=image)
        category.save()
    category = Category.objects.all()
    context = {'category':category}
    return render(request,'adminpannel/pages/addcategory.html',context)



@login_required(login_url="userlogin")
def delcategory(request,uid):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    category = Category.objects.get(uid=uid)
    category.delete()
    return redirect('addcategory')


@login_required(login_url="userlogin")
def addsubcategory(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    if request.method=="POST":
        title = request.POST['title']
        subcat = request.POST['subcategory']
        image = request.FILES['image']
        subcategory = SubCategory(
            category_name=title,
            category=Category.objects.get(uid= subcat),
            category_image= image
        )
        subcategory.save()

    sub_category = SubCategory.objects.all()
    context = {'sub_category':sub_category}
    return render(request,'adminpannel/pages/addsubcategory.html',context)



@login_required(login_url="userlogin")
def delsubcategory(request,uid):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    subcategory = SubCategory.objects.get(uid=uid)
    subcategory.delete()
    return redirect('addsubcategory')



@login_required(login_url="userlogin")
def addbrands(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    if request.method=="POST":
        title = request.POST['title']
        image = request.FILES['image']
        brands=Brands(
            brands_name=title,
            brands_image=image
        )
        brands.save()
    brands = Brands.objects.all()
    context = {'brands':brands}
    return render(request,'adminpannel/pages/addbrands.html',context)


@login_required(login_url="userlogin")
def delbrands(request,uid):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    brand = Brands.objects.get(uid=uid)
    brand.delete()
    return redirect('addbrands')



@login_required(login_url="userlogin")
def addproduct(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    if request.method =='POST':
        title = request.POST['title']
        # category = request.POST['category']
        subcategory = request.POST['subcategory']
        brands = request.POST['brands']
        mrp_price = request.POST['mrp_price']
        dis_price = request.POST['dis_price']
        desc = request.POST['desc']
        length = request.POST['length']
        breadth = request.POST['breadth']
        height = request.POST['height']
        weight = request.POST['weight']
        product = Product(
            product_name=title,
            sub_category=SubCategory.objects.get(uid=subcategory),
            brands =Brands.objects.get(uid=brands),
            mrp_price=mrp_price,
            dis_price=dis_price,
            product_description=desc,
            length = length,
            breadth = breadth,
            height = height,
            weight = weight,
            is_publish=True
        )
        product.save()
        return redirect('editproduct',product.uid)
    sub_category = SubCategory.objects.all()
    brands = Brands.objects.all()
    context={'sub_category':sub_category,"brands":brands}
    return render(request,'adminpannel/pages/addproduct.html',context)


@login_required(login_url="userlogin")
def editproduct(request,uid):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    if request.method == "POST":
        title = request.POST['title']
        # category = request.POST['category']
        subcategory = request.POST['subcategory']
        brands = request.POST['brands']
        mrp_price = request.POST['mrp_price']
        dis_price = request.POST['dis_price']
        desc = request.POST['desc']

        length = request.POST['length']
        breadth = request.POST['breadth']
        height = request.POST['height']
        weight = request.POST['weight']

        product = Product.objects.get(uid = uid)
        print(product)
        print(SubCategory.objects.get(uid=subcategory))
        product.product_name=title
        product.sub_category=SubCategory.objects.get(uid=subcategory)
        product.brands =Brands.objects.get(uid=brands)
        product.mrp_price=mrp_price
        product.dis_price=dis_price
        product.product_description=desc 
        product.length = length
        product.breadth = breadth
        product.height = height
        product.weight = weight
        product.save()

    product = Product.objects.get(uid = uid)
    sub_category = SubCategory.objects.all()
    brands = Brands.objects.all()
    context={'sub_category':sub_category,"brands":brands,'product':product}
    return render(request,'adminpannel/pages/editproduct.html',context)


@login_required(login_url="userlogin")
def addproductimage(request,uid):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    if request.method == "POST":
        product = Product.objects.get(uid = uid)
        print(product)
        image = request.FILES['image']
        product_images = ProductImage(
            product= product,
            image = image
        )
        product_images.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="userlogin")
def delproductimage(request,uid):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    image = ProductImage.objects.get(uid=uid)
    image.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required(login_url="userlogin")
def delproduct(request,uid):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    product = Product.objects.get(uid=uid)
    product.delete()
    return redirect('allproduct')



@login_required(login_url="userlogin")
def allproduct(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    product = Product.objects.all()
    context = {'product':product}
    return render(request,'adminpannel/pages/allproduct.html',context)



@login_required(login_url="userlogin")
def managepage(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    if request.method =="POST":
        uid = request.POST['uid']
        addtype = request.POST['addtype']
        dis_price = request.POST.get('dis_price')
        dis_datetime = request.POST.get('dis_datetime')
        if addtype == "dealoftheday":
            dealoftheday = DealOfTheDay(
                product = Product.objects.get(uid=uid),
                sale_discount_price = dis_price,
                offer_date= dis_datetime
            )
            dealoftheday.save()
        elif addtype == "hotsaler":
            hotsaler = HotSaler(
                product = Product.objects.get(uid=uid)
            )
            hotsaler.save()
        elif addtype == "bestsaler":
            bestsaler = BestSaler(
                product = Product.objects.get(uid=uid)
            )
            bestsaler.save()
    product = Product.objects.all()
    bestsaler = BestSaler.objects.all()
    hotsaler = HotSaler.objects.all()
    dealoftheday = DealOfTheDay.objects.all()
    context={'product':product,'bestsaler':bestsaler,'hotsaler':hotsaler,'dealoftheday':dealoftheday}
    return render(request,'adminpannel/pages/managepage.html',context)


@login_required(login_url="userlogin")
def delmanagepage(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    uid = request.GET.get('uid')
    addtype = request.GET.get('addtype')  
    print(uid)  
    print(addtype)  
    if addtype == "dealoftheday":
        dealoftheday = DealOfTheDay.objects.get(uid=uid)
        dealoftheday.delete()
    elif addtype == "hotsaler":
        hotsaler = HotSaler.objects.get(uid=uid)
        hotsaler.delete()
    elif addtype == "bestsaler":
        bestsaler = BestSaler.objects.get(uid=uid)
        bestsaler.delete()
    
    return redirect('managepage')


@login_required(login_url="userlogin")
def userdetails(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    user_details = User.objects.all()
    context = {'user_details':user_details}
    return render(request,'adminpannel/pages/userdetails.html',context)



@login_required(login_url="userlogin")
def pending(request):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    if request.method == 'POST':
        cartid = request.POST['cartid']
        status = request.POST['status']
        cart = OrderPlaced.objects.get(uid=cartid)
        cart.status = status
        cart.save()
    if request.user.is_staff ==True:
        pending = OrderPlaced.objects.filter(status='Pending',is_paid=True)
        print(pending)
        context = {'pending':pending}
        return render(request,'adminpannel/ordersummery/pending.html',context)
    return redirect('/')



@login_required(login_url="userlogin")
def packed(request):
    if request.method == 'POST':
        cartid = request.POST['cartid']
        status = request.POST['status']
        cart = OrderPlaced.objects.get(uid=cartid)
        cart.status = status
        cart.save()
        messages.success(request, "Status Change Successfully")
    if request.user.is_staff ==True:
        packed = OrderPlaced.objects.filter(status='Packed',is_paid=True)
        context = {'packed':packed}
        return render(request,'adminpannel/ordersummery/packed.html',context)
    return redirect('/')


@login_required(login_url="userlogin")
def on_the_way(request):
    if request.method == 'POST':
        cartid = request.POST['cartid']
        status = request.POST['status']
        cart = OrderPlaced.objects.get(uid=cartid)
        cart.status = status
        cart.save()
        messages.success(request, "Status Change Successfully")
    if request.user.is_staff ==True:
        on_the_way = OrderPlaced.objects.filter(status='On The Way',is_paid=True)
        context = {'on_the_way':on_the_way}
        return render(request,'adminpannel/ordersummery/ontheway.html',context)
    return redirect('/')



@login_required(login_url="userlogin")
def delivered(request):
    if request.method == 'POST':
        cartid = request.POST['cartid']
        status = request.POST['status']
        cart = OrderPlaced.objects.get(uid=cartid)
        cart.status = status
        cart.save()
        messages.success(request, "Status Change Successfully")
    if request.user.is_staff ==True:
        delivered = OrderPlaced.objects.filter(status='Delivered',is_paid=True)
        context = {'delivered':delivered}
        return render(request,'adminpannel/ordersummery/delivered.html',context)
    return redirect('/')



@login_required(login_url="userlogin")
def cancel(request):
    if request.method == 'POST':
        cartid = request.POST['cartid']
        status = request.POST['status']
        cart = OrderPlaced.objects.get(uid=cartid)
        cart.status = status
        cart.save()
        messages.success(request, "Status Change Successfully")
    if request.user.is_staff ==True:
        cancel = OrderPlaced.objects.filter(status='Cancel',is_paid=True)
        context = {'cancel':cancel}
        return render(request,'adminpannel/ordersummery/cancel.html',context)
    return redirect('/')


@login_required(login_url="userlogin")
def change_status(request):
    change_type = request.GET.get('type')
    uid = request.GET.get('uid')
    if change_type =="category":
        category = Category.objects.get(uid=uid)
        if category.is_publish == True:
            category.is_publish =False
        else:
            category.is_publish =True
        category.save()
    elif change_type =="subcategory":
        subcategory = SubCategory.objects.get(uid=uid)
        if subcategory.is_publish == True:
            subcategory.is_publish =False
        else:
            subcategory.is_publish =True
        subcategory.save()
    elif change_type =="brands":
        brands = Brands.objects.get(uid=uid)
        if brands.is_publish == True:
            brands.is_publish =False
        else:
            brands.is_publish =True
        brands.save()
    elif change_type =="product":
        product = Product.objects.get(uid=uid)
        if product.is_publish == True:
            product.is_publish =False
        else:
            product.is_publish =True
        product.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    



@login_required(login_url="userlogin")
def bills(request,uid):
    bill = OrderPlaced.objects.get(uid=uid)
    amount_words =num2words(bill.paid_amount).upper()
    context = {'bill':bill,'amount_words':amount_words}
    return render(request,'adminpannel/bills.html',context)
  


def contactform(request):
    return render(request,'adminpannel/pages/contactform.html')


def searchproduct(request):
    query = request.GET.get('query')
    if query:
        product = Product.objects.filter(product_name__icontains=query)
    else:
        product = Product.objects.all()
    context = {'product':product}
    return render(request,'adminpannel/pages/searchproduct.html',context)


@login_required(login_url="userlogin")
def delcontact(request,uid):
    user_obj =request.user
    if user_obj.is_staff != True:
                return redirect('adminlogin')
    contact = Contact.objects.get(uid=uid)
    contact.delete()
    return redirect('contactform')




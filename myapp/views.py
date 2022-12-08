from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart,Transaction
from django.conf import settings
from django.core.mail import send_mail
import random
from django.contrib.auth import authenticate, login as auth_login
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Create your views here.
def validate_email(request):
	email=request.GET.get('email')
	data={
		'is_taken':User.objects.filter(email__isexact=email).exists()
	}
	return JsonResponse(data)

def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=='user':
			products=Product.objects.all()
			return render(request,'index.html',{'products':products})

		else:
			return render(request,'seller_index.html')
	except:
		products=Product.objects.all()
		return render(request,'index.html',{'products':products})

def category(request):
	return render(request,'category.html')

def product_detail(request,pk):
	wishlist_flag=False
	cart_flag=False
	product=Product.objects.get(pk=pk)
	try:
		user=User.objects.get(email=request.session['email'])
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass

	try:
		user=User.objects.get(email=request.session['email'])
		Cart.objects.get(user=user,product=product,payment_status=False)
		cart_flag=True
	except:
		pass
	return render(request,'product_detail.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,product=product)
	return redirect('wishlist')


def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(user=user,
				product=product,
				product_price=product.product_price,
				product_qty=1,
				total_price=product.product_price
				)
	return redirect('cart')


def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def change_qty(request,pk):
	cart=Cart.objects.get(pk=pk)
	product_qty=int(request.POST['product_qty'])
	cart.product_qty=product_qty
	cart.total_price=cart.product_price*product_qty
	cart.save()
	return redirect('cart')


def checkout(request):
	return render(request,'checkout.html')

def confirmation(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=True)
	for i in carts:
		net_price=net_price+i.total_price
	return render(request,'confirmation.html',{'carts':carts,'net_price':net_price})


def blog(request):
	return render(request,'blog.html')

def single_blog(request):
	return render(request,'single-blog.html')


def signup(request):
	if request.method=='POST':
		user=User()
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.email=request.POST['email']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']	
		user.password=request.POST['password']
		try:
			User.objects.get(email=request.POST['email'])
			msg='Email Already Registered'
			return render(request,'signup.html',{"msg":msg,'user':user})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
							fname=request.POST['fname'],
							lname=request.POST['lname'],
							email=request.POST['email'],
							mobile=request.POST['mobile'],
							address=request.POST['address'],
							password=request.POST['password'],
							profile_pic=request.FILES['profile_pic'],
							usertype=request.POST['usertype']
							)
				msg='User SignUp Successful'
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Match"
				return render(request,'signup.html',{'msg':msg,'user':user})
	else:
		return render(request,'signup.html')


def login(request):
	if request.method=='POST':
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				if user.usertype=='user':
					request.session['email']=user.email
					request.session['fname']=user.fname
					request.session['profile_pic']=user.profile_pic.url
					wishlists=Wishlist.objects.filter(user=user)
					request.session['wishlist_count']=len(wishlists)
					carts=Cart.objects.filter(user=user,payment_status=False)
					request.session['product_count']=len(carts)
					return redirect('index')
				elif user.usertype=='seller':
					request.session['email']=user.email
					request.session['fname']=user.fname
					request.session['profile_pic']=user.profile_pic.url
					return redirect('seller_index')
			else:
				msg='Password Is Incorrect'
				return render(request,'login.html',{'msg':msg})
		except:
			msg='Email Does Not Exist'
			return render(request,'login.html',{'msg':msg})

	else:
		return render(request,'login.html')
		
def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_pic']
		return render(request,'login.html')

	except:
		return render(request,'login.html')

	##------------------------------------CHANGE PASSWORD------------------------------------##

def change_password(request):
	if request.method=='POST':
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==user.password:
				msg='You Cannot Use Your Old Password'
				return render(request,'change_password.html',{'msg':msg})
			else:

				if request.POST['new_password']==request.POST['cnew_password']:
					user.password=request.POST['new_password']
					user.save()
					del request.session['email']
					del request.session['fname']
					del request.session['profile_pic']
					msg='Password Changed Successfully'
					return render(request,'login.html',{'msg':msg})
				else:
					msg='New Password And Confirm New Password Does Not Match'
					return render(request,'change_password.html',{'msg':msg})
		else:
			msg='Old Password Is Incorrect'
			return render(request,'change_password.html',{'msg':msg})

	else:
		return render(request,'change_password.html')


def tracking(request):
	return render(request,'tracking.html')

def elements(request):
	return render(request,'elements.html')

def contact(request):
	return render(request,'contact.html')

def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=='POST':
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_pic=request.FILES['profile_pic']
		except:
			pass
		user.save()
		msg='Profile Updated Successfully'
		request.session['profile_pic']=user.profile_pic.url
		request.session['fname']=user.fname
		return render(request,'profile.html',{'msg':msg,'user':user})
	else:
		return render(request,'profile.html',{'user':user})

def seller_index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=='seller':
			products=Product.objects.all()
			return render(request,'seller_index.html',{'products':products})

		else:
			return render(request,'index.html')
	except:
		products=Product.objects.all()
		return render(request,'seller_index.html',{'products':products})

def seller_change_password(request):
	if request.method=='POST':
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==user.password:
				msg='You Cannot Use Your Old Password'
				return render(request,'seller_change_password.html',{'msg':msg})
			else:

				if request.POST['new_password']==request.POST['cnew_password']:
					user.password=request.POST['new_password']
					user.save()
					del request.session['email']
					del request.session['fname']
					del request.session['profile_pic']
					msg='Password Changed Successfully'
					return render(request,'login.html',{'msg':msg})
				else:
					msg='New Password And Confirm New Password Does Not Match'
					return render(request,'seller_change_password.html',{'msg':msg})
		else:
			msg='Old Password Is Incorrect'
			return render(request,'seller_change_password.html',{'msg':msg})

	else:
		return render(request,'seller_change_password.html')

def seller_profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=='POST':
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		try:
			user.profile_pic=request.FILES['profile_pic']
		except:
			pass
		user.save()
		msg='Profile Updated Successfully'
		request.session['profile_pic']=user.profile_pic.url
		request.session['fname']=user.fname
		return render(request,'seller_profile.html',{'msg':msg,'user':user})
	else:
		return render(request,'seller_profile.html',{'user':user})

def seller_add_product(request):
	if request.method=='POST':
		seller=User.objects.get(email=request.session['email'])
		Product.objects.create(
				seller=seller,
				product_company=request.POST['product_company'],
				product_name=request.POST['product_name'],
				product_price=request.POST['product_price'],
				product_size=request.POST['product_size'],
				product_image=request.FILES['product_image'],
				product_detail=request.POST['product_detail']
			)	
		msg='Product Added Successfully'
		return render(request,'seller_add_product.html',{'msg':msg})

	else:
		return render(request,'seller_add_product.html')

def seller_view_product(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,'seller_view_product.html',{'products':products})

def seller_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller_product_detail.html',{'product':product})

def seller_product_edit(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=='POST':
		product.product_company=request.POST['product_company']
		product.product_name=request.POST['product_name']
		product.product_price=request.POST['product_price']
		product.product_size=request.POST['product_size']
		product.product_detail=request.POST['product_detail']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		msg="Product Updated Successfully"
		return render(request,'seller_product_edit.html',{'product':product,'msg':msg})

	else:
		return render(request,'seller_product_edit.html',{'product':product})

def seller_product_delete(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	msg='Product Deleted Successfully'
	return redirect('seller_view_product')

def forgot_password(request):
	if request.method=='POST':
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=random.randint(1000,9999)
			subject = 'OTP For Forgot Password'
			message ='Hi '+ user.fname+ ', Your OTP For Forgot Password Is '+ str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email, ]
			send_mail( subject, message, email_from, recipient_list )
			msg='OTP Sent Successfully'
			return render(request,'otp.html',{'otp':otp,'email':user.email,'msg':msg})
		except:
			msg='Email Not Registered'
			return render(request,'forgot_password.html',{'msg':msg}) 
	else:
		return render(request,'forgot_password.html')


def verify_otp(request):
	email=request.POST['email']
	otp=request.POST['otp']
	uotp=request.POST['uotp']

	if otp==uotp:
		return render(request,'new_password.html',{'email':email})
	else:
		msg='OTP Does Not Match'
		return render(request,'otp.html',{'email':email,'otp':otp,'msg':msg})

def update_password(request):
	email=request.POST['email']
	np=request.POST['new_password']
	cnp=request.POST['cnew_password']
	if np==cnp:
		user=User.objects.get(email=email)
		if user.password==np:
			msg='You Cannot Use Your Old Password'
			return render(request,'new_password.html',{'email':email,'msg':msg})
		else:
			user.password=np
			user.save()
			# return redirect('logout')
			msg='Password Updated Successfully'
			return render(request,'login.html',{'msg':msg})
	else:
		msg='New Password & Confirm New Password Does Not Match'
		return render(request,'new_password.html',{'email':email,'msg':msg})

def initiate_payment(request):
	user=User.objects.get(email=request.session['email'])
	try:
		amount = int(request.POST['amount'])
	except:
		return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})
	transaction = Transaction.objects.create(made_by=user, amount=amount)
	transaction.save()
	merchant_key = settings.PAYTM_SECRET_KEY
	params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
        )
	paytm_params = dict(params)
	checksum = generate_checksum(paytm_params, merchant_key)
	transaction.checksum = checksum
	transaction.save()
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	paytm_params['CHECKSUMHASH'] = checksum
	print('SENT: ', checksum)
	return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)
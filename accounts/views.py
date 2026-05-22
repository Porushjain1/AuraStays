from django.shortcuts import render, redirect
from .models import HotelUser, HotelVendor, Hotel, Ameneties, HotelImages, HotelBooking
from django.db.models import Q
from django.contrib import messages
from .utils import generateRandomToken, sendEmailToken, sendOTPtoEmail, generateSlug
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
import random
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

# Create your views here.
def login_page(request):

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')


        hotel_user = HotelUser.objects.filter(
            email = email)


        if not hotel_user.exists():
            messages.warning(request, "No Account Found")
            return redirect('/accounts/login/')
        

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account Not Verified")
            return redirect('/accounts/login/')


        hotel_user = authenticate(username = hotel_user[0].username,password = password)
        if hotel_user:
            messages.success(request, "Login Success")
            login(request, hotel_user)
            return redirect('/')
        
        messages.warning(request, "Invalid Credentials")
        return redirect('/accounts/login/')
    

    return render(request, 'login.html')

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')


        if HotelUser.objects.filter(email=email).exists():
            messages.warning(request, "Email is already registered")
            return redirect('/accounts/register/')
            
        if HotelUser.objects.filter(phone_number=phone_number).exists():
            messages.warning(request, "Phone number is already registered")
            return redirect('/accounts/register/')

        hotel_user = HotelUser.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = password,
            phone_number = phone_number,
            email_token = generateRandomToken(),
        )

        hotel_user.set_password(password)
        hotel_user.save()


        sendEmailToken(email , hotel_user.email_token)

        login(request, hotel_user)
        messages.success(request, "Account created! Welcome to Aura Stays.")
        return redirect('/')
        
    return render(request, 'register.html')


def verify_email_token(request, token):
    try:
        is_vendor = False
        hotel_user = HotelUser.objects.filter(email_token=token).first()
        
        if not hotel_user:
            hotel_user = HotelVendor.objects.filter(email_token=token).first()
            is_vendor = True
            
        if not hotel_user:
            return HttpResponse("Invalid Token")

        hotel_user.is_verified = True
        hotel_user.save()
        messages.success(request, "Email Verified")
        
        if is_vendor:
            return redirect('/accounts/login-vendor/')
        return redirect('/accounts/login/')
    except Exception as e:
        return HttpResponse("Invalid Token")
def send_otp(request, email):
    login_type = request.GET.get('type')
    
    if login_type == 'vendor':
        user_qs = HotelVendor.objects.filter(email=email)
        if not user_qs.exists():
            messages.warning(request, "No Vendor Account Found.")
            return redirect('/accounts/login-vendor/')
    else:
        user_qs = HotelUser.objects.filter(email=email)
        if not user_qs.exists():
            messages.warning(request, "No Account Found.")
            return redirect('/accounts/login/')

    otp = random.randint(1000 , 9999)
    user_qs.update(otp=otp)

    sendOTPtoEmail(email , otp)

    if login_type == 'vendor':
        return redirect(f'/accounts/verify-otp/{email}/?type=vendor')
    return redirect(f'/accounts/verify-otp/{email}/')


def verify_otp(request , email):
    login_type = request.GET.get('type')
    
    if request.method == "POST":
        otp = request.POST.get('otp')
        
        if login_type == 'vendor':
            hotel_user = HotelVendor.objects.filter(email=email).first()
            is_vendor = True
        else:
            hotel_user = HotelUser.objects.filter(email=email).first()
            is_vendor = False

        if hotel_user and otp == hotel_user.otp:
            messages.success(request, "Login Success")
            login(request, hotel_user)
            
            if is_vendor:
                return redirect('/accounts/add-hotel/')
            return redirect('/')

        messages.warning(request, "Wrong OTP")
        if login_type == 'vendor':
            return redirect(f'/accounts/verify-otp/{email}/?type=vendor')
        return redirect(f'/accounts/verify-otp/{email}/')

    return render(request , 'verify_otp.html')


def login_vendor(request):

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')


        hotel_user = HotelVendor.objects.filter(
            email = email)


        if not hotel_user.exists():
            messages.warning(request, "No Account Found")
            return redirect('/accounts/login-vendor/')
        

        if not hotel_user[0].is_verified:
            messages.warning(request, "Account Not Verified")
            return redirect('/accounts/login-vendor/')


        hotel_user = authenticate(username = hotel_user[0].username,password = password)

        if hotel_user:
            messages.success(request, "Login Success")
            login(request, hotel_user)
            return redirect('/accounts/add-hotel/')
        
        messages.warning(request, "Invalid Credentials")
        return redirect('/accounts/login-vendor/')
    

    return render(request, 'vendor/login_vendor.html')


def register_vendor(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name =request.POST.get('last_name')
        business_name = request.POST.get('business_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')


        hotel_user = HotelUser.objects.filter(
            Q(email = email) | Q(phone_number = phone_number)
        )

        if hotel_user.exists():
            messages.warning(request, "Account already exists")
            return redirect('/accounts/register-vendor/')
        


        hotel_user = HotelVendor.objects.create(
            username = phone_number,
            first_name = first_name,
            last_name = last_name,
            business_name = business_name,
            email = email,
            password = password,
            phone_number = phone_number,
            email_token = generateRandomToken(),
        )

        hotel_user.set_password(password)
        hotel_user.save()


        sendEmailToken(email , hotel_user.email_token)

        messages.success(request, "Email send to your email")
        return redirect('/accounts/login-vendor')
        
    return render(request, 'vendor/register_vendor.html')


@login_required(login_url='/accounts/login-vendor/')
def dashboard(request):
    vendor = HotelVendor.objects.get(id=request.user.id)
    hotels = Hotel.objects.filter(hotel_owner=vendor)
    
    # Calculate Metrics
    from django.db.models import Sum
    
    total_hotels = hotels.count()
    bookings = HotelBooking.objects.filter(hotel__in=hotels)
    total_bookings = bookings.count()
    
    revenue = bookings.aggregate(Sum('price'))['price__sum'] or 0
    
    context = {
        'total_hotels': total_hotels,
        'total_bookings': total_bookings,
        'revenue': revenue,
        'recent_bookings': bookings.order_by('-booking_start_date')[:5]
    }
    return render(request, "vendor/vendor_dashboard.html", context)

@login_required(login_url='/accounts/login-vendor/')
def vendor_hotels(request):
    vendor = HotelVendor.objects.get(id=request.user.id)
    context = {'hotels': Hotel.objects.filter(hotel_owner=vendor)}
    return render(request, "vendor/vendor_hotels.html", context)

@login_required(login_url='/accounts/login-vendor/')
def vendor_bookings(request):
    vendor = HotelVendor.objects.get(id=request.user.id)
    hotels = Hotel.objects.filter(hotel_owner=vendor)
    bookings = HotelBooking.objects.filter(hotel__in=hotels).order_by('-booking_start_date')
    context = {'bookings': bookings}
    return render(request, "vendor/vendor_bookings.html", context)



@login_required(login_url='login_vendor')
def add_hotel(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        ameneties = request.POST.getlist('ameneties')   
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        hotel_slug = generateSlug(hotel_name)

        try:
            hotel_vendor = request.user.hotelvendor   
        except HotelVendor.DoesNotExist:
            messages.error(request, "You must be a hotel vendor to add a hotel.")
            return redirect('login_vendor')

        hotel_obj = Hotel.objects.create(
            hotel_name=hotel_name,
            hotel_description=hotel_description,
            hotel_price=hotel_price,
            hotel_offer_price=hotel_offer_price,
            hotel_location=hotel_location,
            hotel_slug=hotel_slug,
            hotel_owner=hotel_vendor
        )

        for ameneti_id in ameneties:
            ameneti = Ameneties.objects.get(id=ameneti_id)
            hotel_obj.ameneties.add(ameneti)

        
        hotel_obj.save()

        messages.success(request, "Hotel Created Successfully")
        return redirect('/accounts/dashboard/')

    ameneties = Ameneties.objects.all()

    return render(request, 'vendor/add_hotel.html', context={'ameneties': ameneties})

@login_required(login_url='login_vendor')
def upload_images(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug = slug)
    if request.method == "POST":
        image = request.FILES['image']
        print(image)
        HotelImages.objects.create(
        hotel = hotel_obj,
        image = image
        )
        return HttpResponseRedirect(request.path_info)
    return render(request, 'vendor/upload_images.html', context = {'images' : hotel_obj.hotel_images.all()})

@login_required(login_url='login_vendor')
def delete_image(request, id):
    print(id)
    print("#######")
    hotel_image = HotelImages.objects.get(id = id)
    hotel_image.delete()
    messages.success(request, "Hotel Image deleted")
    return redirect('/accounts/dashboard/')



@login_required(login_url='login_vendor')
def edit_hotel(request, slug):
    hotel_obj = Hotel.objects.get(hotel_slug=slug)
    

    if request.user.id != hotel_obj.hotel_owner.id:
        return HttpResponse("You are not authorized")

    if request.method == "POST":
        
        hotel_name = request.POST.get('hotel_name')
        hotel_description = request.POST.get('hotel_description')
        hotel_price = request.POST.get('hotel_price')
        hotel_offer_price = request.POST.get('hotel_offer_price')
        hotel_location = request.POST.get('hotel_location')
        
        
        hotel_obj.hotel_name = hotel_name
        hotel_obj.hotel_description = hotel_description
        hotel_obj.hotel_price = hotel_price
        hotel_obj.hotel_offer_price = hotel_offer_price
        hotel_obj.hotel_location = hotel_location
        hotel_obj.save()
        
        messages.success(request, "Hotel Details Updated")

        return HttpResponseRedirect(request.path_info)

    
    ameneties = Ameneties.objects.all()
    
    return render(request, 'vendor/edit_hotel.html', context={'hotel': hotel_obj, 'ameneties': ameneties})


def logout_view(request):
    logout(request)
    return redirect('/accounts/login/')
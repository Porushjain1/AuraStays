from django.shortcuts import render
from accounts.models import Hotel , HotelBooking, HotelUser
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.cache import cache_page

from django.db.models import Q

# Create your views here.
from django.db.models import Count

def index(request):
    hotels = Hotel.objects.all()
    search_query = request.GET.get('search')
    
    if search_query:
        print(f"DEBUG: Searching for '{search_query}'")
        hotels = hotels.filter(
            Q(hotel_name__icontains=search_query) | 
            Q(hotel_location__icontains=search_query)
        )
        print(f"DEBUG: Found {hotels.count()} hotels matching '{search_query}'")

    if request.GET.get('sort_by'):
        sort_by = request.GET.get('sort_by')
        if sort_by == "sort_low":
            hotels = hotels.order_by('hotel_offer_price')
        elif sort_by == "sort_high":
            hotels = hotels.order_by('-hotel_offer_price')
            
    # Dynamic Trending Destinations
    trending_locations = Hotel.objects.values('hotel_location').annotate(hotel_count=Count('id')).order_by('-hotel_count')[:3]
    
    image_mapping = {
        'goa': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'manali': 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'jaipur': 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'bangalore': 'https://images.unsplash.com/photo-1596176530529-78163a4f7af2?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'mumbai': 'https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
        'delhi': 'https://images.unsplash.com/photo-1587474260584-136574528ed5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80'
    }
    
    destinations = []
    for loc in trending_locations:
        name = loc['hotel_location']
        img_url = 'https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80' # default
        for key, url in image_mapping.items():
            if key in name.lower():
                img_url = url
                break
        
        destinations.append({
            'name': name.title(),
            'count': loc['hotel_count'],
            'image': img_url
        })

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'hotel_list_partial.html', context = {
            'hotels': hotels[:50]
        })

    return render(request, 'index.html', context = {
        'hotels': hotels[:50],
        'destinations': destinations
    })

from datetime import datetime



def hotel_details(request, slug):
    hotel = Hotel.objects.get(hotel_slug = slug)

    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = datetime.strptime(start_date , '%Y-%m-%d')
        end_date = datetime.strptime(end_date , '%Y-%m-%d')
        days_count = (end_date - start_date).days

        if days_count <= 0:
            messages.warning(request, "Invalid Booking Date.")

            return HttpResponseRedirect(request.path_info)

        
        HotelBooking.objects.create(
            hotel = hotel,
            booking_user=request.user,
            booking_start_date = start_date,
            booking_end_date =end_date,
            price = hotel.hotel_offer_price * days_count
        )
        messages.warning(request, "Booking Captured.")

        return HttpResponseRedirect(request.path_info)


    return render(request, 'hotel_detail.html', context = {'hotel' : hotel})
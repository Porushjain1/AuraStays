import os
import django
import ssl

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oyo_clone.settings")
django.setup()

from accounts.models import HotelVendor, Ameneties, Hotel, HotelImages
from django.core.files.base import ContentFile
import urllib.request
from django.utils.text import slugify

# Fix SSL issue on Mac
ssl._create_default_https_context = ssl._create_unverified_context

def seed_data():
    # Clear existing to prevent duplicates without images
    Hotel.objects.all().delete()

    # 1. Create a Vendor
    vendor, created = HotelVendor.objects.get_or_create(
        username="demo_vendor",
        defaults={
            "phone_number": "1234567890",
            "business_name": "Premium Hotels Group",
            "is_verified": True
        }
    )
    if created:
        vendor.set_password("password123")
        vendor.save()

    # 2. Create Amenities
    wifi, _ = Ameneties.objects.get_or_create(name="Wifi")
    pool, _ = Ameneties.objects.get_or_create(name="Swimming Pool")
    ac, _ = Ameneties.objects.get_or_create(name="AC")

    # 3. Create Hotels
    hotels_data = [
        # Goa
        {"name": "Luxury Oceanfront Resort", "desc": "Experience the best oceanfront views with premium amenities.", "price": 8000, "offer_price": 5500, "location": "Goa, India", "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        {"name": "Beachside Villa", "desc": "Private villa right on the beach.", "price": 12000, "offer_price": 9500, "location": "Goa, India", "image_url": "https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        
        # Manali
        {"name": "Mountain View Retreat", "desc": "A peaceful retreat in the mountains.", "price": 5000, "offer_price": 3500, "location": "Manali, India", "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        {"name": "Snow Peak Cabin", "desc": "Cozy cabin with snow peak views.", "price": 4000, "offer_price": 2500, "location": "Manali, India", "image_url": "https://images.unsplash.com/photo-1605649487212-4d4ce7ca6601?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        
        # Mumbai
        {"name": "Urban Boutique Hotel", "desc": "Stay in the heart of the city in style.", "price": 4000, "offer_price": 2800, "location": "Mumbai, India", "image_url": "https://images.unsplash.com/photo-1551882547-ff40c0d589rx?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        {"name": "Sea Link Grand", "desc": "Luxury hotel overlooking the sea link.", "price": 9500, "offer_price": 7200, "location": "Mumbai, India", "image_url": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        
        # Jaipur
        {"name": "Desert Oasis Palace", "desc": "Live like royalty in this desert palace.", "price": 12000, "offer_price": 8900, "location": "Jaipur, India", "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        {"name": "Heritage Haveli", "desc": "Authentic Rajasthani heritage haveli.", "price": 6000, "offer_price": 4500, "location": "Jaipur, India", "image_url": "https://images.unsplash.com/photo-1542314831-c6a4d14ce8a1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        
        # Bangalore
        {"name": "Tech Hub Suites", "desc": "Modern suites for the working professional.", "price": 3500, "offer_price": 2200, "location": "Bangalore, India", "image_url": "https://images.unsplash.com/photo-1555854877-bab0e564b8d5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        {"name": "Garden City Resort", "desc": "Lush green resort in the garden city.", "price": 7000, "offer_price": 5000, "location": "Bangalore, India", "image_url": "https://images.unsplash.com/photo-1584132967334-10e028bd69f7?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        {"name": "Koramangala Premium Stays", "desc": "Premium stay in the heart of Koramangala.", "price": 4500, "offer_price": 3000, "location": "Bangalore, India", "image_url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        
        # Delhi
        {"name": "Capital Grand Hotel", "desc": "5-star luxury in New Delhi.", "price": 10000, "offer_price": 7500, "location": "New Delhi, India", "image_url": "https://images.unsplash.com/photo-1564501049412-61c2a3083791?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        {"name": "Connaught Place Inn", "desc": "Budget friendly inn near CP.", "price": 2500, "offer_price": 1800, "location": "New Delhi, India", "image_url": "https://images.unsplash.com/photo-1522798514-97ceb8c4f1c8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        
        # Kerala
        {"name": "Backwater Houseboat", "desc": "Float on the serene backwaters of Kerala.", "price": 8500, "offer_price": 6000, "location": "Alleppey, Kerala", "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        {"name": "Munnar Tea Estate Resort", "desc": "Wake up to the smell of fresh tea.", "price": 6500, "offer_price": 4800, "location": "Munnar, Kerala", "image_url": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        
        # Udaipur
        {"name": "Lake View Palace", "desc": "Majestic palace with a view of Lake Pichola.", "price": 15000, "offer_price": 11000, "location": "Udaipur, India", "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        
        # Hyderabad
        {"name": "Nawabi Heritage Hotel", "desc": "Experience the royal Nizam hospitality.", "price": 5500, "offer_price": 3800, "location": "Hyderabad, India", "image_url": "https://images.unsplash.com/photo-1582719508461-905c673771fd?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
        
        # Chennai
        {"name": "Marina Beach Resort", "desc": "Resort located minutes away from Marina Beach.", "price": 4800, "offer_price": 3200, "location": "Chennai, India", "image_url": "https://images.unsplash.com/photo-1540541338287-41700207dee6?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"},
    ]

    for data in hotels_data:
        slug = slugify(data["name"])
        if not Hotel.objects.filter(hotel_slug=slug).exists():
            hotel = Hotel.objects.create(
                hotel_name=data["name"],
                hotel_description=data["desc"],
                hotel_slug=slug,
                hotel_owner=vendor,
                hotel_price=data["price"],
                hotel_offer_price=data["offer_price"],
                hotel_location=data["location"],
                is_active=True
            )
            hotel.ameneties.add(wifi, ac)
            if "Resort" in data["name"] or "Palace" in data["name"]:
                hotel.ameneties.add(pool)
            
            # Download and save image
            try:
                # Use a reliable fallback if the URL fails
                img_url = data["image_url"] if "rx" not in data["image_url"] else "https://images.unsplash.com/photo-1542314831-c6a4d14ce8a1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
                req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                response = urllib.request.urlopen(req)
                image_content = response.read()
                
                hotel_img = HotelImages(hotel=hotel)
                hotel_img.images.save(f"{slug}.jpg", ContentFile(image_content))
                hotel_img.save()
            except Exception as e:
                print(f"Failed to save image for {data['name']}: {e}")

    print("Successfully seeded 4 premium hotels.")

if __name__ == "__main__":
    seed_data()

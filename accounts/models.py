from django.db import models
from django.contrib.auth.models import User


class HotelUser(User):
    profile_picture = models.ImageField(upload_to = "profile")
    phone_number = models.CharField(max_length=100,unique = True)
    email_token = models.CharField(max_length = 100, null = True, blank = True)
    otp = models.CharField(max_length= 10, null= True, blank= True) 
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Hotel User"
        verbose_name_plural = "Hotel Users"


class HotelVendor(User):
    profile_picture = models.ImageField(upload_to = "profile")
    business_name = models.CharField(max_length= 100)
    phone_number = models.CharField(max_length=100,unique = True)
    email_token = models.CharField(max_length = 100, null = True, blank = True)
    otp = models.CharField(max_length= 10, null= True, blank= True) 
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "Hotel Vendors"



class Ameneties(models.Model):
    name = models.CharField(max_length=1000)

    def __str__(self) -> str:
        return self.name


class Hotel(models.Model):
    hotel_name  = models.CharField(max_length= 100)
    hotel_description = models.TextField()
    hotel_slug = models.SlugField(max_length=191 , unique= True)
    hotel_owner = models.ForeignKey(HotelVendor, on_delete = models.CASCADE , related_name = "hotels")
    ameneties = models.ManyToManyField(Ameneties)
    hotel_price = models.FloatField()
    hotel_offer_price = models.FloatField()
    hotel_location  = models.TextField()
    is_active = models.BooleanField(default = True)


class HotelImages(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete = models.CASCADE , related_name = "hotel_images")
    images = models.ImageField(upload_to="hotels")


class HotelManager(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete = models.CASCADE , related_name = "hotel_manager")
    manager_name = models.CharField(max_length=100)
    manager_contact = models.CharField(max_length= 100)


class HotelBooking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete = models.CASCADE , related_name="bookings" )
    booking_user = models.ForeignKey(HotelUser, on_delete = models.CASCADE , )
    booking_start_date = models.DateField()
    booking_end_date = models.DateField()
    price = models.FloatField()
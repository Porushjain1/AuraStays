import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oyo_clone.settings")
django.setup()

from accounts.models import Ameneties

amenities_to_add = [
    "Gym",
    "Spa",
    "Breakfast Included",
    "Free Parking",
    "Smart TV",
    "Kitchen",
    "Room Service",
    "Pet Friendly",
    "Minibar",
    "Beach Access",
    "Airport Shuttle",
    "Valet Parking",
    "Bar / Lounge",
    "Business Center",
    "Hot Tub",
    "Ocean View",
]

added_count = 0
for amenity_name in amenities_to_add:
    obj, created = Ameneties.objects.get_or_create(name=amenity_name)
    if created:
        added_count += 1
        print(f"Added amenity: {amenity_name}")

print(f"Successfully added {added_count} new amenities.")

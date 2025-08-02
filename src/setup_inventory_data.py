#!/usr/bin/env python
"""
Script to create necessary data for inventory management system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from stores.models import Store, Storage, Country, City
from users.models import CustomUser

def create_basic_data():
    """Create basic countries, cities and storages for existing stores"""
    
    # Create Kazakhstan country if not exists
    country, created = Country.objects.get_or_create(
        name="Казахстан",
        defaults={"code": "KZ"}
    )
    if created:
        print(f"✅ Created country: {country.name}")
    
    # Create Almaty city if not exists
    city, created = City.objects.get_or_create(
        name="Алматы",
        defaults={"country": country}
    )
    if created:
        print(f"✅ Created city: {city.name}")
    
    # Create storages for all stores that don't have them
    stores_without_storage = Store.objects.filter(storage__isnull=True).distinct()
    
    for store in stores_without_storage:
        storage, created = Storage.objects.get_or_create(
            store=store,
            defaults={
                "name": f"Основной склад {store.name}",
                "city": city,
                "address": "ул. Абая, 150"
            }
        )
        if created:
            print(f"✅ Created storage for store: {store.name}")
    
    # Show summary
    total_stores = Store.objects.count()
    total_storages = Storage.objects.count()
    print(f"\n📊 Summary:")
    print(f"   Total stores: {total_stores}")
    print(f"   Total storages: {total_storages}")
    print(f"   Countries: {Country.objects.count()}")
    print(f"   Cities: {City.objects.count()}")

if __name__ == "__main__":
    print("🚀 Setting up inventory management data...")
    create_basic_data()
    print("✅ Setup completed!")

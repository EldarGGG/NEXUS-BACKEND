#!/usr/bin/env python
"""
Simple script to update product prices
Run with: python manage.py shell -c "exec(open('simple_price_update.py').read())"
"""

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from stores.models import Item

def update_prices():
    print("Updating product prices...")
    
    # Update all items to have realistic prices
    items = Item.objects.all()
    
    for i, item in enumerate(items):
        # Set different prices for variety
        prices = [Decimal('500.00'), Decimal('1000.00'), Decimal('1500.00'), Decimal('2000.00'), Decimal('750.00')]
        item.default_price = prices[i % len(prices)]
        item.save()
        print(f"Updated {item.name}: {item.default_price} тенге")
    
    print(f"Updated {items.count()} products with new prices!")

# Run the update
update_prices()

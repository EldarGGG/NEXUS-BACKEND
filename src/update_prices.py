#!/usr/bin/env python
"""
Script to update product prices for testing
Run with: python manage.py shell < update_prices.py
"""

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from stores.models import Store, Item, Stock

def update_product_prices():
    print("Updating product prices...")
    
    # Get all items and update their prices
    items = Item.objects.all()
    
    for item in items:
        # Set realistic prices based on product names
        if 'молоко' in item.name.lower() or 'milk' in item.name.lower():
            item.default_price = Decimal('500.00')  # 500 тенге
        elif 'хлеб' in item.name.lower() or 'bread' in item.name.lower():
            item.default_price = Decimal('200.00')  # 200 тенге
        elif 'мясо' in item.name.lower() or 'meat' in item.name.lower():
            item.default_price = Decimal('2500.00')  # 2500 тенге
        elif 'овощи' in item.name.lower() or 'vegetables' in item.name.lower():
            item.default_price = Decimal('300.00')  # 300 тенге
        elif 'фрукты' in item.name.lower() or 'fruits' in item.name.lower():
            item.default_price = Decimal('800.00')  # 800 тенге
        else:
            item.default_price = Decimal('1000.00')  # 1000 тенге по умолчанию
        
        item.save()
        print(f"Updated {item.name}: {item.default_price} тенге")
    
    # Also ensure all items have stock
    for item in items:
        stock, created = Stock.objects.get_or_create(
            item=item,
            defaults={
                'amount': 100,  # 100 штук в наличии
            }
        )
        if created:
            print(f"Created stock for {item.name}: {stock.amount} units")
        elif stock.amount == 0:
            stock.amount = 100
            stock.save()
            print(f"Updated stock for {item.name}: {stock.amount} units")
    
    print("Price and stock update completed!")

if __name__ == '__main__':
    update_product_prices()

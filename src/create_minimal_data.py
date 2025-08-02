#!/usr/bin/env python
"""
Minimal script to create basic test data for Nexus platform
"""

import os
import django
from decimal import Decimal
from django.utils import timezone
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser
from stores.models import Store, Item, Category, Subcategory
from orders.models import Order, OrderItem, Task, Counterparty

def create_minimal_data():
    print("Creating minimal test data...")
    
    # 1. Create seller user
    seller, created = CustomUser.objects.get_or_create(
        username='seller',
        defaults={
            'email': 'seller@nexus.com',
            'first_name': 'Продавец',
            'last_name': 'Тестовый'
        }
    )
    if created:
        seller.set_password('password123')
        seller.save()
        print(f"Created seller: {seller.username}")
    
    # 2. Create test store
    store, created = Store.objects.get_or_create(
        name='Тестовый магазин',
        defaults={
            'description': 'Магазин для тестирования',
            'email': 'store@nexus.com',
            'phone': '+7 777 123 4567',
            'owner': seller
        }
    )
    if created:
        print(f"Created store: {store.name}")
    
    # 3. Create UOM
    uom, _ = Uom.objects.get_or_create(name='шт', defaults={'description': 'Штуки'})
    
    # 4. Create category
    group, _ = Group.objects.get_or_create(
        store=store,
        name='Электроника',
        defaults={'description': 'Электронные устройства', 'is_root': True}
    )
    
    # 5. Create products
    products = [
        {'name': 'iPhone 15', 'price': Decimal('450000.00')},
        {'name': 'Samsung Galaxy S24', 'price': Decimal('380000.00')},
        {'name': 'MacBook Pro', 'price': Decimal('850000.00')},
    ]
    
    for product_data in products:
        product, created = Item.objects.get_or_create(
            store=store,
            name=product_data['name'],
            defaults={
                'description': f'Описание для {product_data["name"]}',
                'default_price': product_data['price'],
                'group': group,
                'uom': uom,
                'status': True
            }
        )
        if created:
            print(f"Created product: {product.name}")
    
    # 6. Create task category
    task_category, _ = TaskCategory.objects.get_or_create(
        name='Общие задачи',
        defaults={'color': '#3B82F6'}
    )
    
    # 7. Create tasks
    tasks = [
        {'title': 'Обработать заказы', 'priority': 'high', 'status': 'pending'},
        {'title': 'Обновить товары', 'priority': 'medium', 'status': 'in_progress'},
        {'title': 'Проверить склад', 'priority': 'low', 'status': 'completed'},
    ]
    
    for task_data in tasks:
        task, created = Task.objects.get_or_create(
            title=task_data['title'],
            store=store,
            defaults={
                'description': f'Описание для {task_data["title"]}',
                'priority': task_data['priority'],
                'status': task_data['status'],
                'category': task_category,
                'assigned_to': seller,
                'created_by': seller
            }
        )
        if created:
            print(f"Created task: {task.title}")
    
    # 8. Create buyer and orders
    buyer, created = CustomUser.objects.get_or_create(
        username='buyer',
        defaults={
            'email': 'buyer@nexus.com',
            'first_name': 'Покупатель',
            'last_name': 'Тестовый'
        }
    )
    if created:
        buyer.set_password('password123')
        buyer.save()
        print(f"Created buyer: {buyer.username}")
    
    # Create orders
    order_statuses = ['pending', 'processing', 'delivered']
    products_list = list(Item.objects.filter(store=store))
    
    for i, status in enumerate(order_statuses):
        order, created = Order.objects.get_or_create(
            user=buyer,
            store=store,
            status=status,
            defaults={
                'comment': f'Тестовый заказ {i+1}',
                'total_price': Decimal('100000.00')
            }
        )
        
        if created and products_list:
            # Add one item to order
            product = products_list[i % len(products_list)]
            OrderItem.objects.create(
                order=order,
                item=product,
                amount=1,
                price_per_item=product.default_price,
                total_price=product.default_price
            )
            order.total_price = product.default_price
            order.save()
            print(f"Created order: {order.order_number}")
    
    print("✅ Minimal test data created successfully!")
    print(f"- Users: {CustomUser.objects.count()}")
    print(f"- Stores: {Store.objects.count()}")
    print(f"- Products: {Item.objects.count()}")
    print(f"- Orders: {Order.objects.count()}")
    print(f"- Tasks: {Task.objects.count()}")

if __name__ == '__main__':
    create_minimal_data()

#!/usr/bin/env python
"""
Script to create a test user with store for JWT authentication testing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser
from stores.models import Store
from orders.models import Cart, Order, OrderItem, Task, Counterparty
from decimal import Decimal
from django.utils import timezone
import random

def create_test_user():
    print("Creating test user with store...")
    
    # Create test user
    phone = "+1234567890"
    email = "test@nexus.com"
    password = "testpass123"
    
    # Check if user already exists
    if CustomUser.objects.filter(username=phone).exists():
        print(f"User with phone {phone} already exists")
        user = CustomUser.objects.get(username=phone)
    else:
        user = CustomUser.objects.create_user(
            username=phone,
            email=email,
            password=password,
            first_name="Test",
            last_name="User"
        )
        print(f"Created user: {user.username}")
    
    # Create cart for user if doesn't exist
    cart, created = Cart.objects.get_or_create(user=user)
    if created:
        print(f"Created cart for user: {user.username}")
    
    # Create store for user if doesn't exist
    store, created = Store.objects.get_or_create(
        owner=user,
        defaults={
            'name': 'Test Store',
            'description': 'Test store for JWT authentication testing',
            'phone': phone,
            'email': email
        }
    )
    if created:
        print(f"Created store: {store.name}")
    
    # Create some test orders
    for i in range(3):
        order, created = Order.objects.get_or_create(
            user=user,
            store=store,
            order_number=f'TEST-ORDER-{i+1}',
            defaults={
                'total_price': Decimal(f'{random.randint(100, 1000)}.00'),
                'status': random.choice(['pending', 'confirmed', 'processing']),
                'comment': f'Test order {i+1}',
                'delivery_address': f'Test Address {i+1}'
            }
        )
        if created:
            print(f"Created order: {order.id}")
    
    # Create some test tasks
    for i in range(2):
        task, created = Task.objects.get_or_create(
            store=store,
            title=f'Test Task {i+1}',
            defaults={
                'description': f'Description for test task {i+1}',
                'priority': random.choice(['low', 'medium', 'high']),
                'status': random.choice(['pending', 'in_progress', 'completed']),
                'assigned_to': user,
                'created_by': user
            }
        )
        if created:
            print(f"Created task: {task.title}")
    
    # Create some test counterparties
    for i in range(2):
        counterparty, created = Counterparty.objects.get_or_create(
            store=store,
            name=f'Test Counterparty {i+1}',
            defaults={
                'type': random.choice(['customer', 'supplier']),
                'phone': f'+987654321{i}',
                'email': f'counterparty{i+1}@test.com',
                'address': f'Address {i+1}',
                'status': 'active'
            }
        )
        if created:
            print(f"Created counterparty: {counterparty.name}")
    
    print("\n" + "="*50)
    print("TEST USER CREATED SUCCESSFULLY!")
    print("="*50)
    print(f"Phone: {phone}")
    print(f"Password: {password}")
    print(f"User ID: {user.id}")
    print(f"Store: {store.name} (ID: {store.id})")
    print(f"Frontend URL: http://localhost:3002/{user.id}/seller")
    print("="*50)

if __name__ == "__main__":
    create_test_user()

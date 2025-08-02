#!/usr/bin/env python
"""
Simplified script to create basic test data for Nexus platform
"""

import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser
from stores.models import Store, Item, Group, Uom
from orders.models import Order, OrderItem, TaskCategory, Task

def create_basic_test_data():
    print("Creating basic test data for Nexus platform...")
    
    # 1. Create test users
    print("Creating users...")
    
    # Create seller user
    seller, created = CustomUser.objects.get_or_create(
        username='seller',
        defaults={
            'email': 'seller@nexus.com',
            'first_name': 'Продавец',
            'last_name': 'Тестовый',
            'is_staff': False,
            'is_active': True
        }
    )
    if created:
        seller.set_password('password123')
        seller.save()
        print(f"Created seller: {seller.username}")
    else:
        print(f"Seller already exists: {seller.username}")
    
    # Create buyer user
    buyer, created = CustomUser.objects.get_or_create(
        username='buyer',
        defaults={
            'email': 'buyer@nexus.com',
            'first_name': 'Покупатель',
            'last_name': 'Тестовый',
            'is_staff': False,
            'is_active': True
        }
    )
    if created:
        buyer.set_password('password123')
        buyer.save()
        print(f"Created buyer: {buyer.username}")
    else:
        print(f"Buyer already exists: {buyer.username}")
    
    # 2. Create test store
    print("Creating store...")
    store, created = Store.objects.get_or_create(
        name='Тестовый магазин Nexus',
        defaults={
            'description': 'Магазин для тестирования функционала платформы Nexus',
            'email': 'store@nexus.com',
            'phone': '+7 777 123 4567',
            'owner': seller
        }
    )
    if created:
        print(f"Created store: {store.name}")
    else:
        print(f"Store already exists: {store.name}")
    
    # 3. Create units of measurement
    print("Creating units...")
    uom_pcs, _ = Uom.objects.get_or_create(name='шт', defaults={'description': 'Штуки'})
    uom_kg, _ = Uom.objects.get_or_create(name='кг', defaults={'description': 'Килограммы'})
    
    # 4. Create product categories
    print("Creating categories...")
    electronics_group, _ = Group.objects.get_or_create(
        store=store,
        name='Электроника',
        defaults={'description': 'Электронные устройства', 'is_root': True}
    )
    
    clothing_group, _ = Group.objects.get_or_create(
        store=store,
        name='Одежда',
        defaults={'description': 'Одежда и аксессуары', 'is_root': True}
    )
    
    # 5. Create test products
    print("Creating products...")
    products_data = [
        {
            'name': 'iPhone 15 Pro',
            'description': 'Новейший смартфон Apple',
            'price': Decimal('450000.00'),
            'group': electronics_group,
            'uom': uom_pcs
        },
        {
            'name': 'Samsung Galaxy S24',
            'description': 'Флагманский Android смартфон',
            'price': Decimal('380000.00'),
            'group': electronics_group,
            'uom': uom_pcs
        },
        {
            'name': 'Футболка Nike',
            'description': 'Спортивная футболка',
            'price': Decimal('8500.00'),
            'group': clothing_group,
            'uom': uom_pcs
        }
    ]
    
    created_products = []
    for product_data in products_data:
        product, created = Item.objects.get_or_create(
            store=store,
            name=product_data['name'],
            defaults={
                'description': product_data['description'],
                'default_price': product_data['price'],
                'group': product_data['group'],
                'uom': product_data['uom'],
                'status': True
            }
        )
        if created:
            print(f"Created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")
        created_products.append(product)
    
    # 6. Create task categories
    print("Creating task categories...")
    task_categories = [
        {'name': 'Обработка заказов', 'color': '#3B82F6'},
        {'name': 'Управление товарами', 'color': '#10B981'},
        {'name': 'Клиентская поддержка', 'color': '#F59E0B'},
    ]
    
    created_categories = []
    for cat_data in task_categories:
        category, created = TaskCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'color': cat_data['color']}
        )
        if created:
            print(f"Created task category: {category.name}")
        else:
            print(f"Task category already exists: {category.name}")
        created_categories.append(category)
    
    # 7. Create test tasks
    print("Creating tasks...")
    tasks_data = [
        {
            'title': 'Обработать новые заказы',
            'description': 'Проверить и подтвердить заказы за последние 24 часа',
            'priority': 'high',
            'status': 'pending',
            'category': created_categories[0] if created_categories else None
        },
        {
            'title': 'Обновить описания товаров',
            'description': 'Добавить подробные описания для новых товаров',
            'priority': 'medium',
            'status': 'in_progress',
            'category': created_categories[1] if len(created_categories) > 1 else None
        }
    ]
    
    for task_data in tasks_data:
        task, created = Task.objects.get_or_create(
            title=task_data['title'],
            store=store,
            defaults={
                'description': task_data['description'],
                'priority': task_data['priority'],
                'status': task_data['status'],
                'category': task_data['category'],
                'assigned_to': seller,
                'created_by': seller,
                'due_date': timezone.now() + timedelta(hours=24)
            }
        )
        if created:
            print(f"Created task: {task.title}")
        else:
            print(f"Task already exists: {task.title}")
    
    # 8. Create test orders
    print("Creating test orders...")
    if created_products:
        order, created = Order.objects.get_or_create(
            user=buyer,
            store=store,
            defaults={
                'status': 'pending',
                'comment': 'Тестовый заказ'
            }
        )
        
        if created:
            # Add items to order
            product = created_products[0]  # iPhone
            OrderItem.objects.create(
                order=order,
                item=product,
                amount=1,
                price_per_item=product.default_price,
                total_price=product.default_price
            )
            
            order.total_price = product.default_price
            order.save()
            print(f"Created order: {order.order_number} - {order.total_price} ₸")
        else:
            print(f"Order already exists: {order.order_number}")
    
    print("✅ Basic test data creation completed successfully!")
    print("\nCreated/Verified:")
    print(f"- Users: {CustomUser.objects.count()}")
    print(f"- Stores: {Store.objects.count()}")
    print(f"- Products: {Item.objects.count()}")
    print(f"- Orders: {Order.objects.count()}")
    print(f"- Tasks: {Task.objects.count()}")
    print(f"- Task Categories: {TaskCategory.objects.count()}")
    
    print("\nLogin credentials:")
    print("Seller: seller / password123")
    print("Buyer: buyer / password123")
    print("Admin: admin / (set password via admin)")

if __name__ == '__main__':
    create_basic_test_data()

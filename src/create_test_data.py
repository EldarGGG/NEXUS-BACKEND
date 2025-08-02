#!/usr/bin/env python
"""
Script to create test data for Nexus platform
Run with: python manage.py shell < create_test_data.py
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
from stores.models import Store, Item, Group, Uom, CounterpartyGroup, CounterpartyMember, Storage, Stock, Country, City
from orders.models import Order, OrderItem, Cart, CartItem, Task, TaskCategory

def create_test_data():
    print("Creating test data for Nexus platform...")
    
    # 1. Create test users
    print("Creating users...")
    
    # Create seller user
    try:
        seller = CustomUser.objects.get(username='seller')
        print(f"Seller already exists: {seller.username}")
    except CustomUser.DoesNotExist:
        seller = CustomUser.objects.create_user(
            username='seller',
            email='seller@nexus.com',
            password='password123',
            first_name='Продавец',
            last_name='Тестовый'
        )
        print(f"Created seller: {seller.username} ({seller.email})")
    
    # Create buyer user
    try:
        buyer = CustomUser.objects.get(username='buyer')
        print(f"Buyer already exists: {buyer.username}")
    except CustomUser.DoesNotExist:
        buyer = CustomUser.objects.create_user(
            username='buyer',
            email='buyer@nexus.com',
            password='password123',
            first_name='Покупатель',
            last_name='Тестовый'
        )
        print(f"Created buyer: {buyer.username} ({buyer.email})")
    
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
    
    # 3. Create units of measurement
    print("Creating units...")
    uom_pcs, _ = Uom.objects.get_or_create(name='шт', defaults={'description': 'Штуки'})
    uom_kg, _ = Uom.objects.get_or_create(name='кг', defaults={'description': 'Килограммы'})
    uom_l, _ = Uom.objects.get_or_create(name='л', defaults={'description': 'Литры'})
    
    # 4. Create product categories
    print("Creating categories...")
    electronics_group, _ = Group.objects.get_or_create(
        store=store,
        name='Электроника',
        defaults={'description': 'Электронные устройства и аксессуары', 'is_root': True}
    )
    
    clothing_group, _ = Group.objects.get_or_create(
        store=store,
        name='Одежда',
        defaults={'description': 'Одежда и аксессуары', 'is_root': True}
    )
    
    food_group, _ = Group.objects.get_or_create(
        store=store,
        name='Продукты питания',
        defaults={'description': 'Продукты и напитки', 'is_root': True}
    )
    
    # 5. Create test products
    print("Creating products...")
    products_data = [
        {
            'name': 'iPhone 15 Pro',
            'description': 'Новейший смартфон Apple с передовыми технологиями',
            'price': Decimal('450000.00'),
            'group': electronics_group,
            'uom': uom_pcs
        },
        {
            'name': 'Samsung Galaxy S24',
            'description': 'Флагманский Android смартфон от Samsung',
            'price': Decimal('380000.00'),
            'group': electronics_group,
            'uom': uom_pcs
        },
        {
            'name': 'MacBook Pro 16"',
            'description': 'Мощный ноутбук для профессионалов',
            'price': Decimal('850000.00'),
            'group': electronics_group,
            'uom': uom_pcs
        },
        {
            'name': 'Футболка Nike',
            'description': 'Спортивная футболка из качественного материала',
            'price': Decimal('8500.00'),
            'group': clothing_group,
            'uom': uom_pcs
        },
        {
            'name': 'Джинсы Levi\'s',
            'description': 'Классические джинсы премиум качества',
            'price': Decimal('25000.00'),
            'group': clothing_group,
            'uom': uom_pcs
        },
        {
            'name': 'Кофе арабика',
            'description': 'Премиальный кофе из отборных зерен',
            'price': Decimal('3500.00'),
            'group': food_group,
            'uom': uom_kg
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
        created_products.append(product)
    
    # 6. Create storage and stock
    print("Creating storage and stock...")
    country, _ = Country.objects.get_or_create(name='Казахстан')
    city, _ = City.objects.get_or_create(name='Алматы', defaults={'country': country})
    
    storage, _ = Storage.objects.get_or_create(
        store=store,
        name='Основной склад',
        defaults={
            'city': city,
            'address': 'ул. Абая 150, Алматы'
        }
    )
    
    # Add stock for products
    for product in created_products:
        stock, created = Stock.objects.get_or_create(
            item=product,
            storage=storage,
            defaults={'amount': 50}  # 50 units in stock
        )
        if created:
            print(f"Added stock for {product.name}: {stock.amount}")
    
    # 7. Create task categories
    print("Creating task categories...")
    task_categories = [
        {'name': 'Обработка заказов', 'description': 'Задачи по обработке заказов клиентов', 'color': '#3B82F6'},
        {'name': 'Управление товарами', 'description': 'Задачи по добавлению и обновлению товаров', 'color': '#10B981'},
        {'name': 'Клиентская поддержка', 'description': 'Задачи по работе с клиентами', 'color': '#F59E0B'},
        {'name': 'Маркетинг', 'description': 'Маркетинговые задачи и акции', 'color': '#EF4444'},
    ]
    
    created_categories = []
    for cat_data in task_categories:
        category, created = TaskCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'color': cat_data['color']
            }
        )
        if created:
            print(f"Created task category: {category.name}")
        created_categories.append(category)
    
    # 8. Create test tasks
    print("Creating tasks...")
    tasks_data = [
        {
            'title': 'Обработать новые заказы',
            'description': 'Проверить и подтвердить заказы, поступившие за последние 24 часа',
            'priority': 'high',
            'status': 'pending',
            'category': created_categories[0],
            'due_date': timezone.now() + timedelta(hours=2)
        },
        {
            'title': 'Обновить описания товаров',
            'description': 'Добавить подробные описания для новых товаров в каталоге',
            'priority': 'medium',
            'status': 'in_progress',
            'category': created_categories[1],
            'due_date': timezone.now() + timedelta(days=3)
        },
        {
            'title': 'Ответить на отзывы клиентов',
            'description': 'Обработать новые отзывы и вопросы от покупателей',
            'priority': 'medium',
            'status': 'pending',
            'category': created_categories[2],
            'due_date': timezone.now() + timedelta(hours=6)
        },
        {
            'title': 'Подготовить акцию на выходные',
            'description': 'Создать рекламные материалы для скидочной акции',
            'priority': 'low',
            'status': 'completed',
            'category': created_categories[3],
            'due_date': timezone.now() + timedelta(days=7)
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
                'due_date': task_data['due_date']
            }
        )
        if created:
            print(f"Created task: {task.title}")
    
    # 9. Create test orders
    print("Creating test orders...")
    orders_data = [
        {
            'user': buyer,
            'status': 'pending',
            'comment': 'Срочный заказ, нужна быстрая доставка',
            'items': [
                {'product': created_products[0], 'amount': 1},  # iPhone
                {'product': created_products[3], 'amount': 2},  # T-shirts
            ]
        },
        {
            'user': buyer,
            'status': 'processing',
            'comment': 'Обычный заказ',
            'items': [
                {'product': created_products[1], 'amount': 1},  # Samsung
            ]
        },
        {
            'user': buyer,
            'status': 'delivered',
            'comment': 'Заказ выполнен отлично!',
            'items': [
                {'product': created_products[5], 'amount': 2},  # Coffee
                {'product': created_products[4], 'amount': 1},  # Jeans
            ]
        }
    ]
    
    for order_data in orders_data:
        order = Order.objects.create(
            user=order_data['user'],
            store=store,
            status=order_data['status'],
            comment=order_data['comment']
        )
        
        total_price = Decimal('0.00')
        for item_data in order_data['items']:
            product = item_data['product']
            amount = item_data['amount']
            price_per_item = product.default_price
            item_total = price_per_item * amount
            
            OrderItem.objects.create(
                order=order,
                item=product,
                amount=amount,
                price_per_item=price_per_item,
                total_price=item_total
            )
            
            total_price += item_total
        
        order.total_price = total_price
        order.save()
        print(f"Created order: {order.order_number} - {total_price} ₸")
    
    # 10. Create counterparty groups
    print("Creating counterparty groups...")
    vip_group, _ = CounterpartyGroup.objects.get_or_create(
        store=store,
        name='VIP клиенты',
        defaults={'description': 'Постоянные клиенты с особыми условиями'}
    )
    
    regular_group, _ = CounterpartyGroup.objects.get_or_create(
        store=store,
        name='Обычные клиенты',
        defaults={'description': 'Стандартные покупатели'}
    )
    
    # Add buyer to regular group
    CounterpartyMember.objects.get_or_create(
        user=buyer,
        counterparty_group=regular_group
    )
    
    print("✅ Test data creation completed successfully!")
    print("\nCreated:")
    print(f"- Users: {CustomUser.objects.count()}")
    print(f"- Stores: {Store.objects.count()}")
    print(f"- Products: {Item.objects.count()}")
    print(f"- Orders: {Order.objects.count()}")
    print(f"- Tasks: {Task.objects.count()}")
    print(f"- Task Categories: {TaskCategory.objects.count()}")
    print(f"- Counterparty Groups: {CounterpartyGroup.objects.count()}")
    
    print("\nLogin credentials:")
    print("Seller: seller@nexus.com / password123")
    print("Buyer: buyer@nexus.com / password123")
    print("Admin: admin / (set password via admin)")

if __name__ == '__main__':
    create_test_data()

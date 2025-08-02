#!/usr/bin/env python
"""
Script to create warehouse test data
Run with: python manage.py shell -c "exec(open('create_warehouse_data.py').read())"
"""

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from stores.models import Store, Item, Storage, Stock, Uom, Group
from users.models import CustomUser

def create_warehouse_data():
    print("Creating warehouse test data...")
    
    # 1. Создаем или получаем пользователя
    try:
        user = CustomUser.objects.get(username='seller')
        print(f"Found existing user: {user.username}")
    except CustomUser.DoesNotExist:
        user = CustomUser.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='password123'
        )
        print(f"Created new user: {user.username}")
    
    # 2. Создаем или получаем магазин
    store, created = Store.objects.get_or_create(
        name='Test Store',
        defaults={
            'description': 'Test store for warehouse management',
            'email': 'store@example.com',
            'phone': '+7 777 123 4567',
            'owner': user
        }
    )
    if created:
        print(f"Created store: {store.name}")
    else:
        print(f"Found existing store: {store.name}")
    
    # 3. Создаем склады
    storages_data = [
        {'name': 'Основной склад', 'description': 'Главный склад магазина'},
        {'name': 'Резервный склад', 'description': 'Дополнительный склад'},
        {'name': 'Холодильная камера', 'description': 'Склад для охлажденных товаров'},
        {'name': 'Торговый зал', 'description': 'Товары в торговом зале'}
    ]
    
    storages = []
    for storage_data in storages_data:
        storage, created = Storage.objects.get_or_create(
            name=storage_data['name'],
            store=store,
            defaults={
                'description': storage_data['description'],
                'address': f"Адрес {storage_data['name']}"
            }
        )
        storages.append(storage)
        if created:
            print(f"Created storage: {storage.name}")
        else:
            print(f"Found existing storage: {storage.name}")
    
    # 4. Создаем единицы измерения
    uoms_data = [
        {'name': 'шт', 'description': 'Штуки'},
        {'name': 'кг', 'description': 'Килограммы'},
        {'name': 'л', 'description': 'Литры'},
        {'name': 'м', 'description': 'Метры'}
    ]
    
    uoms = {}
    for uom_data in uoms_data:
        uom, created = Uom.objects.get_or_create(
            name=uom_data['name'],
            defaults={'description': uom_data['description']}
        )
        uoms[uom.name] = uom
        if created:
            print(f"Created UOM: {uom.name}")
    
    # 5. Создаем группы товаров
    groups_data = [
        {'name': 'Электроника', 'description': 'Электронные устройства'},
        {'name': 'Продукты', 'description': 'Продукты питания'},
        {'name': 'Одежда', 'description': 'Одежда и аксессуары'},
        {'name': 'Книги', 'description': 'Книги и печатные издания'}
    ]
    
    groups = {}
    for group_data in groups_data:
        group, created = Group.objects.get_or_create(
            name=group_data['name'],
            store=store,
            defaults={'description': group_data['description']}
        )
        groups[group.name] = group
        if created:
            print(f"Created group: {group.name}")
    
    # 6. Создаем товары с остатками
    items_data = [
        {
            'name': 'MacBook Pro 16"',
            'description': 'Ноутбук Apple MacBook Pro 16 дюймов',
            'price': Decimal('2000.00'),
            'group': 'Электроника',
            'uom': 'шт',
            'stocks': [
                {'storage': 'Основной склад', 'amount': 10},
                {'storage': 'Резервный склад', 'amount': 5}
            ]
        },
        {
            'name': 'iPhone 15 Pro',
            'description': 'Смартфон Apple iPhone 15 Pro',
            'price': Decimal('1500.00'),
            'group': 'Электроника',
            'uom': 'шт',
            'stocks': [
                {'storage': 'Основной склад', 'amount': 8}
            ]
        },
        {
            'name': 'Молоко 3.2%',
            'description': 'Молоко пастеризованное 3.2% жирности',
            'price': Decimal('500.00'),
            'group': 'Продукты',
            'uom': 'л',
            'stocks': [
                {'storage': 'Холодильная камера', 'amount': 50}
            ]
        },
        {
            'name': 'Хлеб белый',
            'description': 'Хлеб пшеничный белый',
            'price': Decimal('200.00'),
            'group': 'Продукты',
            'uom': 'шт',
            'stocks': [
                {'storage': 'Основной склад', 'amount': 20},
                {'storage': 'Торговый зал', 'amount': 5}
            ]
        },
        {
            'name': 'Футболка хлопковая',
            'description': 'Футболка из 100% хлопка',
            'price': Decimal('1000.00'),
            'group': 'Одежда',
            'uom': 'шт',
            'stocks': [
                {'storage': 'Основной склад', 'amount': 15}
            ]
        },
        {
            'name': 'Книга "Python для начинающих"',
            'description': 'Учебник по программированию на Python',
            'price': Decimal('750.00'),
            'group': 'Книги',
            'uom': 'шт',
            'stocks': [
                {'storage': 'Основной склад', 'amount': 3}
            ]
        }
    ]
    
    for item_data in items_data:
        # Создаем товар
        item, created = Item.objects.get_or_create(
            name=item_data['name'],
            store=store,
            defaults={
                'description': item_data['description'],
                'default_price': item_data['price'],
                'group': groups[item_data['group']],
                'uom': uoms[item_data['uom']],
                'status': True
            }
        )
        
        if created:
            print(f"Created item: {item.name}")
        else:
            print(f"Found existing item: {item.name}")
            # Обновляем цену если товар уже существует
            item.default_price = item_data['price']
            item.save()
        
        # Создаем остатки на складах
        for stock_data in item_data['stocks']:
            storage = next(s for s in storages if s.name == stock_data['storage'])
            stock, created = Stock.objects.get_or_create(
                item=item,
                storage=storage,
                defaults={'amount': stock_data['amount']}
            )
            
            if created:
                print(f"Created stock: {item.name} -> {storage.name}: {stock.amount}")
            else:
                # Обновляем количество если остаток уже существует
                stock.amount = stock_data['amount']
                stock.save()
                print(f"Updated stock: {item.name} -> {storage.name}: {stock.amount}")
    
    print("\nWarehouse test data creation completed!")
    print(f"Created/updated {Item.objects.filter(store=store).count()} items")
    print(f"Created/updated {Stock.objects.filter(storage__store=store).count()} stock records")

if __name__ == '__main__':
    create_warehouse_data()

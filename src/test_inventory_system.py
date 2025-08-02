#!/usr/bin/env python
"""
Test script for inventory management system
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from stores.models import Store, Item, Storage, Stock, Enter, WriteOff, InventoryCheck
from users.models import CustomUser

def test_inventory_system():
    """Test the complete inventory management system"""
    
    print("🧪 Testing Inventory Management System...")
    print("=" * 50)
    
    # Get first user and their store
    try:
        user = CustomUser.objects.first()
        if not user:
            print("❌ No users found. Please register a user first.")
            return
            
        store = Store.objects.filter(owner=user).first()
        if not store:
            print("❌ No store found for user. Please create a store.")
            return
            
        print(f"✅ Testing with user: {user.email}")
        print(f"✅ Testing with store: {store.name}")
        
        # Check items
        items = Item.objects.filter(store=store)
        print(f"📦 Items in store: {items.count()}")
        for item in items:
            print(f"   - {item.name} (ID: {item.id})")
        
        # Check storages
        storages = Storage.objects.filter(store=store)
        print(f"🏪 Storages in store: {storages.count()}")
        for storage in storages:
            print(f"   - {storage.name} (ID: {storage.id})")
        
        # Check stock records
        stocks = Stock.objects.filter(item__store=store)
        print(f"📊 Stock records: {stocks.count()}")
        for stock in stocks:
            print(f"   - {stock.item.name}: {stock.amount} {stock.item.uom.name if stock.item.uom else 'шт.'}")
        
        # Check stock registrations (Enter)
        enters = Enter.objects.filter(item__store=store)
        print(f"📥 Stock registrations: {enters.count()}")
        for enter in enters:
            print(f"   - {enter.item.name}: +{enter.amount} ({enter.created_at.strftime('%Y-%m-%d')})")
        
        # Check write-offs
        writeoffs = WriteOff.objects.filter(item__store=store)
        print(f"📤 Write-offs: {writeoffs.count()}")
        for writeoff in writeoffs:
            print(f"   - {writeoff.item.name}: -{writeoff.amount} ({writeoff.created_at.strftime('%Y-%m-%d')})")
        
        # Check inventory checks
        checks = InventoryCheck.objects.filter(store=store)
        print(f"📋 Inventory checks: {checks.count()}")
        for check in checks:
            print(f"   - {check.name} ({check.created_at.strftime('%Y-%m-%d')})")
        
        print("=" * 50)
        
        # Test creating sample stock registration if we have items and storages
        if items.exists() and storages.exists():
            print("🧪 Testing stock registration creation...")
            
            item = items.first()
            storage = storages.first()
            
            # Create test stock registration
            enter = Enter.objects.create(
                item=item,
                storage=storage,
                amount=10,
                document_number="TEST-001",
                supplier="Test Supplier",
                notes="Test stock registration"
            )
            
            print(f"✅ Created stock registration: {enter.item.name} +{enter.amount}")
            
            # Check if stock was updated
            stock = Stock.objects.filter(item=item, storage=storage).first()
            if stock:
                print(f"✅ Stock updated: {stock.item.name} = {stock.amount}")
            else:
                print("❌ Stock not created")
        
        print("✅ Inventory system test completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inventory_system()

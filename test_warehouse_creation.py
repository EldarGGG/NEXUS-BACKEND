#!/usr/bin/env python3
import requests
import json

def test_warehouse_creation():
    """Test warehouse creation with authentication"""
    
    # Authentication data
    auth_data = {
        'username': '87767228165',
        'password': 'EldarGGG'
    }
    
    try:
        print("🔐 Authenticating user...")
        response = requests.post('http://localhost:8000/api/v1/auth/login/', json=auth_data)
        print(f"Auth response status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access')
            print(f"✅ Authentication successful!")
            print(f"Access token: {access_token[:50]}...")
            
            # Test warehouse creation
            print("\n🏭 Creating warehouse...")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            warehouse_data = {
                'name': 'Test Warehouse',
                'description': 'Test Description for warehouse',
                'address': 'Test Address, Almaty'
            }
            
            warehouse_response = requests.post(
                'http://localhost:8000/api/v1/warehouses/', 
                json=warehouse_data, 
                headers=headers
            )
            
            print(f"Warehouse creation status: {warehouse_response.status_code}")
            
            if warehouse_response.status_code == 201:
                warehouse_result = warehouse_response.json()
                print("✅ Warehouse created successfully!")
                print(f"Warehouse ID: {warehouse_result.get('id')}")
                print(f"Warehouse Name: {warehouse_result.get('name')}")
                print(f"Message: {warehouse_result.get('message')}")
            else:
                print("❌ Warehouse creation failed!")
                print(f"Error response: {warehouse_response.text}")
                
        else:
            print("❌ Authentication failed!")
            print(f"Error response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the backend server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_warehouse_creation()

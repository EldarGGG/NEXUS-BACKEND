#!/usr/bin/env python3
"""
Test script for Tasks API
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/auth/login/"
TASKS_URL = f"{BASE_URL}/seller/tasks/"

# Test user credentials
PHONE = "87767228165"
PASSWORD = "123"

def test_tasks_api():
    print("🧪 Testing Tasks API...")
    
    # Step 1: Login
    print("🔐 Authenticating user...")
    login_data = {
        "phone": PHONE,
        "password": PASSWORD
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    print(f"Auth response status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Authentication failed!")
        print(f"Error response: {response.text}")
        return
    
    # Get auth token
    auth_data = response.json()
    token = auth_data.get('access_token')
    if not token:
        print("❌ No access token received!")
        return
    
    print("✅ Authentication successful!")
    
    # Headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get existing tasks
    print("\n📋 Getting existing tasks...")
    response = requests.get(TASKS_URL, headers=headers)
    print(f"Get tasks response status: {response.status_code}")
    
    if response.status_code == 200:
        tasks = response.json()
        print(f"✅ Found {len(tasks)} existing tasks")
        for task in tasks:
            print(f"  - Task {task['id']}: {task['title']} ({task['status']})")
    else:
        print(f"❌ Failed to get tasks: {response.text}")
        return
    
    # Step 3: Create a new task
    print("\n➕ Creating new task...")
    new_task_data = {
        "title": "Тестовая задача API",
        "description": "Задача создана через API тест",
        "priority": "medium",
        "status": "pending"
    }
    
    response = requests.post(TASKS_URL, json=new_task_data, headers=headers)
    print(f"Create task response status: {response.status_code}")
    
    if response.status_code == 201:
        created_task = response.json()
        print(f"✅ Task created successfully!")
        print(f"  - ID: {created_task['id']}")
        print(f"  - Title: {created_task['title']}")
        print(f"  - Status: {created_task['status']}")
        
        task_id = created_task['id']
        
        # Step 4: Update the task
        print(f"\n✏️ Updating task {task_id}...")
        update_data = {
            "status": "in_progress",
            "description": "Обновленное описание задачи"
        }
        
        response = requests.put(f"{TASKS_URL}{task_id}/", json=update_data, headers=headers)
        print(f"Update task response status: {response.status_code}")
        
        if response.status_code == 200:
            updated_task = response.json()
            print(f"✅ Task updated successfully!")
            print(f"  - Status: {updated_task['status']}")
            print(f"  - Description: {updated_task['description']}")
        else:
            print(f"❌ Failed to update task: {response.text}")
        
        # Step 5: Get tasks again to verify persistence
        print(f"\n🔍 Verifying task persistence...")
        response = requests.get(TASKS_URL, headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            found_task = next((t for t in tasks if t['id'] == task_id), None)
            if found_task:
                print(f"✅ Task {task_id} found in database!")
                print(f"  - Title: {found_task['title']}")
                print(f"  - Status: {found_task['status']}")
            else:
                print(f"❌ Task {task_id} not found in database!")
        
        # Step 6: Delete the test task
        print(f"\n🗑️ Deleting test task {task_id}...")
        response = requests.delete(f"{TASKS_URL}{task_id}/", headers=headers)
        print(f"Delete task response status: {response.status_code}")
        
        if response.status_code == 204:
            print(f"✅ Task deleted successfully!")
        else:
            print(f"❌ Failed to delete task: {response.text}")
        
    else:
        print(f"❌ Failed to create task: {response.text}")
    
    print("\n🎉 Tasks API test completed!")

if __name__ == "__main__":
    test_tasks_api()

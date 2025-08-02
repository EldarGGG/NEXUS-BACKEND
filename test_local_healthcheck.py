#!/usr/bin/env python3
"""
Simple local healthcheck test without Docker
"""
import os
import sys
import django
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
django.setup()

# Now we can import Django modules
from django.test import Client
from django.urls import reverse

def test_healthcheck():
    """Test healthcheck endpoint locally"""
    client = Client()
    
    try:
        # Test healthcheck endpoint
        response = client.get('/api/v1/health/')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        
        if response.status_code == 200:
            print("✅ Healthcheck passed!")
            return True
        else:
            print("❌ Healthcheck failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing healthcheck: {e}")
        return False

if __name__ == "__main__":
    success = test_healthcheck()
    sys.exit(0 if success else 1) 
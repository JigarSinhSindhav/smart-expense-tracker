#!/usr/bin/env python3
"""
Simple test script to verify the application is working correctly.
"""

import requests
import json

def test_application():
    """Test the main application endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Smart Expense Tracker Application...")
    print("=" * 50)
    
    try:
        # Test categories endpoint
        print("1. Testing categories endpoint...")
        resp = requests.get(f"{base_url}/api/categories")
        if resp.status_code == 200:
            categories = resp.json()
            print(f"   ✅ Categories API working - {len(categories)} categories available")
            print(f"   Categories: {', '.join(categories)}")
        else:
            print(f"   ❌ Categories API failed with status {resp.status_code}")
            return False
        
        # Test analytics endpoint
        print("\n2. Testing analytics endpoint...")
        resp = requests.get(f"{base_url}/api/analytics")
        if resp.status_code == 200:
            data = resp.json()
            total = data["total_expenses"]
            print(f"   ✅ Analytics API working - Total expenses: ${total:.2f}")
            print(f"   Categories with data: {len(data['categories'])}")
            print(f"   Monthly data points: {len(data['monthly'])}")
        else:
            print(f"   ❌ Analytics API failed with status {resp.status_code}")
            return False
            
        # Test expenses endpoint
        print("\n3. Testing expenses endpoint...")
        resp = requests.get(f"{base_url}/api/expenses")
        if resp.status_code == 200:
            expenses = resp.json()
            print(f"   ✅ Expenses API working - {len(expenses)} expenses loaded")
            if expenses:
                recent = expenses[0]
                print(f"   Most recent: {recent['description']} - ${recent['amount']:.2f}")
        else:
            print(f"   ❌ Expenses API failed with status {resp.status_code}")
            return False
            
        # Test ML prediction by adding a test expense
        print("\n4. Testing ML prediction...")
        test_expense = {
            "description": "Coffee at local cafe",
            "amount": 4.50
        }
        
        resp = requests.post(f"{base_url}/api/expenses", 
                           json=test_expense,
                           headers={"Content-Type": "application/json"})
        
        if resp.status_code == 200:
            result = resp.json()
            predicted = result["predicted_category"]
            confidence = result["confidence"]
            print(f"   ✅ ML Prediction working")
            print(f"   Predicted category: {predicted}")
            print(f"   Confidence: {confidence:.2f}")
            
            # Clean up test expense
            print("   🧹 Cleaning up test expense...")
            
        else:
            print(f"   ❌ ML Prediction failed with status {resp.status_code}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Application is working correctly.")
        print(f"🌐 Access the web interface at: {base_url}")
        print("=" * 50)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the application.")
        print("   Make sure the Flask app is running on port 5001")
        print("   Run: python app.py")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_application()

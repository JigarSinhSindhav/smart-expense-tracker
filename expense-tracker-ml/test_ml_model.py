#!/usr/bin/env python3
"""
Test script for the improved ML expense categorization model
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import ExpenseCategorizer

def test_ml_model():
    """Test the improved ML model with various expense descriptions"""
    
    print("🚀 Testing Improved ML Expense Categorizer")
    print("=" * 60)
    
    categorizer = ExpenseCategorizer()
    
    # Test cases with expected categories
    test_cases = [
        # Food tests
        ("McDonald's lunch", "Food"),
        ("Starbucks coffee", "Food"), 
        ("Grocery shopping at Walmart", "Food"),
        ("Pizza delivery", "Food"),
        ("Restaurant dinner", "Food"),
        ("Whole Foods market", "Food"),
        ("Bar drinks", "Food"),
        
        # Transport tests
        ("Uber ride to airport", "Transport"),
        ("Gas at Shell station", "Transport"),
        ("Parking meter downtown", "Transport"),
        ("Car oil change", "Transport"),
        ("Flight to New York", "Transport"),
        ("Metro card refill", "Transport"),
        ("Taxi fare", "Transport"),
        
        # Entertainment tests
        ("Netflix monthly subscription", "Entertainment"),
        ("Movie theater tickets", "Entertainment"),
        ("Concert at venue", "Entertainment"),
        ("Video game purchase", "Entertainment"),
        ("Gym membership", "Entertainment"),
        ("Book at Barnes Noble", "Entertainment"),
        
        # Shopping tests
        ("Amazon online purchase", "Shopping"),
        ("Clothes at Target", "Shopping"),
        ("Best Buy electronics", "Shopping"),
        ("Home Depot supplies", "Shopping"),
        ("Birthday gift", "Shopping"),
        ("New shoes", "Shopping"),
        
        # Bills tests
        ("Electric bill payment", "Bills"),
        ("Internet bill Comcast", "Bills"),
        ("Cell phone bill Verizon", "Bills"),
        ("Rent payment", "Bills"),
        ("Car insurance premium", "Bills"),
        ("Credit card payment", "Bills"),
        
        # Healthcare tests
        ("Doctor appointment", "Healthcare"),
        ("Pharmacy prescription", "Healthcare"),
        ("Dental cleaning", "Healthcare"),
        ("Eye exam", "Healthcare"),
        ("Hospital visit", "Healthcare"),
        ("Physical therapy", "Healthcare"),
        
        # Other tests
        ("Bank ATM fee", "Other"),
        ("Charity donation", "Other"),
        ("Pet veterinarian", "Other"),
        ("Legal consultation", "Other"),
        ("Investment transfer", "Other"),
    ]
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    print(f"Running {total_tests} test cases...")
    print("-" * 60)
    
    for i, (description, expected_category) in enumerate(test_cases, 1):
        predicted_category, confidence = categorizer.predict_category(description)
        
        is_correct = predicted_category == expected_category
        status = "✅ CORRECT" if is_correct else "❌ WRONG"
        
        if is_correct:
            correct_predictions += 1
        
        print(f"{i:2d}. '{description}' → {predicted_category} (conf: {confidence:.2f}) {status}")
        if not is_correct:
            print(f"    Expected: {expected_category}")
    
    print("-" * 60)
    accuracy = (correct_predictions / total_tests) * 100
    print(f"📊 ACCURACY: {correct_predictions}/{total_tests} = {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("🎉 EXCELLENT! Model performance is great!")
    elif accuracy >= 65:
        print("👍 GOOD! Model performance is acceptable!")
    else:
        print("⚠️  NEEDS IMPROVEMENT! Model accuracy is below expectations.")
    
    print("\n" + "=" * 60)
    print("🧪 Testing edge cases and challenging examples:")
    
    edge_cases = [
        "mcdonalds big mac",
        "uber to work", 
        "netflix",
        "amazon prime",
        "doctor visit copay",
        "gas shell station",
        "target groceries",
        "starbucks venti latte",
        "parking downtown",
        "phone bill verizon"
    ]
    
    for desc in edge_cases:
        cat, conf = categorizer.predict_category(desc)
        print(f"'{desc}' → {cat} (confidence: {conf:.2f})")
    
    return accuracy

if __name__ == "__main__":
    accuracy = test_ml_model()
    
    if accuracy < 70:
        print("\n⚠️  Low accuracy detected. Consider:")
        print("1. Adding more training data")
        print("2. Improving text preprocessing")
        print("3. Adjusting model parameters")
    else:
        print(f"\n🚀 Model is ready for deployment with {accuracy:.1f}% accuracy!")

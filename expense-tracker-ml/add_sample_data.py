#!/usr/bin/env python3
"""
Sample data generation script for the Expense Tracker ML application.
This creates realistic sample expenses to demonstrate the application functionality.
"""

import sqlite3
import random
from datetime import datetime, timedelta

# Sample expense data
SAMPLE_EXPENSES = [
    # Food expenses
    ("Starbucks coffee and pastry", 12.50, "Food"),
    ("McDonald's lunch meal", 8.99, "Food"),
    ("Grocery shopping at Whole Foods", 125.67, "Food"),
    ("Pizza delivery from Domino's", 24.75, "Food"),
    ("Breakfast at local cafe", 15.30, "Food"),
    ("Subway sandwich", 7.50, "Food"),
    ("Restaurant dinner with friends", 45.80, "Food"),
    ("Ice cream truck", 4.50, "Food"),
    ("Sushi takeout", 32.90, "Food"),
    ("Coffee beans from local roaster", 18.95, "Food"),
    
    # Transport expenses
    ("Uber ride to downtown", 18.75, "Transport"),
    ("Gas station fill-up", 52.30, "Transport"),
    ("Metro bus monthly pass", 85.00, "Transport"),
    ("Parking downtown", 12.00, "Transport"),
    ("Taxi to airport", 45.50, "Transport"),
    ("Car maintenance oil change", 75.99, "Transport"),
    ("Lyft ride home", 22.15, "Transport"),
    ("Train ticket to New York", 89.00, "Transport"),
    ("Parking meter", 3.50, "Transport"),
    ("Uber Eats delivery fee", 4.99, "Transport"),
    
    # Entertainment expenses
    ("Movie theater tickets", 28.50, "Entertainment"),
    ("Netflix monthly subscription", 15.99, "Entertainment"),
    ("Concert tickets", 125.00, "Entertainment"),
    ("Spotify Premium subscription", 9.99, "Entertainment"),
    ("Book from Amazon", 24.99, "Entertainment"),
    ("Gaming purchase on Steam", 39.99, "Entertainment"),
    ("Museum entrance fee", 20.00, "Entertainment"),
    ("Streaming service subscription", 12.99, "Entertainment"),
    ("Board game purchase", 34.95, "Entertainment"),
    ("Comedy show tickets", 45.00, "Entertainment"),
    
    # Shopping expenses
    ("New shirt from Target", 19.99, "Shopping"),
    ("Amazon Prime purchase", 67.45, "Shopping"),
    ("Electronics store headphones", 89.99, "Shopping"),
    ("Home Depot garden supplies", 43.20, "Shopping"),
    ("Pharmacy toiletries", 28.75, "Shopping"),
    ("Gift for friend's birthday", 55.00, "Shopping"),
    ("New running shoes", 120.00, "Shopping"),
    ("Office supplies", 23.45, "Shopping"),
    ("Kitchen utensils", 35.60, "Shopping"),
    ("Phone case replacement", 15.99, "Shopping"),
    
    # Bills expenses
    ("Electric bill payment", 145.67, "Bills"),
    ("Internet service provider", 79.99, "Bills"),
    ("Mobile phone bill", 65.00, "Bills"),
    ("Rent payment", 1200.00, "Bills"),
    ("Car insurance premium", 178.50, "Bills"),
    ("Water utility bill", 67.34, "Bills"),
    ("Credit card payment", 450.00, "Bills"),
    ("Gym membership monthly", 49.99, "Bills"),
    ("Storage unit rental", 95.00, "Bills"),
    ("Home insurance", 125.00, "Bills"),
    
    # Healthcare expenses
    ("Doctor visit co-pay", 35.00, "Healthcare"),
    ("Prescription medication", 25.99, "Healthcare"),
    ("Dental cleaning", 150.00, "Healthcare"),
    ("Eye exam", 125.00, "Healthcare"),
    ("Physical therapy session", 85.00, "Healthcare"),
    ("Pharmacy vitamins", 18.50, "Healthcare"),
    ("Urgent care visit", 200.00, "Healthcare"),
    ("Health insurance premium", 320.00, "Healthcare"),
    
    # Other expenses
    ("Bank ATM fee", 3.50, "Other"),
    ("Charity donation", 50.00, "Other"),
    ("Software subscription", 29.99, "Other"),
    ("Dry cleaning", 15.75, "Other"),
    ("Pet grooming", 65.00, "Other"),
    ("Professional development course", 99.00, "Other"),
    ("Tax preparation service", 200.00, "Other"),
    ("Legal consultation", 150.00, "Other")
]

def add_sample_data():
    """Add sample expenses to the database with realistic dates"""
    
    # Initialize database
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    # Create tables (in case they don't exist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            predicted_category TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_corrected BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Clear existing sample data (optional)
    print("Clearing existing data...")
    cursor.execute('DELETE FROM expenses')
    
    # Add sample expenses with random dates over the past 90 days
    print("Adding sample expenses...")
    
    base_date = datetime.now()
    
    for i, (description, amount, category) in enumerate(SAMPLE_EXPENSES):
        # Generate a random date within the last 90 days
        days_ago = random.randint(0, 90)
        expense_date = base_date - timedelta(days=days_ago)
        
        # Some expenses will be "predicted" (no user correction)
        # Some will be "user corrected" to simulate learning
        user_corrected = random.choice([True, False, False, False])  # 25% chance of correction
        
        if user_corrected:
            # Simulate incorrect prediction that user corrected
            wrong_categories = [cat for cat in ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Other'] if cat != category]
            predicted_category = random.choice(wrong_categories)
        else:
            # Correct prediction
            predicted_category = category
        
        cursor.execute('''
            INSERT INTO expenses (description, amount, category, predicted_category, date, user_corrected)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (description, amount, category, predicted_category, expense_date.isoformat(), user_corrected))
        
        print(f"Added: {description} - ${amount} ({category})")
    
    # Add some sample budgets
    print("\nAdding sample budgets...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            budget_amount REAL NOT NULL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    sample_budgets = [
        ('Food', 500.00),
        ('Transport', 200.00),
        ('Entertainment', 150.00),
        ('Shopping', 300.00),
        ('Bills', 2000.00),
        ('Healthcare', 200.00),
        ('Other', 100.00)
    ]
    
    for category, budget in sample_budgets:
        cursor.execute('''
            INSERT OR REPLACE INTO budgets (category, budget_amount)
            VALUES (?, ?)
        ''', (category, budget))
        print(f"Budget set: {category} - ${budget}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully added {len(SAMPLE_EXPENSES)} sample expenses!")
    print("✅ Sample budgets configured!")
    print("\n🚀 Your expense tracker is ready with realistic sample data!")
    
    # Display some stats
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM expenses')
    total_expenses = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(amount) FROM expenses')
    total_amount = cursor.fetchone()[0]
    
    cursor.execute('SELECT category, COUNT(*) FROM expenses GROUP BY category')
    category_counts = cursor.fetchall()
    
    print(f"\n📊 Database Statistics:")
    print(f"   Total Expenses: {total_expenses}")
    print(f"   Total Amount: ${total_amount:.2f}")
    print(f"   Categories:")
    for category, count in category_counts:
        print(f"     - {category}: {count} expenses")
    
    conn.close()

if __name__ == "__main__":
    add_sample_data()

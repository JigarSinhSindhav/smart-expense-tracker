from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import sqlite3
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
import re
import pickle
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Database setup
DATABASE = 'expenses.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create expenses table
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
    
    # Create budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT UNIQUE NOT NULL,
            budget_amount REAL NOT NULL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

class ExpenseCategorizer:
    def __init__(self):
        self.model = None
        self.categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills', 'Healthcare', 'Other']
        self.model_path = 'models/expense_model.pkl'
        
    def preprocess_text(self, text):
        """Enhanced text preprocessing"""
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Common replacements to standardize terms - much more comprehensive
        replacements = {
            # Food related
            'mcdonalds': 'fast food restaurant', 'mcdonald': 'fast food restaurant',
            'kfc': 'fast food restaurant', 'burger king': 'fast food restaurant',
            'taco bell': 'fast food restaurant', 'chipotle': 'fast food restaurant',
            'subway sandwich': 'fast food restaurant', 'pizza hut': 'pizza restaurant',
            'dominos': 'pizza restaurant', 'domino': 'pizza restaurant',
            'starbucks': 'coffee shop', 'dunkin': 'coffee shop', 'tim hortons': 'coffee shop',
            'walmart grocery': 'grocery store', 'target grocery': 'grocery store',
            'whole foods': 'grocery store', 'trader joe': 'grocery store',
            'kroger': 'grocery store', 'safeway': 'grocery store',
            'restaurant': 'restaurant meal', 'bar': 'bar drinks',
            
            # Transport related
            'uber': 'rideshare transport', 'lyft': 'rideshare transport',
            'taxi': 'taxi transport', 'cab': 'taxi transport',
            'shell': 'gas station fuel', 'bp': 'gas station fuel',
            'exxon': 'gas station fuel', 'chevron': 'gas station fuel',
            'parking': 'parking fee', 'metro': 'public transport',
            'subway card': 'public transport', 'bus': 'public transport',
            'flight': 'airline transport', 'airline': 'airline transport',
            
            # Shopping related
            'amazon': 'online shopping', 'ebay': 'online shopping',
            'target shopping': 'retail shopping', 'walmart shopping': 'retail shopping',
            'best buy': 'electronics shopping', 'apple store': 'electronics shopping',
            'home depot': 'hardware shopping', 'lowes': 'hardware shopping',
            'cvs': 'pharmacy shopping', 'walgreens': 'pharmacy shopping',
            'costco': 'wholesale shopping', 'ikea': 'furniture shopping',
            
            # Entertainment related
            'netflix': 'streaming entertainment', 'hulu': 'streaming entertainment',
            'disney plus': 'streaming entertainment', 'spotify': 'music streaming',
            'youtube premium': 'streaming entertainment', 'movie': 'movie entertainment',
            'cinema': 'movie entertainment', 'concert': 'music entertainment',
            'gym': 'fitness entertainment', 'gaming': 'video game entertainment',
            
            # Bills related
            'electric': 'electricity bill', 'internet': 'internet bill',
            'wifi': 'internet bill', 'phone': 'phone bill', 'cell': 'phone bill',
            'rent': 'rent payment', 'mortgage': 'mortgage payment',
            'insurance': 'insurance payment', 'utility': 'utility bill',
            
            # Healthcare related
            'doctor': 'medical healthcare', 'physician': 'medical healthcare',
            'hospital': 'medical healthcare', 'pharmacy': 'prescription healthcare',
            'dental': 'dental healthcare', 'dentist': 'dental healthcare',
            'medical': 'medical healthcare', 'health': 'medical healthcare'
        }
        
        for key, value in replacements.items():
            if key in text:
                text = text.replace(key, value)
                
        return text
        
    def prepare_initial_data(self):
        """Create comprehensive initial training data"""
        training_data = [
            # Food - much more comprehensive
            ('restaurant dinner', 'Food'), ('coffee shop', 'Food'), ('grocery store', 'Food'),
            ('pizza delivery', 'Food'), ('lunch meeting', 'Food'), ('breakfast cafe', 'Food'),
            ('fast food', 'Food'), ('supermarket', 'Food'), ('food truck', 'Food'),
            ('mcdonalds', 'Food'), ('burger king', 'Food'), ('kfc', 'Food'), ('subway sandwich', 'Food'),
            ('taco bell', 'Food'), ('chipotle', 'Food'), ('pizza hut', 'Food'), ('dominos', 'Food'),
            ('starbucks', 'Food'), ('dunkin donuts', 'Food'), ('tim hortons', 'Food'),
            ('walmart grocery', 'Food'), ('target grocery', 'Food'), ('whole foods', 'Food'),
            ('trader joes', 'Food'), ('kroger', 'Food'), ('safeway', 'Food'),
            ('restaurant bill', 'Food'), ('dinner out', 'Food'), ('lunch out', 'Food'),
            ('breakfast out', 'Food'), ('takeout', 'Food'), ('food delivery', 'Food'),
            ('groceries', 'Food'), ('snacks', 'Food'), ('drinks', 'Food'), ('alcohol', 'Food'),
            ('bar tab', 'Food'), ('wine', 'Food'), ('beer', 'Food'), ('coffee', 'Food'),
            ('lunch with friends', 'Food'), ('dinner date', 'Food'), ('brunch', 'Food'),
            ('ice cream', 'Food'), ('candy', 'Food'), ('chocolates', 'Food'), ('bakery', 'Food'),
            ('deli sandwich', 'Food'), ('sushi restaurant', 'Food'), ('chinese food', 'Food'),
            ('mexican food', 'Food'), ('italian restaurant', 'Food'), ('thai food', 'Food'),
            ('indian restaurant', 'Food'), ('japanese cuisine', 'Food'), ('fast casual', 'Food'),
            ('food court', 'Food'), ('catering', 'Food'), ('birthday cake', 'Food'),
            ('party food', 'Food'), ('wedding catering', 'Food'), ('office lunch', 'Food'),
            
            # Transport - comprehensive
            ('uber ride', 'Transport'), ('lyft ride', 'Transport'), ('taxi fare', 'Transport'),
            ('gas station', 'Transport'), ('fuel', 'Transport'), ('gasoline', 'Transport'),
            ('bus ticket', 'Transport'), ('train ticket', 'Transport'), ('subway card', 'Transport'),
            ('metro card', 'Transport'), ('parking fee', 'Transport'), ('parking meter', 'Transport'),
            ('car maintenance', 'Transport'), ('oil change', 'Transport'), ('car repair', 'Transport'),
            ('flight booking', 'Transport'), ('airline ticket', 'Transport'), ('airport parking', 'Transport'),
            ('rental car', 'Transport'), ('car rental', 'Transport'), ('toll road', 'Transport'),
            ('car insurance', 'Transport'), ('auto insurance', 'Transport'), ('vehicle registration', 'Transport'),
            ('dmv fee', 'Transport'), ('car wash', 'Transport'), ('tires', 'Transport'),
            ('mechanic', 'Transport'), ('garage', 'Transport'), ('shell gas', 'Transport'),
            ('bp gas', 'Transport'), ('exxon gas', 'Transport'), ('chevron gas', 'Transport'),
            
            # Entertainment - comprehensive
            ('movie theater', 'Entertainment'), ('cinema', 'Entertainment'), ('movie ticket', 'Entertainment'),
            ('concert ticket', 'Entertainment'), ('music concert', 'Entertainment'), ('festival', 'Entertainment'),
            ('netflix subscription', 'Entertainment'), ('spotify premium', 'Entertainment'), ('hulu', 'Entertainment'),
            ('disney plus', 'Entertainment'), ('amazon prime video', 'Entertainment'), ('youtube premium', 'Entertainment'),
            ('gaming purchase', 'Entertainment'), ('video game', 'Entertainment'), ('playstation', 'Entertainment'),
            ('xbox', 'Entertainment'), ('nintendo', 'Entertainment'), ('steam', 'Entertainment'),
            ('book store', 'Entertainment'), ('bookstore', 'Entertainment'), ('magazine', 'Entertainment'),
            ('newspaper', 'Entertainment'), ('sports event', 'Entertainment'), ('theater show', 'Entertainment'),
            ('comedy show', 'Entertainment'), ('amusement park', 'Entertainment'), ('zoo', 'Entertainment'),
            ('museum', 'Entertainment'), ('art gallery', 'Entertainment'), ('bowling', 'Entertainment'),
            ('mini golf', 'Entertainment'), ('arcade', 'Entertainment'), ('gym membership', 'Entertainment'),
            
            # Shopping - comprehensive
            ('clothing store', 'Shopping'), ('clothes shopping', 'Shopping'), ('fashion', 'Shopping'),
            ('amazon purchase', 'Shopping'), ('online shopping', 'Shopping'), ('ebay', 'Shopping'),
            ('electronics store', 'Shopping'), ('best buy', 'Shopping'), ('apple store', 'Shopping'),
            ('home depot', 'Shopping'), ('lowes', 'Shopping'), ('hardware store', 'Shopping'),
            ('target shopping', 'Shopping'), ('walmart shopping', 'Shopping'), ('costco', 'Shopping'),
            ('pharmacy items', 'Shopping'), ('cvs', 'Shopping'), ('walgreens', 'Shopping'),
            ('gift purchase', 'Shopping'), ('birthday gift', 'Shopping'), ('christmas gift', 'Shopping'),
            ('department store', 'Shopping'), ('mall shopping', 'Shopping'), ('shoes', 'Shopping'),
            ('jewelry', 'Shopping'), ('makeup', 'Shopping'), ('cosmetics', 'Shopping'),
            ('furniture', 'Shopping'), ('ikea', 'Shopping'), ('home goods', 'Shopping'),
            ('office supplies', 'Shopping'), ('stationery', 'Shopping'),
            
            # Bills - comprehensive
            ('electricity bill', 'Bills'), ('electric bill', 'Bills'), ('power bill', 'Bills'),
            ('internet bill', 'Bills'), ('wifi bill', 'Bills'), ('broadband', 'Bills'),
            ('phone bill', 'Bills'), ('cell phone bill', 'Bills'), ('mobile bill', 'Bills'),
            ('rent payment', 'Bills'), ('mortgage payment', 'Bills'), ('house payment', 'Bills'),
            ('insurance premium', 'Bills'), ('health insurance', 'Bills'), ('car insurance', 'Bills'),
            ('home insurance', 'Bills'), ('life insurance', 'Bills'), ('water bill', 'Bills'),
            ('gas bill', 'Bills'), ('heating bill', 'Bills'), ('cable bill', 'Bills'),
            ('credit card payment', 'Bills'), ('loan payment', 'Bills'), ('student loan', 'Bills'),
            ('mortgage', 'Bills'), ('property tax', 'Bills'), ('income tax', 'Bills'),
            ('utility bill', 'Bills'), ('hoa fee', 'Bills'), ('subscription', 'Bills'),
            
            # Healthcare - comprehensive
            ('doctor visit', 'Healthcare'), ('physician', 'Healthcare'), ('medical appointment', 'Healthcare'),
            ('hospital bill', 'Healthcare'), ('emergency room', 'Healthcare'), ('urgent care', 'Healthcare'),
            ('pharmacy prescription', 'Healthcare'), ('medication', 'Healthcare'), ('prescription', 'Healthcare'),
            ('dental checkup', 'Healthcare'), ('dentist', 'Healthcare'), ('dental cleaning', 'Healthcare'),
            ('eye exam', 'Healthcare'), ('optometrist', 'Healthcare'), ('glasses', 'Healthcare'),
            ('contact lenses', 'Healthcare'), ('physical therapy', 'Healthcare'), ('chiropractor', 'Healthcare'),
            ('medical test', 'Healthcare'), ('blood test', 'Healthcare'), ('x ray', 'Healthcare'),
            ('mri scan', 'Healthcare'), ('surgery', 'Healthcare'), ('medical procedure', 'Healthcare'),
            ('health checkup', 'Healthcare'), ('annual exam', 'Healthcare'), ('specialist', 'Healthcare'),
            
            # Other - comprehensive
            ('bank fee', 'Other'), ('atm fee', 'Other'), ('overdraft fee', 'Other'),
            ('donation', 'Other'), ('charity', 'Other'), ('gift', 'Other'),
            ('subscription service', 'Other'), ('membership fee', 'Other'), ('annual fee', 'Other'),
            ('pet care', 'Other'), ('veterinarian', 'Other'), ('pet food', 'Other'),
            ('childcare', 'Other'), ('babysitter', 'Other'), ('daycare', 'Other'),
            ('education', 'Other'), ('tuition', 'Other'), ('school supplies', 'Other'),
            ('legal fee', 'Other'), ('lawyer', 'Other'), ('attorney', 'Other'),
            ('investment', 'Other'), ('savings', 'Other'), ('retirement', 'Other'),
            ('transfer', 'Other'), ('cash withdrawal', 'Other'), ('miscellaneous', 'Other')
        ]
        return training_data
    
    def train_model(self, additional_data=None):
        """Train the categorization model with improved features"""
        # Get initial training data
        training_data = self.prepare_initial_data()
        
        # Add data from database if available
        if additional_data:
            training_data.extend(additional_data)
        
        # Preprocess descriptions
        descriptions = [self.preprocess_text(item[0]) for item in training_data]
        categories = [item[1] for item in training_data]
        
        # Create and train the model with better parameters
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=2000,
                lowercase=True,
                ngram_range=(1, 2),  # Use both unigrams and bigrams
                stop_words='english',
                min_df=1,
                max_df=0.95
            )),
            ('classifier', LogisticRegression(
                random_state=42,
                max_iter=1000,
                C=1.0,
                class_weight='balanced'  # Handle class imbalance
            ))
        ])
        
        self.model.fit(descriptions, categories)
        
        # Save the model
        os.makedirs('models', exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
    
    def load_model(self):
        """Load the trained model"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            return True
        except FileNotFoundError:
            return False
    
    def predict_category(self, description):
        """Predict category for a given description with improved accuracy"""
        if self.model is None:
            if not self.load_model():
                self.train_model()
        
        # Preprocess the input
        processed_description = self.preprocess_text(description)
        
        # Make prediction
        prediction = self.model.predict([processed_description])[0]
        probabilities = self.model.predict_proba([processed_description])[0]
        confidence = max(probabilities)
        
        # If confidence is too low, suggest 'Other' category
        if confidence < 0.3:
            return 'Other', confidence
        
        return prediction, confidence

# Initialize categorizer
categorizer = ExpenseCategorizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, description, amount, category, predicted_category, 
               date, user_corrected FROM expenses 
        ORDER BY date DESC
    ''')
    
    expenses = []
    for row in cursor.fetchall():
        expenses.append({
            'id': row[0],
            'description': row[1],
            'amount': row[2],
            'category': row[3],
            'predicted_category': row[4],
            'date': row[5],
            'user_corrected': row[6]
        })
    
    conn.close()
    return jsonify(expenses)

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    """Add a new expense"""
    data = request.json
    description = data.get('description', '')
    amount = float(data.get('amount', 0))
    user_category = data.get('category')
    
    # Predict category
    predicted_category, confidence = categorizer.predict_category(description)
    
    # Use user category if provided, otherwise use prediction
    final_category = user_category if user_category else predicted_category
    user_corrected = bool(user_category and user_category != predicted_category)
    
    # Save to database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO expenses (description, amount, category, predicted_category, user_corrected)
        VALUES (?, ?, ?, ?, ?)
    ''', (description, amount, final_category, predicted_category, user_corrected))
    
    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Retrain model if user corrected
    if user_corrected:
        retrain_model()
    
    return jsonify({
        'id': expense_id,
        'description': description,
        'amount': amount,
        'category': final_category,
        'predicted_category': predicted_category,
        'confidence': confidence,
        'user_corrected': user_corrected
    })

@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update an expense category"""
    data = request.json
    new_category = data.get('category')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current expense
    cursor.execute('SELECT predicted_category FROM expenses WHERE id = ?', (expense_id,))
    result = cursor.fetchone()
    
    if result:
        predicted_category = result[0]
        user_corrected = new_category != predicted_category
        
        cursor.execute('''
            UPDATE expenses 
            SET category = ?, user_corrected = ? 
            WHERE id = ?
        ''', (new_category, user_corrected, expense_id))
        
        conn.commit()
        
        if user_corrected:
            retrain_model()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all available categories"""
    return jsonify(categorizer.categories)

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get expense analytics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Category totals
    cursor.execute('''
        SELECT category, SUM(amount) as total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    ''')
    
    category_data = [{'category': row[0], 'total': row[1]} for row in cursor.fetchall()]
    
    # Monthly spending
    cursor.execute('''
        SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
        FROM expenses
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
        LIMIT 12
    ''')
    
    monthly_data = [{'month': row[0], 'total': row[1]} for row in cursor.fetchall()]
    
    # Recent expenses
    cursor.execute('''
        SELECT description, amount, category, date
        FROM expenses
        ORDER BY date DESC
        LIMIT 10
    ''')
    
    recent_expenses = []
    for row in cursor.fetchall():
        recent_expenses.append({
            'description': row[0],
            'amount': row[1],
            'category': row[2],
            'date': row[3]
        })
    
    conn.close()
    
    return jsonify({
        'categories': category_data,
        'monthly': monthly_data,
        'recent': recent_expenses,
        'total_expenses': sum(item['total'] for item in category_data)
    })

@app.route('/api/budgets', methods=['GET'])
def get_budgets():
    """Get all budgets"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT category, budget_amount FROM budgets')
    budgets = [{'category': row[0], 'budget': row[1]} for row in cursor.fetchall()]
    
    conn.close()
    return jsonify(budgets)

@app.route('/api/budgets', methods=['POST'])
def set_budget():
    """Set budget for a category"""
    data = request.json
    category = data.get('category')
    budget_amount = float(data.get('budget', 0))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO budgets (category, budget_amount)
        VALUES (?, ?)
    ''', (category, budget_amount))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

def retrain_model():
    """Retrain the model with corrected data"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT description, category FROM expenses 
        WHERE user_corrected = TRUE
    ''')
    
    corrected_data = [(row[0], row[1]) for row in cursor.fetchall()]
    conn.close()
    
    if corrected_data:
        categorizer.train_model(corrected_data)

if __name__ == '__main__':
    init_db()
    
    # Train initial model if it doesn't exist
    if not categorizer.load_model():
        categorizer.train_model()
    
    # Use PORT environment variable for Railway, fallback to 5001 for local
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)

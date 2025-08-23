from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.database import db
from ml_model.predictor import predictor

app = Flask(__name__, 
           static_folder='../static',
           template_folder='../frontend')
CORS(app)  # Enable CORS for frontend-backend communication

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict_category():
    """Predict category for expense description"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        
        if not description.strip():
            return jsonify({'error': 'Description is required'}), 400
        
        # Get prediction from ML model
        prediction = predictor.predict(description)
        
        return jsonify({
            'category': prediction['category'],
            'confidence': prediction['confidence'],
            'description': description
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    """Add a new expense"""
    try:
        data = request.get_json()
        
        # Validate required fields
        description = data.get('description', '').strip()
        amount = data.get('amount')
        category = data.get('category', '').strip()
        
        if not description:
            return jsonify({'error': 'Description is required'}), 400
        
        if not amount or amount <= 0:
            return jsonify({'error': 'Valid amount is required'}), 400
        
        if not category:
            return jsonify({'error': 'Category is required'}), 400
        
        # Get prediction for comparison
        prediction = predictor.predict(description)
        
        # Add expense to database
        expense_id = db.add_expense(
            description=description,
            amount=float(amount),
            category=category,
            predicted_category=prediction['category'],
            confidence=prediction['confidence'],
            notes=data.get('notes', '')
        )
        
        return jsonify({
            'id': expense_id,
            'message': 'Expense added successfully',
            'predicted_category': prediction['category'],
            'confidence': prediction['confidence']
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses"""
    try:
        expenses = db.get_all_expenses()
        return jsonify(expenses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense"""
    try:
        success = db.delete_expense(expense_id)
        if success:
            return jsonify({'message': 'Expense deleted successfully'})
        else:
            return jsonify({'error': 'Expense not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    """Update an expense"""
    try:
        data = request.get_json()
        
        success = db.update_expense(
            expense_id,
            description=data.get('description'),
            amount=data.get('amount'),
            category=data.get('category'),
            notes=data.get('notes')
        )
        
        if success:
            return jsonify({'message': 'Expense updated successfully'})
        else:
            return jsonify({'error': 'Expense not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/categories', methods=['GET'])
def get_category_analytics():
    """Get spending analytics by category"""
    try:
        data = db.get_expenses_by_category()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/monthly', methods=['GET'])
def get_monthly_analytics():
    """Get monthly spending analytics"""
    try:
        data = db.get_monthly_summary()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/total', methods=['GET'])
def get_total_spending():
    """Get total spending"""
    try:
        total = db.get_total_spending()
        return jsonify({'total': total})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get available categories"""
    try:
        categories = predictor.get_categories()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor.categorizer.model is not None,
        'database_connected': True
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("Starting Expense Tracker API...")
    if debug:
        print("Visit: http://localhost:5000")
    app.run(debug=debug, host='0.0.0.0', port=port)

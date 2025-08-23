import pickle
import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))
from train_model import ExpenseCategorizer

class ExpensePredictor:
    def __init__(self):
        self.categorizer = ExpenseCategorizer()
        self.model_path = os.path.join(os.path.dirname(__file__), 'expense_categorizer.pkl')
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        if os.path.exists(self.model_path):
            return self.categorizer.load_model(self.model_path)
        else:
            print("Model not found. Please train the model first.")
            return False
    
    def predict(self, description):
        """Predict category for expense description"""
        if not self.categorizer.model:
            return {'category': 'Other', 'confidence': 0.0}
        
        return self.categorizer.predict_category(description)
    
    def get_categories(self):
        """Get list of available categories"""
        return self.categorizer.categories

# Create global predictor instance
predictor = ExpensePredictor()

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
import pickle
import os

class ExpenseCategorizer:
    def __init__(self):
        self.model = None
        self.categories = ['Food', 'Transportation', 'Entertainment']
        
    def load_data(self, csv_path):
        """Load training data from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            print(f"Loaded {len(df)} training examples")
            print(f"Categories: {df['category'].unique()}")
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def preprocess_text(self, text):
        """Simple text preprocessing"""
        if pd.isna(text):
            return ""
        return str(text).lower().strip()
    
    def train_model(self, df):
        """Train the expense categorization model"""
        # Preprocess descriptions
        df['description_clean'] = df['description'].apply(self.preprocess_text)
        
        # Prepare features and labels
        X = df['description_clean']
        y = df['category']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Create pipeline with TF-IDF and Naive Bayes
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
        # Train model
        print("Training model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\nModel Accuracy: {accuracy:.2%}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
    
    def predict_category(self, description):
        """Predict category for a single expense description"""
        if not self.model:
            return "Unknown"
        
        clean_description = self.preprocess_text(description)
        prediction = self.model.predict([clean_description])[0]
        confidence = self.model.predict_proba([clean_description]).max()
        
        return {
            'category': prediction,
            'confidence': float(confidence)
        }
    
    def save_model(self, model_path):
        """Save trained model to disk"""
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"Model saved to {model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self, model_path):
        """Load trained model from disk"""
        try:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"Model loaded from {model_path}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

def main():
    # Initialize categorizer
    categorizer = ExpenseCategorizer()
    
    # Get paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data', 'training_data.csv')
    model_path = os.path.join(current_dir, 'expense_categorizer.pkl')
    
    print("=== Expense Categorizer Training ===")
    
    # Load and train model
    df = categorizer.load_data(data_path)
    if df is not None:
        accuracy = categorizer.train_model(df)
        
        # Save model
        categorizer.save_model(model_path)
        
        # Test with some examples
        print("\n=== Testing Model ===")
        test_expenses = [
            "Lunch at McDonald's",
            "Uber ride home",
            "Netflix monthly fee",
            "Grocery shopping",
            "Concert ticket"
        ]
        
        for expense in test_expenses:
            result = categorizer.predict_category(expense)
            print(f"'{expense}' -> {result['category']} (confidence: {result['confidence']:.2%})")
    
    print("\nTraining completed!")

if __name__ == "__main__":
    main()

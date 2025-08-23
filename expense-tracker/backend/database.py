import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

class ExpenseDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to database in project root
            project_root = os.path.dirname(os.path.dirname(__file__))
            self.db_path = os.path.join(project_root, 'expenses.db')
        else:
            self.db_path = db_path
        
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create expenses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    predicted_category TEXT,
                    confidence REAL,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                )
            ''')
            
            # Create budgets table for future features
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL UNIQUE,
                    monthly_limit REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print("Database initialized successfully")
    
    def add_expense(self, description, amount, category, predicted_category=None, confidence=None, notes=None):
        """Add a new expense to the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (description, amount, category, predicted_category, confidence, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (description, amount, category, predicted_category, confidence, notes))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_expenses(self):
        """Get all expenses from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM expenses 
                ORDER BY date_added DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_expenses_by_category(self):
        """Get expenses grouped by category"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, SUM(amount) as total_amount, COUNT(*) as count
                FROM expenses 
                GROUP BY category
                ORDER BY total_amount DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_expenses_by_month(self, year=None, month=None):
        """Get expenses for a specific month"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM expenses 
                WHERE strftime('%Y', date_added) = ? AND strftime('%m', date_added) = ?
                ORDER BY date_added DESC
            ''', (str(year), f"{month:02d}"))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_monthly_summary(self):
        """Get monthly spending summary"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    strftime('%Y-%m', date_added) as month,
                    category,
                    SUM(amount) as total_amount,
                    COUNT(*) as count
                FROM expenses 
                GROUP BY strftime('%Y-%m', date_added), category
                ORDER BY month DESC, total_amount DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_expense(self, expense_id):
        """Delete an expense by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_expense(self, expense_id, description=None, amount=None, category=None, notes=None):
        """Update an expense"""
        updates = []
        values = []
        
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        if amount is not None:
            updates.append("amount = ?")
            values.append(amount)
        if category is not None:
            updates.append("category = ?")
            values.append(category)
        if notes is not None:
            updates.append("notes = ?")
            values.append(notes)
        
        if not updates:
            return False
        
        values.append(expense_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE expenses 
                SET {", ".join(updates)}
                WHERE id = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def get_total_spending(self):
        """Get total spending across all categories"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT SUM(amount) as total FROM expenses')
            result = cursor.fetchone()
            return result['total'] if result['total'] else 0.0
    
    def clear_all_expenses(self):
        """Clear all expenses (for testing)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses')
            conn.commit()

# Create global database instance
db = ExpenseDatabase()

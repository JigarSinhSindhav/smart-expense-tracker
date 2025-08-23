#!/usr/bin/env python3
"""
Setup script for Smart Expense Tracker
This script will train the ML model and start the application
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def train_model():
    """Train the ML model"""
    print("Training ML model...")
    try:
        # Change to ml_model directory and run training
        os.chdir('ml_model')
        subprocess.check_call([sys.executable, 'train_model.py'])
        os.chdir('..')
        print("✅ ML model trained successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error training model: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    return True

def start_app():
    """Start the Flask application"""
    print("Starting the application...")
    print("🌟 Visit http://localhost:5000 to use the app")
    print("Press Ctrl+C to stop the server")
    
    try:
        os.chdir('backend')
        subprocess.check_call([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Error starting app: {e}")

def main():
    print("🚀 Smart Expense Tracker Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('requirements.txt'):
        print("❌ Please run this script from the expense-tracker directory")
        sys.exit(1)
    
    # Install dependencies
    if not install_requirements():
        sys.exit(1)
    
    # Train model
    if not train_model():
        print("⚠️  Model training failed. You can try again later by running:")
        print("  cd ml_model && python train_model.py")
    
    # Start application
    start_app()

if __name__ == "__main__":
    main()

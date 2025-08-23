#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Train the ML model
cd ml_model
python train_model.py
cd ..

echo "Build completed successfully!"

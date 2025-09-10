#!/bin/bash
# PhotoVault Run Script

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting PhotoVault application..."
python main.py

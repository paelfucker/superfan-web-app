#!/usr/bin/env bash

# Create and activate virtual environment
python3 -m venv env
source env/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Install and build frontend
cd frontend
npm install
npm run build
cd ..

# Start FastAPI app with gunicorn
exec gunicorn backend.main:app --bind=0.0.0.0:$PORT

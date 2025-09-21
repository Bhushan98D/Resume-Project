"""
System startup script for the Resume Relevance Check System.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed."""
    print("Checking requirements...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'sqlalchemy', 
        'pandas', 'numpy', 'scikit-learn', 'spacy',
        'fuzzywuzzy', 'sentence-transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✓ All required packages are installed")
    return True

def check_spacy_model():
    """Check if spaCy model is available."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✓ spaCy model is available")
        return True
    except OSError:
        print("✗ spaCy model not found. Please install with:")
        print("python -m spacy download en_core_web_sm")
        return False

def start_backend_server():
    """Start the FastAPI backend server."""
    print("Starting backend server...")
    
    # Change to backend directory
    os.chdir("backend")
    
    try:
        # Start the server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "app:app", 
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
        
        print("✓ Backend server started on http://localhost:8000")
        return process
    except Exception as e:
        print(f"✗ Error starting backend: {e}")
        return None

def start_frontend_server():
    """Start the Streamlit frontend server."""
    print("Starting frontend server...")
    
    # Change back to project root
    os.chdir("..")
    
    try:
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "frontend/dashboard.py",
            "--server.port", "8501", "--server.address", "0.0.0.0"
        ])
        
        print("✓ Frontend server started on http://localhost:8501")
        return process
    except Exception as e:
        print(f"✗ Error starting frontend: {e}")
        return None

def main():
    """Main startup function."""
    print("Resume Relevance Check System - Startup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("✗ Please run this script from the project root directory")
        return
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check spaCy model
    if not check_spacy_model():
        return
    
    print("\nStarting servers...")
    
    # Start backend
    backend_process = start_backend_server()
    if not backend_process:
        print("Failed to start backend server")
        return
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    frontend_process = start_frontend_server()
    if not frontend_process:
        print("Failed to start frontend server")
        backend_process.terminate()
        return
    
    print("\n" + "=" * 40)
    print("System is now running!")
    print("Backend API: http://localhost:8000")
    print("Frontend Dashboard: http://localhost:8501")
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Wait for user to stop
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Servers stopped.")

if __name__ == "__main__":
    main()

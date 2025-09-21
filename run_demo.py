"""
Quick demo runner for the Resume Relevance Check System.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing requirements: {e}")
        return False

def download_spacy_model():
    """Download required spaCy model."""
    print("Downloading spaCy model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✓ spaCy model downloaded successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error downloading spaCy model: {e}")
        return False

def run_demo():
    """Run the demo script."""
    print("Running demo...")
    try:
        subprocess.check_call([sys.executable, "demo.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running demo: {e}")
        return False

def start_backend():
    """Start the backend server."""
    print("Starting backend server...")
    try:
        # Start backend in background
        backend_process = subprocess.Popen([sys.executable, "backend/app.py"])
        time.sleep(3)  # Give server time to start
        print("✓ Backend server started!")
        return backend_process
    except Exception as e:
        print(f"✗ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend."""
    print("Starting Streamlit dashboard...")
    try:
        # Start frontend
        frontend_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "frontend/dashboard.py"])
        time.sleep(2)
        print("✓ Streamlit dashboard started!")
        print("Dashboard should open automatically in your browser.")
        print("If not, go to: http://localhost:8501")
        return frontend_process
    except Exception as e:
        print(f"✗ Error starting frontend: {e}")
        return None

def main():
    """Main function to set up and run the system."""
    print("Resume Relevance Check System - Quick Start")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("✗ Please run this script from the project root directory")
        return
    
    # Install requirements
    if not install_requirements():
        print("Failed to install requirements. Please install manually:")
        print("pip install -r requirements.txt")
        return
    
    # Download spaCy model
    if not download_spacy_model():
        print("Failed to download spaCy model. Please install manually:")
        print("python -m spacy download en_core_web_sm")
        return
    
    # Run demo
    print("\nRunning demo with sample data...")
    if not run_demo():
        print("Demo failed. Please check the error messages above.")
        return
    
    # Ask user if they want to start the web interface
    print("\n" + "=" * 50)
    response = input("Would you like to start the web interface? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("\nStarting web interface...")
        
        # Start backend
        backend_process = start_backend()
        if not backend_process:
            print("Failed to start backend. Please start manually:")
            print("python backend/app.py")
            return
        
        # Start frontend
        frontend_process = start_frontend()
        if not frontend_process:
            print("Failed to start frontend. Please start manually:")
            print("streamlit run frontend/dashboard.py")
            return
        
        print("\n" + "=" * 50)
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
    
    else:
        print("\nDemo completed! To start the web interface later:")
        print("1. Start backend: python backend/app.py")
        print("2. Start frontend: streamlit run frontend/dashboard.py")

if __name__ == "__main__":
    main()

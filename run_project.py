"""
run_project.py
Setup and run the AQI Prediction system
"""

import subprocess
import sys
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent

def install_requirements():
    """Install project requirements"""
    print("=" * 60)
    print("Installing dependencies...")
    print("=" * 60)
    
    requirements_file = PROJECT_ROOT / "requirements" / "advanced.txt"
    
    if requirements_file.exists():
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements_file)],
            check=False
        )
        print("✓ Dependencies installed successfully\n")
    else:
        print("! Requirements file not found, installing basics...")
        basics = [
            "streamlit>=1.28.0",
            "pandas>=1.5.0",
            "numpy>=1.23.0",
            "matplotlib>=3.7.0",
            "plotly>=5.14.0",
            "scikit-learn>=1.2.0",
            "requests>=2.31.0"
        ]
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q"] + basics,
            check=False
        )
        print("✓ Basic dependencies installed\n")


def run_dashboard():
    """Run Streamlit dashboard"""
    print("=" * 60)
    print("Starting AQI Prediction Dashboard...")
    print("=" * 60)
    print("\n📊 Dashboard will open at: http://localhost:8501\n")
    print("Press CTRL+C to stop the server\n")
    
    dashboard_path = PROJECT_ROOT / "src" / "apps" / "dashboard.py"
    
    if dashboard_path.exists():
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port=8501",
            "--logger.level=error"
        ])
    else:
        print("✗ Dashboard file not found at", dashboard_path)
        print("\nAvailable options:")
        print("1. python run_project.py --api fastapi")
        print("2. python run_project.py --api flask")


def run_fastapi():
    """Run FastAPI server"""
    print("=" * 60)
    print("Starting FastAPI Server...")
    print("=" * 60)
    print("\n🔌 API will be available at: http://localhost:8000")
    print("📚 API Docs at: http://localhost:8000/docs\n")
    print("Press CTRL+C to stop the server\n")
    
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "src.apps.api.fastapi_app:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ])


def run_flask():
    """Run Flask server"""
    print("=" * 60)
    print("Starting Flask Server...")
    print("=" * 60)
    print("\n🔌 API will be available at: http://localhost:5000\n")
    print("Press CTRL+C to stop the server\n")
    
    os.environ["FLASK_APP"] = "src.apps.api.flask_app"
    os.environ["FLASK_ENV"] = "development"
    
    subprocess.run([
        sys.executable, "-m", "flask",
        "run",
        "--host", "0.0.0.0",
        "--port", "5000"
    ])


def main():
    """Main entry point"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " AQI PREDICTION SYSTEM - PROJECT LAUNCHER ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Install dependencies first
    install_requirements()
    
    # Get argument
    if len(sys.argv) > 1:
        app = sys.argv[1].lower()
        
        if app == "--dashboard":
            run_dashboard()
        elif app == "--api":
            if len(sys.argv) > 2:
                api_type = sys.argv[2].lower()
                if api_type == "fastapi":
                    run_fastapi()
                elif api_type == "flask":
                    run_flask()
                else:
                    print(f"Unknown API type: {api_type}")
            else:
                print("Available API types: fastapi, flask")
                print("Usage: python run_project.py --api fastapi")
        else:
            print(f"Unknown option: {app}")
    else:
        # Default: run dashboard
        print("Starting with default: Streamlit Dashboard")
        print("(Use --api fastapi or --api flask for API servers)\n")
        run_dashboard()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Application stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

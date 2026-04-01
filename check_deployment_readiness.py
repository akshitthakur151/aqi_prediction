"""
Pre-Deployment Verification Script
Checks if your AQI Dashboard is ready for deployment
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: MISSING - {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: MISSING - {dirpath}")
        return False

def check_file_content(filepath, content_list, description):
    """Check if file contains certain content"""
    if not os.path.exists(filepath):
        print(f"❌ {description}: File not found")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    missing = []
    for item in content_list:
        if item not in content:
            missing.append(item)
    
    if not missing:
        print(f"✅ {description}: All required packages present")
        return True
    else:
        print(f"⚠️  {description}: Missing packages - {', '.join(missing)}")
        return False

def main():
    print("\n" + "="*70)
    print("🚀 AQI DASHBOARD - DEPLOYMENT READINESS CHECK")
    print("="*70 + "\n")
    
    all_checks_passed = True
    
    # 1. Check main files
    print("📋 CHECKING CORE FILES:")
    print("-" * 70)
    all_checks_passed &= check_file_exists("src/apps/dashboard.py", "Dashboard App")
    all_checks_passed &= check_file_exists("requirements.txt", "Requirements")
    all_checks_passed &= check_file_exists(".streamlit/config.toml", "Streamlit Config")
    all_checks_passed &= check_file_exists("Dockerfile", "Dockerfile")
    all_checks_passed &= check_file_exists(".dockerignore", "DockerIgnore")
    print()
    
    # 2. Check data and models
    print("🗂️  CHECKING DATA & MODELS:")
    print("-" * 70)
    all_checks_passed &= check_file_exists("data/aqi_data.csv", "AQI Data")
    all_checks_passed &= check_directory_exists("models", "Models Directory")
    if os.path.isdir("models"):
        pkl_files = list(Path("models").glob("*.pkl"))
        if pkl_files:
            print(f"✅ Model files found: {len(pkl_files)} pickle files")
        else:
            print(f"❌ Model files: NO PICKLE FILES FOUND in models/")
            all_checks_passed = False
    print()
    
    # 3. Check dependencies
    print("📦 CHECKING DEPENDENCIES:")
    print("-" * 70)
    required_packages = [
        "streamlit>=1.32.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "scikit-learn>=1.3.0",
        "xgboost>=2.0.0"
    ]
    all_checks_passed &= check_file_content(
        "requirements.txt",
        required_packages,
        "Required packages"
    )
    print()
    
    # 4. Check Git status
    print("🔧 CHECKING GIT:")
    print("-" * 70)
    if os.path.isdir(".git"):
        print(f"✅ Git repository: Initialized")
        # Check if there are uncommitted changes
        os.system("git status --short > /tmp/git_status.txt 2>&1")
        with open("/tmp/git_status.txt", 'r') as f:
            status = f.read()
        if status.strip():
            print(f"⚠️  Uncommitted changes detected. Run: git add . && git commit -m 'message'")
        else:
            print(f"✅ No uncommitted changes")
    else:
        print(f"❌ Git repository: NOT initialized")
        all_checks_passed = False
    print()
    
    # 5. Deployment readiness summary
    print("="*70)
    if all_checks_passed:
        print("✅ DEPLOYMENT READY! 🎉")
        print("\nNEXT STEPS:")
        print("1. Ensure all changes are committed: git push origin main")
        print("2. Visit: https://share.streamlit.io/")
        print("3. Create new app and connect your GitHub repository")
        print("4. Select: src/apps/dashboard.py as the main file")
        print("5. Your app will be live in minutes!")
        print("\nAlternatively, deploy with Docker:")
        print("  docker build -t aqi-predictor:latest .")
        print("  docker run -p 8501:8501 aqi-predictor:latest")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nPlease fix the issues above before deploying.")
        print("See DEPLOYMENT_GUIDE.md for help.")
    
    print("="*70 + "\n")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())

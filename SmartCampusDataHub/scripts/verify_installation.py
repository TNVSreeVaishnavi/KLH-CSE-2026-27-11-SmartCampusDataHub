#!/usr/bin/env python3
"""
Installation and Verification Script for Smart Campus Data Hub

This script verifies all dependencies are installed and provides quick diagnostic information.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("Python Version Check")
    print(f"  Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    if sys.version_info < (3, 8):
        print("  WARNING: Python 3.8+ required")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\nDependency Check")
    
    required_packages = [
        'pandas',
        'numpy',
        'streamlit',
        'plotly',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  {package}")
        except ImportError:
            print(f"  {package} (missing)")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_project_structure():
    """Verify project structure"""
    print("\nProject Structure Check")
    
    required_dirs = [
        'data/raw',
        'data/processed',
        'data/sample',
        'config',
        'ingestion',
        'processing',
        'database',
        'analytics',
        'dashboard',
        'scripts',
        'tests',
        'logs'
    ]
    
    required_files = [
        'config/config.py',
        'ingestion/ingest.py',
        'processing/cleaning.py',
        'processing/validation.py',
        'processing/transformation.py',
        'database/connection.py',
        'database/schema.sql',
        'database/load_data.py',
        'analytics/queries.py',
        'dashboard/app.py',
        'scripts/run_pipeline.py',
        'scripts/generate_sample_data.py',
        'tests/test_pipeline.py',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md'
    ]
    
    project_root = Path(__file__).parent.parent
    
    all_ok = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  {dir_path}/")
        else:
            print(f"  {dir_path}/ (missing)")
            all_ok = False
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  {file_path}")
        else:
            print(f"  {file_path} (missing)")
            all_ok = False
    
    return all_ok

def main():
    """Run verification checks"""
    
    print("="*70)
    print("SMART CAMPUS DATA HUB - INSTALLATION & VERIFICATION")
    print("="*70)
    
    py_ok = check_python_version()
    struct_ok = check_project_structure()
    deps_ok, missing_deps = check_dependencies()
    
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    all_ok = py_ok and struct_ok and deps_ok
    
    if all_ok:
        print("\nAll checks passed! You're ready to use Smart Campus Data Hub.")
        print("\nNext steps:")
        print("  1. Generate sample data:")
        print("     python scripts/generate_sample_data.py")
        print("  2. Run the pipeline:")
        print("     python scripts/run_pipeline.py")
        print("  3. Start the dashboard:")
        print("     streamlit run dashboard/app.py")
        print("  4. Run tests:")
        print("     python tests/test_pipeline.py")
    else:
        print("\nSome checks failed. Please address the issues:")
        if not py_ok:
            print("  - Upgrade to Python 3.8 or higher")
        if not struct_ok:
            print("  - Verify project structure is complete")
        if missing_deps:
            print(f"  - Install missing packages: {', '.join(missing_deps)}")
            print("    Run: pip install -r requirements.txt")
    
    print("="*70)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Setup script for arch-sense agentic coaching system.
Creates database, directories, and validates configuration.
"""

import os
import sys
from pathlib import Path

def setup_directories():
    """Create required directories."""
    dirs = [
        'data',      # For SQLite database
        'logs',      # For server logs
        'models',    # Already exists
        'db',        # Already exists
        'agents',    # Already exists
        'services'   # Already exists
    ]
    
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"✓ Directory {d}/")

def setup_env():
    """Create .env file from example if not present."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✓ .env already exists")
        return
    
    if env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✓ Created .env from .env.example")
    else:
        print("✗ .env.example not found")

def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")
    
    required = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'crewai'
    ]
    
    import subprocess
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'list'],
        capture_output=True,
        text=True
    )
    
    installed = result.stdout.lower()
    missing = []
    
    for pkg in required:
        if pkg.lower() in installed:
            print(f"✓ {pkg}")
        else:
            missing.append(pkg)
            print(f"✗ {pkg}")
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"Run: pip install -r requirements.txt")
        return False
    
    return True

def init_database():
    """Initialize SQLite database with schema."""
    try:
        from db.database import GameDatabase
        from config import settings
        
        db = GameDatabase(str(settings.database_url))
        db.init_schema()
        print("✓ Database initialized at", settings.database_url)
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def validate_config():
    """Validate configuration."""
    try:
        from config import settings
        
        print("\nConfiguration:")
        print(f"  Environment: {settings.environment}")
        print(f"  Server: {settings.host}:{settings.port}")
        print(f"  Database: {settings.database_url}")
        print(f"  Coaching Style: {settings.coaching_style}")
        print(f"  Difficulty: {settings.difficulty_level}")
        
        if not os.getenv('GEMINI_API_KEY'):
            print("  ⚠️  GEMINI_API_KEY not set (coaches will use rule-based analysis)")
        else:
            print("  ✓ GEMINI_API_KEY configured")
        
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False

def main():
    """Run all setup steps."""
    print("🚀 Setting up arch-sense agentic coaching system...\n")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("✗ Python 3.9+ required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Run setup steps
    setup_directories()
    setup_env()
    
    if not check_dependencies():
        print("\n⚠️  Install dependencies and try again:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    if not validate_config():
        sys.exit(1)
    
    if not init_database():
        print("\n⚠️  Database initialization failed")
        print("You can still run the server; database will be created on first request")
    
    print("\n" + "="*50)
    print("✅ Setup complete!")
    print("="*50)
    print("\nTo start the server:")
    print("  python main.py")
    print("\nAPI Docs:")
    print("  http://localhost:8000/docs")
    print("\nFrontend should connect to:")
    print("  http://localhost:8000")
    print("\nEnvironment file:")
    print("  Edit .env to configure API keys, coaching style, difficulty")

if __name__ == '__main__':
    main()

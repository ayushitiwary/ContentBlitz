#!/usr/bin/env python3
"""
Quick start script for ContentBlitz
Run this to launch the application
"""

import subprocess
import sys
import os
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("📝 Creating .env from .env.example...")

        example_path = Path(".env.example")
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            with open(env_path, 'w') as f:
                f.write(content)

            print("✅ .env file created!")
            print("\n⚠️  IMPORTANT: Edit .env file and add your API keys before continuing.")
            print("   Required: OPENAI_API_KEY")
            print("   Optional: SERPER_API_KEY (for web research)\n")
            return False
        else:
            print("❌ .env.example not found!")
            return False

    # Check if keys are set
    with open(env_path, 'r') as f:
        content = f.read()
        if "your_openai_api_key_here" in content:
            print("⚠️  Warning: Please set your OPENAI_API_KEY in .env file")
            return False

    return True

def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import streamlit
        import langchain
        import openai
        return True
    except ImportError:
        print("❌ Dependencies not installed!")
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def main():
    """Main entry point"""
    print("🚀 ContentBlitz - Starting...\n")

    # Check environment
    if not check_env_file():
        sys.exit(1)

    # Check dependencies
    check_dependencies()

    # Create data directory if it doesn't exist
    data_dir = Path("data/chromadb")
    data_dir.mkdir(parents=True, exist_ok=True)

    print("✅ All checks passed!")
    print("🌐 Launching ContentBlitz web interface...\n")
    print("=" * 60)
    print("Access the app at: http://localhost:8501")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

    # Launch Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "ui/app.py",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    main()


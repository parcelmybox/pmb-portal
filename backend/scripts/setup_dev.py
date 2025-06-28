#!/usr/bin/env python3
"""
Development setup script for ParcelMyBox Portal.
This script helps set up the development environment with the new project structure.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and print output in real-time."""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=cwd
    )
    
    # Print output in real-time
    for line in process.stdout:
        print(line, end='')
    
    # Wait for the process to complete
    process.wait()
    return process.returncode

def main():
    print("Setting up ParcelMyBox Portal development environment...")
    
    # Set up Python virtual environment
    if not os.path.exists('venv'):
        print("Creating Python virtual environment...")
        run_command('python -m venv venv')
    
    # Activate virtual environment and install requirements
    print("Installing Python dependencies...")
    if os.name == 'nt':  # Windows
        pip_cmd = '\\venv\\Scripts\\pip'
        python_cmd = '\\venv\\Scripts\\python'
    else:  # Unix/Linux/Mac
        pip_cmd = 'venv/bin/pip'
        python_cmd = 'venv/bin/python'
    
    run_command(f'{pip_cmd} install --upgrade pip')
    run_command(f'{pip_cmd} install -r backend/requirements.txt')
    
    # Install backend in development mode
    run_command(f'{pip_cmd} install -e .')
    
    # Set up Django
    print("Setting up Django...")
    run_command(f'{python_cmd} backend/manage.py migrate')
    run_command(f'{python_cmd} backend/manage.py createsuperuser --noinput')
    
    # Install frontend dependencies
    print("Installing frontend dependencies...")
    run_command('npm install', cwd='frontend')
    
    # Set up environment variables
    env_file = Path('.env')
    if not env_file.exists():
        print("Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# Django Settings
DEBUG=1
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=*

# Database Settings
DB_NAME=pmb_db
DB_USER=pmb_user
DB_PASSWORD=pmb_user
DB_HOST=db
DB_PORT=3306

# Frontend Settings
REACT_APP_API_URL=http://localhost:8000
""")
    
    print("\nSetup complete!\n")
    print("To start the development environment, run:")
    print("1. docker-compose up -d")
    print("2. cd frontend && npm start")
    print("\nAccess the application at http://localhost:3000")

if __name__ == '__main__':
    main()

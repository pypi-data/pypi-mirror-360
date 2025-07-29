#!/usr/bin/env python3
"""
Main entry point for promptman package.
Allows running with: python -m promptman
"""

import os
import sys

# Add the current directory to Python path so we can import run
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import and run the main application
    from run import main

    main()
except ImportError:
    print("Error: Unable to import the main application module.")
    print("Please ensure promptman is properly installed.")
    sys.exit(1)
except Exception as e:
    print(f"Error starting AI Prompt Manager: {e}")
    sys.exit(1)

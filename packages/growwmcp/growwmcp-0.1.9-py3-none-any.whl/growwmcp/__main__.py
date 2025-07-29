# src/your_package_name/__main__.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from growwmcp.main import main  # Change from .main to growwmcp.main

if __name__ == "__main__":
    main()  # or just main() if it handles args internally

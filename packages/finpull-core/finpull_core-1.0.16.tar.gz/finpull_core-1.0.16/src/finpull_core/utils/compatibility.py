"""
Compatibility checking for different environments and dependencies
"""

# Platform detection for compatibility
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

try:
    from openpyxl import Workbook
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

def check_web_scraping_support():
    """Check if web scraping is supported"""
    return HAS_REQUESTS and HAS_BS4

def check_gui_support():
    """Check if GUI is supported"""
    return HAS_TKINTER

def check_excel_support():
    """Check if Excel export is supported"""
    return HAS_OPENPYXL

def get_missing_dependencies():
    """Get list of missing optional dependencies"""
    missing = []
    
    if not HAS_REQUESTS:
        missing.append("requests")
    if not HAS_BS4:
        missing.append("beautifulsoup4")
    if not HAS_YFINANCE:
        missing.append("yfinance")
    if not HAS_TKINTER:
        missing.append("tkinter (python3-tk)")
    if not HAS_OPENPYXL:
        missing.append("openpyxl")
    
    return missing

def get_available_features():
    """
    Return dict of available features based on installed packages
    
    Returns:
        Dictionary mapping feature names to availability status
    """
    return {
        "web_scraping": HAS_REQUESTS and HAS_BS4,
        "yahoo_finance": HAS_YFINANCE,
        "gui": HAS_TKINTER,
        "excel_export": HAS_OPENPYXL,
        "json_export": True,
        "csv_export": True
    }

def print_dependency_status():
    """Print status of all dependencies"""
    print("Dependency Status:")
    print(f"  requests: {'✓' if HAS_REQUESTS else '✗'}")
    print(f"  beautifulsoup4: {'✓' if HAS_BS4 else '✗'}")
    print(f"  yfinance: {'✓' if HAS_YFINANCE else '✗'}")
    print(f"  tkinter: {'✓' if HAS_TKINTER else '✗'}")
    print(f"  openpyxl: {'✓' if HAS_OPENPYXL else '✗'}")
    
    missing = get_missing_dependencies()
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
    else:
        print("\nAll dependencies available!")

if __name__ == "__main__":
    print_dependency_status() 
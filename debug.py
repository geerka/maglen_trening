#!/usr/bin/env python
"""Debug script to check if app can be imported and initialized"""

import sys
import os

print("[DEBUG] Python version:", sys.version)
print("[DEBUG] Current directory:", os.getcwd())
print("[DEBUG] Files in current directory:", os.listdir('.'))

try:
    print("[DEBUG] Attempting to import Flask...")
    from flask import Flask
    print("[DEBUG] ✓ Flask imported successfully")
except Exception as e:
    print(f"[ERROR] Could not import Flask: {e}")
    sys.exit(1)

try:
    print("[DEBUG] Attempting to import app from app.py...")
    from app import app
    print("[DEBUG] ✓ App imported successfully")
except Exception as e:
    print(f"[ERROR] Could not import app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("[DEBUG] App initialized successfully!")
print("[DEBUG] Routes available:")
for rule in app.url_map.iter_rules():
    print(f"  - {rule}")

print("[DEBUG] ✓ All checks passed!")

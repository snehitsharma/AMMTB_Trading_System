import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("Attempting to import main...")
try:
    from main import app
    print("SUCCESS: main imported successfully.")
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()

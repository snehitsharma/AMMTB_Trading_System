
import sys
import asyncio
import uvicorn
import os

# FORCE WINDOWS SELECTOR POLICY (Fixes "Event loop is closed" crash)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    # Ensure we can import from current dir
    sys.path.append(os.getcwd())
    
    # Run Uvicorn
    print("🚀 US Agent Launching with Windows Selector Policy...")
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)

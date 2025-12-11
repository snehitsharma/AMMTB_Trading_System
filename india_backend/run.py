
import sys
import asyncio
import uvicorn
import os

# FORCE WINDOWS SELECTOR POLICY
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    print("🚀 India Agent Launching with Windows Selector Policy...")
    uvicorn.run("main:app", host="127.0.0.1", port=8003, reload=True)

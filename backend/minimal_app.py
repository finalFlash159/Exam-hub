#!/usr/bin/env python3
"""
Minimal FastAPI app for Railway deployment testing
"""

import os
from fastapi import FastAPI

# Create minimal app
app = FastAPI(title="Minimal Test API")

@app.get("/")
async def root():
    return {"message": "Minimal FastAPI app working", "port": os.environ.get("PORT", "unknown")}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "minimal-test"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting minimal app on port {port}")
    uvicorn.run("minimal_app:app", host="0.0.0.0", port=port, reload=False) 
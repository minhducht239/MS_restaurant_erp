from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import users
import os

app = FastAPI(title="User Service")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for avatars
if not os.path.exists("uploads"):
    os.makedirs("uploads")
    
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(users.router, prefix="/users", tags=["Users"])

@app.get("/")
async def health():
    return {"status": "ok", "service": "user_service"}
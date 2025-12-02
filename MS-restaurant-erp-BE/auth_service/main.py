from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth

app = FastAPI(title="Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def health():
    return {"status": "ok", "service": "auth_service"}
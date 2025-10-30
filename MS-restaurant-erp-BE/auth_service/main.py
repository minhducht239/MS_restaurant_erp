from fastapi import FastAPI
from routes import users

app = FastAPI(title="Auth Service (MongoDB)")

app.include_router(users.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def health():
    return {"status": "ok"}

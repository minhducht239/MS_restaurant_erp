from fastapi import FastAPI
from routes import staff

app = FastAPI(title="Staff Service")
app.include_router(staff.router)

@app.get("/")
async def health():
    return {"status": "ok"}
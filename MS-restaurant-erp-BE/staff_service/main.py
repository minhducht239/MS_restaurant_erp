from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import staff

app = FastAPI(title="Staff Service", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(staff.router, tags=["Staff"])

@app.get("/")
async def root():
    return {
        "service": "Staff Service",
        "version": "1.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
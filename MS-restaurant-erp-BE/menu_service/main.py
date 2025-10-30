from fastapi import FastAPI
from routes import menu

app = FastAPI(title="Menu Service")
app.include_router(menu.router)
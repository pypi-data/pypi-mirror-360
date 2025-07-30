from fastapi import FastAPI
from app.routes import router
from app.database import engine, metadata

app = FastAPI()

@app.on_event("startup")
async def startup():
    metadata.create_all(engine)

app.include_router(router)
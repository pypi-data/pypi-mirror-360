from fastapi import FastAPI
from routes.test import router

app = FastAPI()
app.include_router(router)


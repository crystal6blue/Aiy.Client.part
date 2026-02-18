from fastapi import FastAPI
from internal.api.routes import router

app = FastAPI()
app.include_router(router)

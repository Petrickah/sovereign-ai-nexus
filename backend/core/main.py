from contextlib import asynccontextmanager

from fastapi import FastAPI
from db.database import DatabaseClient

db_client = DatabaseClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db_client.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {
        "Database URL": db_client.get_url(),
        "Database Details": db_client.get_details(),
    }

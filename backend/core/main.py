from fastapi import FastAPI
from db.database import DatabaseClient

app = FastAPI()

@app.get("/")
async def read_root():
    client = DatabaseClient()
    try:
        return {
            "Database URL": client.get_url(),
            "Database Details": client.get_details(),
        }
    finally:
        client.close()

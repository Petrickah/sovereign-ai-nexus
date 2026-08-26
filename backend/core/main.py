import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db.database import DatabaseClient
from core.models import ChatRequest, ChatResponse

db_client = DatabaseClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db_client.close()

app = FastAPI(lifespan=lifespan)

frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

async def call_llm(prompt: str) -> str:
    context = []
    for msg in reversed(db_client.get_exchanges(msg_count=30)):
        context.append("User: {prompt}\nResponse: {response}\n".format(prompt=msg.prompt, response=msg.response))
    full_prompt = "Salut! Tu ești Claude Code, un assistent AI creeat de Anthropic. Ai avut următoarea conversație:\n{context}Utilizatorul spune:\n{prompt}".format(
        context ='---\n\n'.join(context),
        prompt  =prompt
    )

    proc = await asyncio.create_subprocess_exec(
        "claude", "-p", full_prompt,
        cwd="/workspace",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(stderr.decode())
    return stdout.decode().strip()

@app.get("/")
async def read_root():
    return {
        "Database URL": db_client.get_url(),
        "Database Details": db_client.get_details(),
    }

@app.post("/chat")
async def chat(msg: ChatRequest):
    created_at = datetime.now(timezone.utc)
    response_text = await call_llm(msg.prompt)

    # This will save into the database the Chat Exchange
    new_id = db_client.insert_exchange(msg.prompt, response_text, created_at)

    return ChatResponse(
        id=new_id,
        prompt=msg.prompt,
        response=response_text,
        created_at=created_at
    )

@app.get("/history")
async def get_history() -> list[ChatResponse]:
    return db_client.get_history()

@app.delete("/history/{exchange_id}")
async def delete_exchange(exchange_id: int):
    if not db_client.delete_exchange(exchange_id):
        raise HTTPException(status_code=404, detail="Exchange not found")
    return {"id": exchange_id}

@app.delete("/history")
async def delete_history():
    deleted = db_client.delete_all_exchanges()
    return {"deleted": deleted}
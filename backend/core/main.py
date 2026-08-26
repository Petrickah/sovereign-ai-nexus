import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI

from db.database import DatabaseClient
from core.models import ChatRequest, ChatResponse

db_client = DatabaseClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    db_client.close()

app = FastAPI(lifespan=lifespan)

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
    response: ChatResponse = ChatResponse(
        prompt = msg.prompt,
        response = await call_llm(msg.prompt),
        created_at = created_at
    )

    # This will save into the database the Chat Exchange
    db_client.insert_exchange(response)

    return response
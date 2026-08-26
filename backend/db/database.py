import os
from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, make_url

from core.models import ChatResponse

class DatabaseClient:
    def __init__(self) -> None:
        self._url = make_url("postgresql://{user}:{password}@{dbhost}:{dbport}/{dbname}".format(
            user    =os.environ["DATABASE_USER"],
            password=os.environ["DATABASE_PASSWORD"],
            dbname  =os.environ["DATABASE_NAME"],
            dbhost  =os.environ.get("DATABASE_HOST", "database"),
            dbport  =os.environ["DATABASE_PORT"]
        ))
        self._engine = create_engine(self._url)
        self._connect: Connection = self._engine.connect()

    def close(self) -> None:
        self._connect.close()

    def get_url(self) -> str:
        return str(self._url)

    def insert_exchange(self, prompt: str, response: str, created_at: datetime) -> int:
        result = self._connect.execute(
            text("INSERT INTO exchanges (prompt, response, created_at) VALUES (:prompt, :response, :created_at) RETURNING id"),
            {"prompt": prompt, "response": response, "created_at": created_at},
        )
        new_id = result.scalar_one()
        self._connect.commit()
        return new_id

    def get_exchanges(self, msg_count: int) -> list[ChatResponse]:
        result = self._connect.execute(
            text("SELECT id, prompt, response, created_at FROM exchanges ORDER BY created_at DESC LIMIT :msg_count"),
            {"msg_count": msg_count}
        )
        responses = []
        for row in result:
            responses.append(ChatResponse(
                id=row.id,
                prompt=row.prompt,
                response=row.response,
                created_at=row.created_at
            ))

        return responses

    def get_history(self) -> list[ChatResponse]:
        result = self._connect.execute(
            text("SELECT id, prompt, response, created_at FROM exchanges ORDER BY created_at ASC")
        )
        return [
            ChatResponse(id=row.id, prompt=row.prompt, response=row.response, created_at=row.created_at)
            for row in result
        ]

    def delete_exchange(self, exchange_id: int) -> bool:
        result = self._connect.execute(
            text("DELETE FROM exchanges WHERE id = :id RETURNING id"),
            {"id": exchange_id}
        )
        deleted = result.scalar_one_or_none() is not None
        self._connect.commit()
        return deleted

    def delete_all_exchanges(self) -> int:
        result = self._connect.execute(text("DELETE FROM exchanges"))
        self._connect.commit()
        return result.rowcount

    def get_details(self) -> dict:
        version = self._connect.execute(text("SELECT version()")).scalar()
        database = self._connect.execute(text("SELECT current_database()")).scalar()
        user = self._connect.execute(text("SELECT current_user")).scalar()
        tables = self._connect.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )).scalars().all()
        return {
            "version": version,
            "database": database,
            "user": user,
            "tables": list(tables),
        }
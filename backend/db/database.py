import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, make_url

from core.models import ChatResponse

class DatabaseClient:
    def __init__(self) -> None:
        self._url = make_url("postgresql://{user}:{password}@database:{dbport}/{dbname}".format(
            user    =os.environ["DATABASE_USER"],
            password=os.environ["DATABASE_PASSWORD"],
            dbname  =os.environ["DATABASE_NAME"],
            dbport  =os.environ["DATABASE_PORT"]
        ))
        self._engine = create_engine(self._url)
        self._connect: Connection = self._engine.connect()

    def close(self) -> None:
        self._connect.close()

    def get_url(self) -> str:
        return str(self._url)

    def insert_exchange(self, chat_response: ChatResponse) -> None:
        self._connect.execute(
            text("INSERT INTO exchanges (prompt, response, created_at) VALUES (:prompt, :response, :created_at)"),
            {"prompt": chat_response.prompt, "response": chat_response.response, "created_at": chat_response.created_at},
        )
        self._connect.commit()

    def get_exchanges(self, msg_count: int) -> list[ChatResponse]:
        result = self._connect.execute(
            text("SELECT prompt, response, created_at FROM exchanges ORDER BY created_at DESC LIMIT (:msg_count)"),
            {"msg_count": msg_count}
        )
        responses = []
        for row in result:
            responses.append(ChatResponse(
                prompt=row.prompt, 
                response=row.response, 
                created_at=row.created_at
            ))

        return responses

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
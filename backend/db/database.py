import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, make_url

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
from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings

client = MongoClient(
    settings.mongodb_uri
    )

database: Database = client[settings.mongodb_database]

def get_database() -> Database:
    return database


def close_mongodb() -> None:
    client.close()
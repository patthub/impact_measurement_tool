from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Optional
import os

class MongoSettings(BaseModel):
    uri: str = "mongodb://localhost:27017"
    database: str = "imeto"

settings = MongoSettings()

client = AsyncIOMotorClient(settings.uri)
db = client[settings.database]

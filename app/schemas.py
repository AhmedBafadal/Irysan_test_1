# app/schemas.py
from pydantic import BaseModel

class DataEntryCreate(BaseModel):
    latitude: float
    longitude: float
    year: int
    pm25: float

class DataEntryResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    year: int
    pm25: float

    class Config:
        orm_mode = True
from sqlalchemy import Column, Integer, Float
from sqlalchemy.ext.declarative import declarative_base

# Use SQLAlchemy's declarative base for the models
Base = declarative_base()

class DataEntry(Base):
    __tablename__ = "data_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    year = Column(Integer, nullable=False)
    pm25 = Column(Float, nullable=False)
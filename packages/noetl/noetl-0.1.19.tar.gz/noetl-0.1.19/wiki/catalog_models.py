
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON

class CatalogEntry(SQLModel, table=True):
    __tablename__ = "catalog"
    resource_path: str = Field(primary_key=True)
    resource_version: str = Field(primary_key=True)
    resource_type: str = Field(index=True)
    source: str = Field(default="inline")
    resource_location: Optional[str] = None
    payload: dict = Field(sa_column=Column(JSON), nullable=False)
    meta: Optional[dict] = Field(sa_column=Column(JSON))
    timestamp: Optional[str] = Field(default=None)

class Event(SQLModel, table=True):
    __tablename__ = "event"
    event_id: str = Field(primary_key=True)
    event_type: str = Field(index=True)
    resource_path: str
    resource_version: str
    payload: Optional[dict] = Field(sa_column=Column(JSON))
    meta: Optional[dict] = Field(sa_column=Column(JSON))
    timestamp: Optional[str] = Field(default=None)

class ResourceType(SQLModel, table=True):
    __tablename__ = "resource_type"
    name: str = Field(primary_key=True)

class EventType(SQLModel, table=True):
    __tablename__ = "event_type"
    name: str = Field(primary_key=True)
    template: Optional[str]

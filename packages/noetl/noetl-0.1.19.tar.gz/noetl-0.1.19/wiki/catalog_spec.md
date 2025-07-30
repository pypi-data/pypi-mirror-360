
# Finalized Catalog + Event Schema (With Templating & Defaults)

This schema supports rendering messages for event types via a `template` field, and includes default values for both resource types and event types.

---

## Reference Tables

### `resource_type`

```sql
CREATE TABLE resource_type (
    name TEXT PRIMARY KEY
);

-- Defaults:
INSERT INTO resource_type (name) VALUES
    ('playbook'),
    ('workflow'),
    ('target'),
    ('step'),
    ('task'),
    ('action');
```

### `event_type`

```sql
CREATE TABLE event_type (
    name TEXT PRIMARY KEY,
    template TEXT
);

-- Defaults:
INSERT INTO event_type (name, template) VALUES
    ('REGISTERED', 'Resource {{ resource_path }} version {{ resource_version }} was registered.'),
    ('UPDATED', 'Resource {{ resource_path }} version {{ resource_version }} was updated.'),
    ('UNCHANGED', 'Resource {{ resource_path }} already registered.'),
    ('EXECUTION_STARTED', 'Execution started for {{ resource_path }}.'),
    ('EXECUTION_FAILED', 'Execution failed for {{ resource_path }}.'),
    ('EXECUTION_COMPLETED', 'Execution completed for {{ resource_path }}.');
```

---

## Core Tables

### `catalog`

```sql
CREATE TABLE catalog (
    resource_path TEXT NOT NULL,
    resource_type TEXT NOT NULL REFERENCES resource_type(name),
    resource_version TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'inline',
    resource_location TEXT,
    payload JSONB NOT NULL,
    meta JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (resource_path, resource_version)
);
```

### `event`

```sql
CREATE TABLE event (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL REFERENCES event_type(name),
    resource_path TEXT NOT NULL,
    resource_version TEXT NOT NULL,
    payload JSONB,
    meta JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    FOREIGN KEY (resource_path, resource_version)
        REFERENCES catalog(resource_path, resource_version)
)
PARTITION BY RANGE (timestamp);
```

---

## SQLModel Python Definitions

```python
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
```

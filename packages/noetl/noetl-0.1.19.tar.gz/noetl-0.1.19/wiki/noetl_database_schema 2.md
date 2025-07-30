
# NoETL Database Schema

## Catalog and Event Versioning System

This document outlines the schema for cataloging versioned workflow resources and recording associated events.

---

## Tables

### `resource_type`

Defines allowed resource categories in the system.

```sql
CREATE TABLE resource_type (
    name TEXT PRIMARY KEY
);

-- Default values
INSERT INTO resource_type (name) VALUES
    ('playbook'),
    ('workflow'),
    ('target'),
    ('step'),
    ('task'),
    ('action');
```

---

### `event_type`

Defines event types and their associated message templates used for rendering human-readable logs or notifications.

```sql
CREATE TABLE event_type (
    name TEXT PRIMARY KEY,
    template TEXT
);

-- Default values
INSERT INTO event_type (name, template) VALUES
    ('REGISTERED', 'Resource {{ resource_path }} version {{ resource_version }} was registered.'),
    ('UPDATED', 'Resource {{ resource_path }} version {{ resource_version }} was updated.'),
    ('UNCHANGED', 'Resource {{ resource_path }} already registered.'),
    ('EXECUTION_STARTED', 'Execution started for {{ resource_path }}.'),
    ('EXECUTION_FAILED', 'Execution failed for {{ resource_path }}.'),
    ('EXECUTION_COMPLETED', 'Execution completed for {{ resource_path }}.');
```

---

### `catalog`

Holds the payload of versioned resources such as workflows and playbooks.

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

---

### `event`

Stores emitted events related to resource registration, execution, etc.

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

## Files Referenced

- `catalog_schema.sql`: SQL DDL with default inserts
- `catalog_models.py`: SQLModel Python definitions
- `catalog_spec.md`: Specification overview


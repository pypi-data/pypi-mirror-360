# NoETL Playbook Submission Endpoint & Versioning

## Requirements

- Create a FastAPI endpoint `/api/v1/playbook` that accepts converted playbook JSON payloads.
- Create CLI-side support to convert YAML playbooks to JSON and submit them.
- Enable Registration `payload` Postgres table with `path`, `version`, `template`, and content as `jsonb`, ensuring only new versions are saved.
- Use an `event_source` table for capturing ingestion events, partitionable for scalability.
- Support both raw `SQL CREATE TABLE` statements and `SQLModel` model classes for the tables.
- Version control logic that compares content and returns the current or updated version.



## FastAPI Endpoint – /api/v1/playbook

We add a new **FastAPI** POST endpoint at `/api/v1/playbook` for playbook submissions. This endpoint accepts a JSON payload representing a workflow playbook (the CLI will convert the user’s YAML to JSON before sending). The incoming JSON is expected to include a unique **path** (playbook identifier), an optional template name, and the workflow definition content (e.g. environment, variables, tasks, steps, etc.). For example, a submitted JSON might look like:
```yaml
{
  "path": "analytics/daily_report",
  "template": "default",
  "environment": { /* ... */ },
  "variables": { /* ... */ },
  "tasks": { /* ... */ },
  "steps": [ /* ... */ ]
}
```

**Input Handling & Validation:** Inside the endpoint, we parse the JSON into its components. We extract the top-level path (and optional template) and treat the remainder of the JSON as the playbook content. This `content` contains the actual workflow DSL (environment, variables, tasks, steps, etc.). We then validate the content against our DSL schema or Pydantic models to ensure it’s well-formed (e.g. contains required keys like steps, properly structured tasks/actions, etc.). This safeguards that only valid playbooks are stored. (The NoETL design already anticipated including metadata like a version in playbooks, so we leverage that by managing `version` in the storage layer.)

**Duplicate Detection:** The endpoint implements **idempotent** behavior for playbook submissions. It checks the payload table (see schema below) to see if a playbook with the same path **and identical content** already exists. This is done by querying for an existing row matching the path and comparing the stored JSON content (we can utilize PostgreSQL’s JSONB equality to compare structure, or compute a hash of the content). If an identical entry is found, we do **not** create a new version. Instead, the API returns the existing version number along with a message indicating the playbook is unchanged. This way, repeated submissions of the same playbook are **idempotent** and do not fill the catalog with duplicates.


**Versioning Logic:** If the submitted playbook content is new (i.e. the `path` is new or content differs from the latest version), the endpoint will create a **new version** entry. We determine the next version by finding the current highest version for that `path` in the payload table (or 0 if none) and incrementing it. Each distinct content change results in a new version number, preserving a history of changes ￼. We then insert a new record into the `payload` table with the given path, the computed `version` number, the optional template, and the JSON content.

**Event Logging:** Regardless of whether a new version was created or an existing one reused, each submission attempt is recorded in an **event_source** table for auditing and tracking. We insert a new event row with details such as the playbook path, the timestamp of submission, the resulting version number, and a status message. For example, the status might be **"CREATED"** for a new version or **"UNCHANGED"** if the content was identical to an existing version. This event log allows us to track when playbooks are registered or updated, and it can be used for monitoring or debugging submission history.

**Response:** The API responds with a JSON indicating the outcome. For example, on success it might return:

```json
{ 
  "path": "analytics/daily_report", 
  "version": 3, 
  "message": "Playbook registered as version 3" 
}
```

If the content was unchanged (duplicate), it could return the existing version with a message like `"Playbook already up-to-date (version 3)"`. In both cases, the client (CLI) receives the version number of the playbook in the catalog.

See the code below that illustrates the endpoint implementation in FastAPI (using an APIRouter for version 1 of the API):

```python
from fastapi import APIRouter, HTTPException
from datetime import datetime
from sqlmodel import Session, select
from .models import Payload, EventSource  # SQLModel classes for tables

router = APIRouter(prefix="/api/v1", tags=["Playbooks"])

@router.post("/playbook")
async def submit_playbook(playbook: dict):
    # Extract fields
    path = playbook.get("path")
    template = playbook.get("template")
    if not path:
        raise HTTPException(status_code=400, detail="Missing playbook path")
    # Separate content (everything except path and template)
    content = {k: v for k, v in playbook.items() if k not in ("path", "template")}
    # (Optionally validate content structure here against DSL schema)

    # Start database session (example uses sync session for simplicity)
    with Session(engine) as session:
        # Check for identical existing playbook
        stmt = select(Payload).where(Payload.path == path, Payload.content == content)
        existing = session.exec(stmt).first()
        if existing:
            version = existing.version
            # Log event as unchanged
            event = EventSource(path=path, version=version, status="UNCHANGED", timestamp=datetime.utcnow())
            session.add(event)
            session.commit()
            return {"path": path, "version": version, "message": "Playbook already exists (version %d)" % version}
        # No identical entry, determine new version
        stmt = select(Payload).where(Payload.path == path)
        all_versions = session.exec(stmt).all()
        new_version = (max([p.version for p in all_versions]) if all_versions else 0) + 1
        # Insert new payload entry
        new_payload = Payload(path=path, version=new_version, template=template, content=content)
        session.add(new_payload)
        # Log create event
        event = EventSource(path=path, version=new_version, status="CREATED", timestamp=datetime.utcnow())
        session.add(event)
        session.commit()
        return {"path": path, "version": new_version, "message": f"Playbook registered as version {new_version}"}
```

In a our implementation, the database operations would be asynchronous and use transactions, and the content validation would be more robust. The above is a simplified illustration. The important part is that the logic ensures each playbook `path` is versioned and not duplicated, and every submission is recorded.

Finally, we integrate this router into the FastAPI application. In the application startup (e.g. `create_app()` in `noetl.server.app`), include the router:

```python
from noetl.server.api import catalog_router

app.include_router(playbook_routes.router)
```

This registers the `/api/v1/playbook` endpoint with the app. Now, the server can handle playbook submissions as defined.

## Database Schema for Catalog

To support this feature, we introduce two new tables in the PostgreSQL database: `payload` and `event_source`. We will add their creation SQL to the database initialization (e.g., in the `schema_ddl.sql` script) and define corresponding ORM models using `sqlmodel.SQLModel`. Using JSONB for content storage allows flexible querying of playbook structure if needed, while still enforcing a schema at the application level.

### Catalog Table – Versioned Playbooks, Workflows, Targets

The payload table stores each playbook’s content and manages versioning. Its schema is:
- **path** – TEXT, the unique identifier or name for the playbook. (This, together with version, forms the primary key to allow multiple versions per path.) .  

    path-style with type prefixes for readability and folder-friendly usage:
    - Playbook: /catalog/playbooks/test_public_api
    - Workflow: /catalog/workflows/email_digest
    - Target: /catalog/targets/high_priority  

    This makes it easy to:
    - Map to filesystem-like structures
    - Store in GCS buckets (or mount points)
    - Serve via REST API paths directly
    - Reuse same path to fetch DSL from /usr/data/catalog/playbooks/... or gs://...

Then use type + path in combination to resolve exactly what the resource is.


- **version** – INTEGER, the version number of this entry. This is auto-incremented per path (i.e. each time a given path is updated, it gets the next version number). We do not reuse or globally increment versions, so each playbook has an independent version sequence.
- **template** – TEXT (nullable), an optional field to indicate a template name or category, if this playbook is based on a template or meant to serve as one. This can be used for filtering or informational purposes.
- **content** – JSONB, the full playbook DSL content (excluding the above metadata). This JSON is the validated workflow definition that can be executed by the NoETL engine.

We designate (`path`, `version`) as the **primary key** to ensure uniqueness of each version record. We could also add a unique index on (`path`, `content`) if we want to enforce that the same content for a path isn’t stored twice, but since we handle that logic at insertion, the primary key on version suffices. The table will typically be queried by `path` (to get latest version or history) and occasionally by `path+version` to retrieve a specific version.

#### SQL DDL – Create catalog Table:
```sql
CREATE TABLE IF NOT EXISTS catalog (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    path       TEXT NOT NULL,                           -- global unique path for lookup
    kind       TEXT NOT NULL CHECK (kind IN ('playbook', 'workflow', 'target')),
    version    INTEGER NOT NULL,
    source     TEXT DEFAULT 'inline',                   -- e.g. 'inline', 'gcs', 'filesystem'
    location   TEXT,                                    -- optional pointer to external content
    payload    JSONB NOT NULL,                          -- content itself (if inline)
    timestamp  TIMESTAMPTZ DEFAULT now(),
    UNIQUE (path, version)
);
```

In this design, whenever a new playbook is registered or updated, a new row is inserted. Old versions are retained for history (e.g., for auditing or potential rollback, or to allow the currently running worklows to complete their jobs). The combination of path and version uniquely identifies a playbook version. Storing the content as JSONB allows us to store the full flexible structure of the playbook and even query into it if needed (for example, to find playbooks that contain certain steps or use certain tasks, in future).

We also define a corresponding **SQLModel** class to use in our application code:
```python
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON

class Payload(SQLModel, table=True):
    __tablename__ = "payload"
    path: str = Field(primary_key=True)                        # part of PK
    version: int = Field(primary_key=True)                     # part of PK
    template: Optional[str] = Field(default=None, nullable=True)
    content: dict = Field(sa_column=Column(JSON))              # use JSON (mapped to JSONB in PG)
```
In SQLModel, using `Field(primary_key=True)` on both path and version marks them as a composite primary key. We map content to a JSON column (which SQLModel will create as JSON – we will ensure in Postgres it’s the JSONB type). This model will allow us to easily insert and query playbook entries in the FastAPI code.

### Event Source Table – Submission Events

The `event_source` table logs each playbook submission event with relevant metadata. Every time a user submits a playbook (via CLI or other means), we create an event record here, regardless of whether the playbook content was new or a duplicate. This table helps in tracking changes over time and debugging.

Proposed columns for **event_source**:
- **event_id** – BIGSERIAL, a unique event identifier (primary key). This auto-increments globally for each event.
- **path** – TEXT, the playbook path that was submitted.
- **version** – INTEGER, the version number that resulted from the submission. This corresponds to the playbook’s version in the payload table at the time of the event (if a new version was created, it will be that new version; if unchanged, it’s the current version that remained).
- **timestamp** – TIMESTAMPTZ, the date and time of the submission event (defaulting to NOW() on insert).
- **status** – TEXT, a brief status of the submission (e.g., "CREATED" for a new version, "UNCHANGED" for a duplicate submission, or potentially error statuses in the future). This tells whether the submission resulted in a new version or not.
- **meta** (additional metadata) JSONB 

We can include other fields as needed. For example, we might store the source of the event (source='CLI' vs other UI), the user ID who submitted (if authentication is in place), or a message. These are optional and can be added as needed by extending the table or by adding content to the meta field.

SQL DDL – Create event_source Table (Partitioned by Month):
```sql

CREATE TABLE IF NOT EXISTS event_source (
    event_id    BIGSERIAL PRIMARY KEY,
    path        TEXT NOT NULL,                  -- e.g. 'analytics/daily_summary'
    version     INTEGER NOT NULL,               -- playbook version
    type        TEXT NOT NULL,                  -- e.g. 'PLAYBOOK_REGISTERED', 'TASK_STARTED'
    status      TEXT NOT NULL,                  -- e.g. 'CREATED', 'UNCHANGED'
    source      TEXT DEFAULT 'cli',             -- e.g. 'cli', 'api', 'web'
    payload     JSONB NOT NULL,                 -- full playbook DSL or other event-specific content
    meta       JSONB,                           -- metadata (e.g., source, user, message)
    timestamp   TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (event_id)
)
PARTITION BY RANGE (timestamp);


-- Example partitions for event_source, one per month (create new ones as needed):
CREATE TABLE IF NOT EXISTS event_source_2025_04
    PARTITION OF event_source FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');
CREATE TABLE IF NOT EXISTS event_source_2025_05 PARTITION OF event_source
    FOR VALUES FROM ('2025-05-01') TO ('2025-06-01');
-- (In fact, you would set up a process to create a new monthly partition as time goes on)
```

In the above, the event_source table is declared with **PARTITION BY RANGE (timestamp)**, and we show example child tables for April and May 2025. This means any event with a timestamp in April 2025 goes into `event_source_2025_04`, and so on. Partitioning by month is a reasonable choice here to balance the number of partitions and the size of each. This design makes it easy to drop or archive old partitions (e.g., events older than a year) and keeps most queries (which typically focus on recent submissions) fast.

The corresponding SQLModel class for events:

```
from datetime import datetime
from sqlmodel import SQLModel, Field

class EventSource(SQLModel, table=True):
    __tablename__ = "event_source"
    event_id: Optional[int] = Field(default=None, primary_key=True)  # bigserial PK
    path: str = Field(index=True)          # index by path for querying events by playbook
    version: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str
    # Additional fields can be added here, e.g.:
    # source: Optional[str] = None
    # user: Optional[str] = None
```

We mark `event_id` as primary key (it will auto-increment). We also add an index on path to quickly retrieve all events for a given playbook. The timestamp uses a default factory to set current time. The model doesn’t explicitly handle partitioning – that is handled by the SQL DDL and the database itself – but whenever we insert an EventSource, PostgreSQL will route it to the appropriate partition based on the timestamp.

With these models in place, the FastAPI endpoint can create Payload and EventSource objects and use a session to add them to the database as shown in the earlier code snippet. This achieves a version-controlled storage of playbooks and an audit log of submissions, satisfying the requirement of multiple versions with proper tracking.

## CLI Integration (noetl.py)

On the CLI side, we ensure that the `noetl` tool can submit playbooks to this new endpoint. The CLI (implemented with Typer in `noetl.py`) already has a command (e.g. `register-playbook`) that takes a YAML file path as input. We will update/confirm this command to perform the following steps:
1.	**Load YAML and Convert to JSON:** The CLI reads the given YAML file from the local filesystem. For example, using `yaml.safe_load`, it parses the YAML into a Python dictionary (which is essentially the JSON structure). This dictionary will include the playbook definition – it should contain the path key (and optionally template) along with the workflow content. If the YAML is missing a path, the CLI should prompt an error or derive one (the path is essential as the primary ID in the catalog).
2.	**Extract Path (for logging):** The CLI may extract the path from the loaded data just to inform the user or ensure it’s present. (This is mainly a sanity check – the server will also validate that path is provided.) For instance, if payload_dict["path"] is not found, the CLI can abort and tell the user to include a path in the YAML.
3.	**Submit to REST API:** The CLI constructs the URL for the API endpoint. Following our design, this would be `http://<host>:<port>/api/v1/playbook`. (We use the versioned endpoint path.) The CLI then sends an HTTP POST to this URL with the JSON payload. This can be done using a helper like requests or an internal RequestHandler. In our project, we have a RequestHandler (in `noetl.shared.connectors.requestify`) which is a wrapper of HTTP client. We use that to send the request:

```python
import yaml, requests  # or RequestHandler utility
data = yaml.safe_load(open(path_to_yaml, 'r'))
url = f"http://{host}:{port}/api/v1/playbook"
response = requests.post(url, json=data)
```

The CLI will include options to specify the host/port (defaulting to localhost and the default port). By default, if running locally with Docker, host might be 0.0.0.0 and port 8080 as per the compose file.

4.	**Handle Response:** After posting, the CLI checks the HTTP status. On success (200 OK), the response body will contain the path and version (and message). The CLI then outputs a confirmation to the user, such as: _"Playbook analytics/daily_report registered as version 3."_ If the response indicates no new version (status message `"already exists"`), the CLI can inform the user that the playbook was already up-to-date (and perhaps show the version). On failure (non-2xx status), the CLI will print the error returned by the server.
5.	**Example Usage:** Once integrated, a user can run the CLI command to register a playbook:
```shell
$ noetl register-playbook path/to/playbook.yaml --host 127.0.0.1 --port 8080
```

The CLI will load `playbook.yaml`, send it to the server, and then print the result (version info or error).

This CLI flow is essentially already outlined in the project. We ensure the endpoint path matches our implementation (`/api/v1/playbook`). For instance, if previously the CLI was hitting `/api/playbooks`, we update it to `/api/v1/playbook` for consistency. The conversion to JSON and submission is handled automatically by the CLI code, so from the user’s perspective, they just provide the YAML file.

By integrating the above, we have a complete path from a user authoring a YAML playbook, running the CLI to register it, and the system storing it in the NoETL catalog with version control and logging. This implementation satisfies the requirements by providing robust version tracking (no duplicate entries for identical content) and an audit trail of submissions, while enforcing the structure of the playbook DSL.

## Integration into Project Layout:

- The new API route (FastAPI logic) can be placed in a module like `noetl/server/api/playbook_routes.py` and included in the application as described.
- The data models Payload and EventSource (SQLModel classes) can reside in a models module (for example, `noetl/server/api/models.py` or a shared models file) so that both the API and other parts of the app (or future features) can access them.
- The database initialization SQL (e.g., `data/noetl_postgres_db/schema_ddl.sql`) should be updated to add the `CREATE TABLE` statements for the new tables, so that the Postgres schema is up-to-date when the app deploys. Partition setup for `event_source` can also be done in that script or via a migration.
- The CLI (`noetl.py`) already has the command structure; we just ensure the endpoint URL is correct and perhaps improve error messages for missing `path`.

With these changes, the NoETL catalog will reliably store each playbook submission with proper versioning and allow retrieving the latest or specific versions on demand. This design meets the outlined requirements: supporting multiple playbook versions with unique path identifiers, preventing duplicate entries, and logging all events for observability. Each change to a playbook is tracked as a new version, and the system enforces that the playbook content conforms to the defined DSL schema. The event log, partitioned by time, will scale well as usage grows, enabling maintenance of the log data over the long term.
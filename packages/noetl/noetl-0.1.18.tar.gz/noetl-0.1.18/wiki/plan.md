# Development plan

## 1. Configuration Validation
- **Objective:**
Validate that the uploaded YAML configuration conforms to our agentic workflow DSL.
- **Approach:**
    - Use PyYAML to parse YAML files.
    - Define a data model using Pydantic to enforce required fields (e.g., apiVersion, kind, tasks, steps, etc.).
    - Provide clear error messages if validation fails.

- **Example:**
The code snippet below shows how to read a YAML file, parse it, and validate it using a Pydantic model.

## 2. Catalog and Payload Persistence
- **Persistence Options:**
    - **Filesystem:** We will use local storage for immediate development and testing.
    - **Cloud Storage Integration (e.g., Google Cloud Storage):** We will add a service later that mirrors local storage updates.

- **Catalog File:**
A JSON file (or similar) that records each payload’s ID, file path, metadata, and original configuration. This will allow you to update and reference payloads easily.

## 3. FastAPI Endpoints
Implement endpoints for:
- **Upload Payload:**
`POST /payloads/upload`
    - Accepts a YAML file using multipart/form-data.
    - Validates the config, saves it to the filesystem, and updates the catalog.

- **Update Payload:**
`PUT /payloads/{id}`
    - Validates an updated config, replaces the payload file, and updates the catalog.

- **Add Tasks/Actions:**
`POST /payloads/{id}/tasks`
    - Allows appending or updating tasks/actions within an existing payload.

- **Override Variables and Steps:**
`POST /payloads/{id}/override`
    - Allows altering variables or the step sequence for workflows.

## 4. Jinja2 for Template Rendering
Jinja2 can be used to render configuration templates dynamically (for example, when we need to interpolate environment-specific variables) or generate dynamic payloads.
- Define template files (e.g., in a "templates" directory).
- Use Jinja2 to render templates before validation or execution.

## 5. Example Code
Below is a simplified example of FastAPI app, configuration validation, and a simple upload endpoint:
``` python
# python
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, ValidationError, validator
import yaml
import os
import uuid
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Define the FastAPI app
app = FastAPI()

# Define directory to store payloads and the catalog file
PAYLOAD_DIR = Path("./payloads")
CATALOG_FILE = Path("./catalog.json")
PAYLOAD_DIR.mkdir(exist_ok=True)
if not CATALOG_FILE.exists():
    CATALOG_FILE.write_text(json.dumps({}))


class Playbook(BaseModel):
    apiVersion: str
    kind: str
    name: str
    environment: dict
    tasks: list
    steps: list

    @validator("tasks", "steps")
    def if_empty(cls, value):
        if not value:
            raise ValueError("Must not be empty")
        return value


def load_catalog():
    with open(CATALOG_FILE, "r") as f:
        return json.load(f)


def update_catalog(payload_id: str, data: dict):
    catalog = load_catalog()
    catalog[payload_id] = data
    with open(CATALOG_FILE, "w") as f:
        json.dump(catalog, f, indent=2)


TEMPLATES_DIR = Path("./templates")
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


@app.post("/payloads/upload")
async def upload_payload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        # Optionally, if the payload is a Jinja2 template, render it first
        # For example, choose a template or pass context; here we just use the raw file.
        config_str = contents.decode("utf-8")

        # If templates are used, e.g.,
        # template = jinja_env.from_string(config_str)
        # config_str = template.render(variable1="value1") 

        # Parse YAML
        config_data = yaml.safe_load(config_str)

        # Validate the configuration using the Pydantic model
        playbook = Playbook(**config_data)
    except (yaml.YAMLError, ValidationError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Generate a unique payload id and store the payload
    payload_id = str(uuid.uuid4())
    payload_file = PAYLOAD_DIR / f"{payload_id}.yaml"
    payload_file.write_text(config_str)

    # Update catalog with minimal required information (extend as needed)
    catalog_entry = {
        "id": payload_id,
        "name": playbook.name,
        "path": str(payload_file),
        "uploaded_at": os.path.getctime(payload_file)
    }
    update_catalog(payload_id, catalog_entry)

    return {"message": "Payload uploaded successfully", "payload_id": payload_id}


# Additional endpoints can be implemented in a similar manner.
# For example: update, add tasks, and override endpoints.

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
```
## 6. Next Steps
1. **Expand on Endpoints:**
Implement additional endpoints for updating payloads, adding tasks, and overriding variables/steps.
2. **Integrate Google Cloud Storage:**
When ready, add functions to mirror payload storage to Google Cloud Storage (for example, using the google-cloud-storage library).
3. **Enhance Validation:**
Expand the Pydantic model to include more detailed validations according to your DSL. Consider using custom validators if necessary.
4. **Error Handling and Logging:**
Add proper logging and error handling for production readiness.
5. **Testing and Documentation:**
Write tests to ensure your endpoints and validation logic work as expected. Document API endpoints and usage examples.

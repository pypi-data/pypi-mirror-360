# NoETL.io – Dynamic Agent Execution Engine
A lightweight, agentic state-machine engine for orchestrating task-based workflows using declarative playbooks.

- [**Part 1 Video**](https://drive.google.com/file/d/1PcTcTe__Eedy82x5vd_Eeemb4BRHnVQq/view?usp=sharing)
- [**Part 2 Video**](https://drive.google.com/file/d/1QL-st_l_mwAXQxHdafY4ZomEaKecxssh/view?usp=sharing)
- [**Part 3 Video**](https://drive.google.com/file/d/1Lcxi2p1oW-EXnQ4UJFo4dJtJ60J8oznk/view?usp=sharing)
---

- [NoETL DSL Design](noetl_dsl_design.md)
- [NoETL Architecture Overview](architecture_overview.md)
- [NoETL GitHub repository branch main](https://github.com/noetl/noetl/tree/main)
- [Codedex Learn](https://www.codedex.io/)

## What is noetl.io?

**noetl.io** is a dynamic state-event-driven workflow execution engine that bridges declarative automation and agentic AI workflows.

- **Playbooks**: Blueprints of execution. Think of them like *classes* in programming.
- **Workflows**: Instantiations of playbooks. Think *objects* with runtime-bound overrides.
- **Tasks**: Named sequences of actions, reusable like *functions*.
- **Actions**: One-off atomic instructions (like *lambda* functions).
- **Steps**: State transitions using rules to drive flow logic.
- **Rules**: Pre-Post-execution transitions defined with `case` and `run`.

---

## Concepts

### Playbook
```yaml
apiVersion: noetl.io/v1
kind: AgentPlaybook
name: openai_workflow
path: /catalog/playbooks/openai_workflow

environment:
  baseUrl: "https://api.openai.com/v1"
  model: "gpt-4"
  prompt: "What's the weather in Paris?"
  resultPath: "data/response.json"
  logLevel: INFO

variables:
  localUrl: "http://localhost:8000"

tasks:
  - name: query_openai
    description: "Send a query to OpenAI"
    runtime:
      mode: isolated
      reportUrl: "{{ variables.localUrl }}/callbacks/openai"
    run:
      - action: call_openai
        method: http
        endpoint: "{{ environment.baseUrl }}/chat/completions"
        headers:
          Authorization: "Bearer {{ secrets.OPENAI_API_KEY }}"
        body:
          model: "{{ environment.model }}"
          messages:
            - role: user
              content: "{{ environment.prompt }}"

  - name: save_response
    description: "Save AI response to file"
    run:
      - action: script
        script: "scripts/save_to_file.py"
        params:
          output: "{{ environment.resultPath }}"

steps:
  - name: analyze
    run:
      - task: query_openai
    rule:
      - case: "{{ result.success }}"
        run:
          - step: parse
      - case: "{{ not result.success }}"
        run:
          - step: handle_error

  - name: parse
    run:
      - task: save_response
    rule:
      - case: "{{ result.success }}"
        run: []  # Done
      - case: "{{ not result.success }}"
        run:
          - step: handle_error

  - name: handle_error
    run:
      - action: log
        method: log
        message: "{{ error.message }}"
        level: ERROR
    rule:
      - case: "{{ error.retryable }}"
        run:
          - step: analyze
```

### Runtime
Tasks or actions can declare runtime to specify isolated, async, remote, or plugin-driven execution:
```yaml
runtime:
  mode: isolated
  reportUrl: "http://localhost:8000/callbacks/result"
```

### Execution Model
Think **state machine**:
- **Steps** are states.
- **Rules** define post-execution transitions.
- **Case** matches conditions (if-then-else style logic).
- **Run** defines what to execute — including transitions to other steps.

### Transitions
```yaml
rule:
  - case: "{{ agent.done }}"
    run:
      - step: complete
  - case: "{{ not agent.done }}"
    run:
      - task: keep_working
```

### Workflow
A **workflow** is a live execution instance of one or more playbooks. It can:
- Override **variables** and **environment**
- Inject anonymous **steps** or **actions**
- Track and update **state** dynamically

### Extensions
- **Plugins** for runtime contexts (e.g. kubernetes, dask, airflow)
- **Environment templating** with Jinja2
- **Inline scripting** via method: script
- **Runtime-aware callbacks** (for async reporting)

## Goals for an Agent-Oriented Framework

- **Dynamic Transitions & Conditional Logic:**  
  Workflows must support conditional transitions—similar to how "when" clauses work in configuration management (like Ansible). This feature enables an agent to branch to different tasks or steps based on dynamic conditions evaluated at runtime.

- **Iterable/Loopable Task Sequences:**  
  Beyond executing an action once, an agent may need to repeat entire sequences until specific success criteria are met. For example, reattempting an API call until a desired response is received. This looping mechanism is similar to a while-loop in programming.

- **Context-Driven Parameterization:**  
  Reusability is enhanced by making tasks parameterized. The agent’s context (or state) can provide dynamic data such as query results or runtime variables. This allows tasks to be written once and applied in multiple scenarios without hardcoded values.

- **State Management & Autonomy:**  
  Effective state tracking is essential. Recording outputs from tasks, error flags, and progress checkpoints allows the agent to make decisions on the fly—such as whether to branch, retry, or end the process. This state can be persisted in JSON, databases, or other storage mechanisms.

- **Multi-Agent Orchestration:**  
  The system should support running several agent instances concurrently or sequentially. With isolated contexts for each agent instance, you can process different datasets or client IDs in parallel, similar to a fan-out pattern.

- **Modularity & Reusability:**  
  Decomposing complex workflows into smaller, reusable tasks and actions keeps the playbook modular. By defining common operations in a single location, multiple agent scenarios can invoke them with varying parameters.

- **Robust Error Handling & Logging:**  
  Decide if an error is retryable, and log detailed information to trace the agent’s decisions. The ability to log state changes, outcomes, and error details is crucial for troubleshooting and iterative improvements.

---

# Solution Overview: PostgreSQL to CSV Agent Workflow
[agent_playbook.yaml](agent_playbook.yaml)
This solution is an agent playbook designed to orchestrate a PostgreSQL-to-CSV export workflow. The playbook defines all the necessary configuration, tasks, and steps in a unified YAML file, allowing an autonomous agent to execute the workflow dynamically.

## Key Components

### 1. Environment Configuration
- **Database Settings:**  
  The environment section provides connection details (host, port, database name, user, password) to connect to a PostgreSQL instance.
- **Output Settings:**  
  It also specifies an output CSV path for exporting data and settings for logging, including dynamic log file names based on the agent’s identifier.
- **Logging Level:**  
  The log level is set to INFO to capture essential runtime details.

### 2. Task Definitions
The playbook includes three primary tasks:

- **create_table:**  
  - Purpose: To create a PostgreSQL table if it doesn’t already exist.
  - Details: Includes a SQL query for table creation.
  - Runtime: Configured with an isolated mode and a report URL for asynchronous callback reporting.

- **insert_record:**  
  - Purpose: Insert a sample record into the newly created table.
  - Details: Executes a simple insertion query.

- **export_to_csv:**  
  - Purpose: Export the entire table data into a CSV file.
  - Details: Runs a query to fetch the data and writes the output to the specified CSV file. The task is set up to include headers in the CSV.

### 3. Workflow Steps (State Management)
The workflow is divided into three sequential steps, implementing a state-machine style pattern:

- **initialize_db:**
  - **Actions:**  
    Executes the creation of the table and insertion of a record sequentially.
  - **Transition Rule:**  
    - If the operations are successful, the workflow transitions to the **export_step**.
    - Otherwise, it moves to the **handle_error** step.

- **export_step:**
  - **Actions:**  
    Uses the export task to transform the PostgreSQL data into a CSV file.
  - **Transition Rule:**  
    - If the export succeeds, the workflow ends.
    - If the export fails, the workflow diverts to the **handle_error** step.

- **handle_error:**
  - **Actions:**  
    Logs error details, including the error message and severity.
  - **Transition Rule:**  
    - If the error is marked as retryable, the process loops back to the **initialize_db** step for another attempt.
    - If the error is not retryable, the workflow terminates.

# NoETL System Architecture and Execution Flow

With the [NoETL DSL semantics and validation](noetl_dsl_design.md) in place, we outline the system’s architecture — i.e., how the FastAPI service runs a workflow defined in YAML. The architecture comprises the following components:

- **FastAPI Workflow Service:** The entry point is a FastAPI application that provides API endpoints for workflow operations. For example, an endpoint `/workflows/run` might accept a YAML playbook (or reference to one) and trigger its execution, possibly returning a workflow instance ID. Another endpoint might fetch the status or result of a workflow instance. FastAPI handles request/response, authentication, etc., and delegates workflow execution to the engine.

- **Workflow Engine (Orchestrator):** This is the core of the service, responsible for parsing the YAML, validating it, and executing the defined workflow logic. It can be implemented as a set of classes or modules:
  - **Parser & Validator:** When a workflow definition is received, the parser reads the YAML into an internal structure (e.g., Python objects for steps, tasks, actions). The validator then applies all rules described in [NoETL DSL](dsl_overview.md) (unique names, valid references, etc.). Only if the playbook is valid do we proceed; otherwise, the API returns a validation error to the user.
  - **Execution Context:** The engine maintains a context (state) during execution – this could include variable data (perhaps a dictionary of context variables that tasks can read/write), and the current execution state (which steps are active, which have completed). A context object (`context.py`) tracks things like input data, outputs, and any dynamic information needed for conditions.
  - **Rule Evaluator:** When executing a step, the engine evaluates that step’s `rule`. This involves evaluating each case’s Jinja2 condition against the current context. We will integrate a Jinja2 templating engine or a safe expression evaluator for this. Once a case condition is found true, the engine retrieves its `run` field and decides what to do:
    - If the run is a list of step names, those steps are scheduled for execution next. In a simple implementation, this could push those steps onto a stack or queue of "steps to execute". If multiple steps are listed, the engine can either execute them sequentially (one after the other) or spawn them concurrently (if we design the engine to handle parallel branches). **Concurrency:** To truly allow parallel branches, the engine might use async tasks or threads for each branch. Initially, we might implement it sequentially (for simplicity), but the design should not preclude running them in parallel. Each new step is executed with the same context (or a cloned context if branches should have isolated data).
    - If the `run` is a list of actions/tasks, the engine will execute each action in order. This likely calls into an **Action Handler** layer.
  - **Task Manager:** If the `run` list contains any task names (as opposed to inline action objects or step names), the engine will resolve each task name to its list of actions (from the tasks definitions) and then execute those actions. Essentially, referencing a task is like a macro call that inlines its actions at runtime.
  - **Action Handlers:** For each action encountered (either directly in a run or inside a task), the engine dispatches to the handler for that action type. We will implement a handler for each supported type of action:
    - e.g., an HTTP handler that takes `method`, `url`, `body`, `headers` and makes an HTTP request (perhaps using httpx library), returning the response (which can be placed into the context if needed).
    - a Postgres handler that uses a database connection to execute the given query.
    - etc.
These handlers should run synchronously or asynchronously depending on action nature. The result of actions can be stored in the context (for example, result of an HTTP GET could be saved as `context["response_data"]` to be used in subsequent steps or conditions).

  - **Logging & Event Emission:** As steps start, complete, and actions execute, the engine will log events. This serves two purposes: internal monitoring (progress tracking, debugging) and external logging for process mining/analysis. Each significant event (step transition, action performed, branch end) can emit an entry to an event log with timestamp, workflow instance ID, step name, action details, outcome, etc. This event log is crucial for later analyzing the workflow’s behavior or auditing.

- **Data Stores (if applicable):** The service might use a database to store definitions (playbooks), track running workflow instances, and persist state for long-running workflows. For example, if a workflow is long or needs to survive service restarts, the engine could checkpoint which step is next and what the context is. This is an advanced feature – initially, we might run workflows in-memory.
- **External Systems:** The action handlers will interact with external systems (APIs, databases, etc.) as needed. These external interactions are transparent to the workflow definition (which just says `action: http` etc.). In the architecture diagram, external systems (like external API endpoints, databases, message queues) are on the periphery, being invoked by actions.

**Execution Flow Example:** Below is a step-by-step outline of how a workflow instance executes in this architecture:
1.	**Workflow Submission:** A client (or another service) makes a request to FastAPI (e.g., POST `/workflows/run`) with a YAML playbook (or an identifier for a stored playbook) and any input data. The FastAPI handler invokes the **Parser/Validator** to load the YAML into the engine’s memory. If validation fails, an error is returned here and execution stops.
2.	**Initialization:** The engine creates a new workflow instance context. This includes setting any initial context variables (maybe from input data) and preparing to start at the designated **start step**. (We might designate the first listed step in YAML as the start, or have a special `start` step defined).
3.	**Step Execution Loop:** The engine enters a loop/recursion to execute steps until there are no more active steps:
- Take the next step to execute (initially the start step). Mark it as "current step". Log that the step has begun.
- Evaluate the step’s rule cases in order:
  - For each case, evaluate its Jinja2 condition against the current context. The first condition that evaluates to true determines the path. (If none is true, the step ends with no actions and no next step – an end state for that branch.)
- Once a matching case is found, retrieve its `run`.
  - **If `run` is a set of actions/tasks:** Execute each in sequence:
    - For each item in the list: if it’s a task name, look up the actions and execute them in order; if it’s an action, call the corresponding action handler to perform it. Update the context if the action produces output. Log each action execution (start, success/failure).
    - After all actions in the run are done, the step is considered completed. Because this case did not specify a step transition, this branch of execution will not proceed to a new step. (The engine will note that this branch has finished.) Control returns to either a parent branch or loop to check other branches.
  - **If run is a set of step names:** This is a transition. Consider the current step completed (log that it ended). For each step name in the `run` list:
    - Add that step to the set of active steps to execute. This could mean pushing them onto a stack or scheduling them asynchronously. Essentially, the current workflow branch now splits into one or multiple branches, one for each target step.
    - If multiple steps are listed, we have a **fork**. The engine will handle each of those steps in turn (or in parallel threads). Each new step will receive a copy of the current context (or shared context if we choose a global context – but typically, parallel branches might work on the same context unless explicitly separated).
- Continue the loop: pick the next step from the active set and repeat. If steps were added (from a transition) they will be processed. If an action run just completed with no transition, then that branch is done (no new steps added).
- The workflow ends when there are no more active steps to execute (i.e., all branches have either transitioned to a terminal step or ended with no next step). At that point, the engine can mark the workflow instance as **Completed**.
4.	**Completion and Result:** Once finished, the engine may compile results (for example, maybe the context holds some output variables that the workflow produced). The FastAPI endpoint then returns a response to the client indicating completion (and possibly output data or logs). If the workflow is asynchronous, the API might immediately return an ID and the results would be fetched later from another endpoint. The design allows both modes.
5.	**Concurrent Execution Model:** In the above loop, if parallel transitions are allowed (multiple steps in one run), the engine effectively has to manage multiple active steps at once. Initially, we might implement this by simply queueing them and executing sequentially (which achieves correctness but not true parallelism). However, because the model explicitly supports branching, the architecture is ready for concurrency. In a future iteration, we can use Python asyncio or background threads to run branches concurrently. We’d need to ensure thread-safe context or separate contexts per branch to avoid race conditions. This aligns with the Petri net semantics of concurrent tokens: the workflow engine should be able to handle tokens (execution threads) evolving independently when a step transitions to multiple next steps.

--- 

- **Architecture Diagram:** The architecture can be visualized as a flow of control from the API layer down to the action execution. At a high level:
  - The **client** interacts with the **FastAPI service** (HTTP layer).
  - The FastAPI service passes the workflow definition to the **Workflow Orchestrator** module.
  - The orchestrator parses and validates the YAML (using the schema rules).
  - It then enters the **Execution Engine** which handles the Step logic and uses an **Action Executor** to perform each atomic action.
  - The Action Executor communicates with external systems (HTTP calls, DB queries, etc.).
  - Throughout the process, events are logged to an **Event Log** (which could simply be console log or a structured log storage).
  - Once done, control unwinds back up to FastAPI which returns the outcome.

![Local Diagram](./images/arch_diag.png)

(_An illustrative diagram would show the FastAPI request coming in, hitting the workflow engine, which then cycles through [Step -> Rule -> Case -> Action] and possibly branching out to multiple steps, before finishing._)

This architecture ensures a clear separation of concerns: FastAPI deals with request/response and user interaction, the workflow engine deals with the business logic defined in the YAML, and the action handlers deal with the external side effects. It is extensible (new action types can be plugged in, new steps can be added without changing engine logic), and debuggable (since every transition and action is explicit and logged).

---

The service will be a **Python-based workflow orchestration system** built on FastAPI (for a RESTful API) with Jinja2 for templating of workflow definitions.   
The service reads a declarative YAML playbook describing a workflow (with environment, tasks, steps, etc.) and executes it according to the defined logic. The architecture separates tasks (groups of actions) from actions (atomic operations) and supports conditional branching, parallel execution, and error handling.   
We will use FastAPI to provide endpoints for job submission, status checking, and callbacks, and we will employ Postgres storage event sourcing to log all workflow events. 

Key components include:
- **FastAPI Server** to handle inbound requests (start workflow, get status, health checks, etc.) and to serve as a callback receiver for external tasks.
- **Workflow Orchestrator** (the Job class) to manage end-to-end execution of a playbook: initializing context, iterating through steps, and coordinating task execution (potentially in parallel).
- **Event Store** (Google Storage, Postgres, MongoDB, Firestore) to record events such as job start, step start/completion, task results, and errors. This acts as the single source of truth for workflow state and history.
- **Template Engine** (Jinja2) integration for dynamic fields: configuration values, conditional expressions, and even control flow decisions will use Jinja2 templating syntax {{ ... }} evaluated against the current context.

**Separation of concerns:** FastAPI for presentation/API layer, a core engine for workflow logic, and the database for persistence. Multiple workflows can run in parallel, and tasks within a workflow can execute concurrently when possible. All state changes go through the event-sourcing mechanism, improving reliability and auditability (every action is logged as an event).


## Execution Engine Design

## Core Components and Modules

the service structured into core modules each handling a specific aspect of the workflow processing:

- **Context Manager (Context class)** – This module (extending `context.py`) holds the workflow configuration and runtime state in a structured way. It merges the static playbook definitions with dynamic data (variables, loop indices, etc.) and makes them accessible via dictionary-like keys. The **Context** is responsible for scoping (`job-level`, `step-level`, `task-level` contexts) and for providing values to Jinja2 templates. For example, when a new step is started, a sub-context is created with `Context.new_step_context()` that filters the relevant tasks for that step and carries forward necessary state. The Context will be extended to evaluate conditional expressions and to inject runtime values (e.g., results of previous tasks) for templating. It may also expose a method to evaluate a Jinja2 expression against the current context (using the interpreter module) to support dynamic routing or conditional task execution.
- **Interpolation / Template Engine (interp.py)** – This module provides functions to load and render templates with Jinja2. It supports loading a YAML file or string and replacing placeholders using a context. We will use `process_payload` (from `interp.py`) to initially process the input playbook: it can apply any top-level overrides and render the template with provided variables. We will extend this to possibly allow partial rendering: some parts of the playbook (like task parameters) can be rendered immediately, while others (like conditional expressions that depend on runtime results) will be stored as template strings to be rendered later. The Interpreter module will also host any custom Jinja2 filters (for example, the existing `dict2list` filter) and we can add more filters or functions to assist in templating logic as needed (e.g., a filter to check existence of a file, etc.).
- **Job Orchestrator (Job class - or we can rename/add Dispatcher)** – The `Job` class (from `job.py`) is the **primary orchestrator** for a workflow execution. When a new job is created, it processes the payload (YAML) into a **Context** and initializes a `State` (event manager). The `Job.execute()` method is responsible for iterating through the workflow steps and executing each step in order. Currently, this is sequential; we will extend it to support dynamic step ordering (based on conditions) and possibly parallel step execution when steps are independent. The `Job` will also manage a background task (via `asyncio`) for persisting state/events: in the code, `Job.start_worker()` launches an asyncio task that consumes a queue of state events and writes them out asynchronously. We will continue using this pattern to decouple event logging from the main execution flow. The FastAPI request to start a workflow will create a `Job` (running in-process), and either run it to completion asynchronously or return a job ID for the client to poll (depending on the API design). The `Job` class will be extended with methods or logic to handle pausing and resuming (for callback tasks, described later) and to incorporate new control flow instructions (like skipping to a step, or breaking out of the loop on a condition).
- **Step Executor (Step class)** – Each workflow **step** groups one or more tasks along with associated control logic (e.g., run tasks in parallel, or conditional branching after tasks). We will extend a `Step` class which has an `execute()` coroutine. The `Job.execute()` already instantiates `Step(context=step_context, state=self.state)` for each `step`. The `Step.execute()` will be responsible for executing all tasks defined in that step, managing concurrency among tasks, and handling step-level conditions and errors. If the playbook step definition contains a condition (like `case: "{{ x > 5 }}"`), the `Step` executor will evaluate it using the `Context` before running tasks – if the condition is false, it may skip the tasks or route to an alternative step. Similarly, a step could have a pointer in the playbook, which the `Step` could communicate back to the `Job` to influence what step runs next (e.g., by storing the next step name in the context or returning it along with results). The Step will use the event system to log step start and completion or error. We will extend the Step logic to also check for any **step-level error handlers** (like a fallback step): if a task fails and an on_error step is specified, the Step can trigger that instead of propagating an error immediately.
- **Task Runner** – A **task** represents a unit of work within a step. In the playbook, tasks are defined globally (under a tasks: section) and a step references which task(s) to run. Each task has attributes like a name (id), a type (what kind of action to perform), a runtime mode (in-process, isolated, etc.), and parameters required for execution. We will design a Task runner component to execute a single task according to its actions' types and runtime. This could be implemented as a function or a class method (perhaps within the Step class or a separate TaskExecutor class). The Task runner will look at the task definition and dispatch to the correct execution mechanism:
  - For a Python function task (e.g., type "python" with a code reference), call the function directly (if in-process) or via subprocess (if isolated).
  - For a shell command task (type "shell"), use Python’s subprocess to run it if isolated.
  - For an HTTP call task (type "http" or "api"), perhaps use `httpx` to call the external service.
  - For any task, before execution, resolve any templated parameters using the current `Context` (via Jinja2).

The `Task` runner should return the task’s result (or status) which will be inserted into the `Context` (so that subsequent tasks or steps can access it via context variables). It will also push an event to the event store for task completion (including result or output, if not too large, otherwise reference link to the large outputs). We will incorporate **loop logic** here as well: if a task has a loop configuration (e.g., an array of items to iterate over), the Task runner will execute the task’s action repeatedly for each item (creating a sub-context for each iteration) ￼ ￼. This could be handled by the `Context.new_item_context()` method in the code (which sets up a loop item in the context) and running the task action in a loop.

- **Event and State Manager** – This part covers the event-sourcing backbone. The code hints at a `State` class and an `Event` class used to record execution progress. We will implement the Filebased and Postgres-backed storage by extending the `StorageFactory` and `Event/State` classes. In the current implementation, the default storage is a JSON file (since storage_type default is "json"). We will create a new storage type "postgres" in the StorageFactory that connects to a Postgres database. The `State/Event` classes will be updated to use an asynchronous database client to write events. Each event will include fields like: job_id, step name (or task name), event type (e.g., START_STEP, END_STEP, ERROR, etc.), timestamp, and a payload (JSON data with context or result details). For example, when a step starts, we enqueue an event with type "START_STEP", and when a task completes successfully, we record a "TASK_SUCCEEDED" event with the task output. The **event store schema** might consist of a single events table with a JSONB column for details, or separate tables for jobs, steps, and task results. A simple approach is an events table (id, job_id, sequence, event_type, timestamp, data) to store everything in order. This event log can later be queried to reconstruct the final state or to get real-time status updates for a workflow. (For quick status checks, we might also keep a lightweight **current state** in memory or cached in the database, e.g., job status and last update, but the source of truth remains the events).
- **FastAPI API Layer** – We will use FastAPI to wrap the orchestrator into a service. The CLI entry (noetl.py) already has a FastAPI app and router are set up. We will create endpoints such as:
  - `POST /jobs (or /workflows)`: to submit a new playbook for execution. The request could include the YAML (or a reference to a stored playbook). The handler will parse the YAML (using `interp.load_payload` or similar), instantiate a `Job`, and trigger its `execute()` asynchronously. It will immediately return a job identifier (allowing the client to poll or subscribe for results), or possibly stream events if using Server-Sent Events or WebSocket (optional extension).
  - `GET /jobs/{job_id}`: to fetch the current status or result of a job. This can read from the event store (e.g., check for any ERROR events or the final COMPLETED event) and return summary information, or even the collected results that the `Job.execute()` returns.
  - `POST /jobs/{job_id}/{task_id}/callback`: (for callback tasks) to receive an external call indicating a task is completed or providing results. This is part of the **callback runtime mode** handling (discussed below). The service would, upon receiving this, record an event that the waiting task has finished and unblock the workflow to continue.
  - Additionally, a health check endpoint (e.g., `GET /health`) can be provided for monitoring the service.

The API layer will run with Uvicorn, enabling concurrency through FastAPI’s async support. Each job could run in-process on the server (suitable for many light tasks or I/O-bound tasks). If heavy CPU-bound tasks are common, we might consider running each job in a separate process or thread (or using multiple Uvicorn workers) to utilize multiple CPUs – but that can be configured depending on deployment needs.

## Runtime Execution Modes

A key requirement is to support multiple **runtime modes** for executing tasks. Each task in the playbook can specify a runtime that tells the system how to run it. We will support at least three modes initially, with a design that allows adding more. The modes and their implementation plan are:

- **In-Process Execution**: The default mode where tasks run within the orchestrator process (synchronously or asynchronously). This is ideal for tasks that are quick or involve I/O that can be awaited (like HTTP calls, database queries, etc.). When runtime: `"in-process"` (or if no runtime is specified), the Task runner will execute the task logic directly in Python. For example, if the task is defined to call a Python function or perform some calculations, the service will just await that function or run it in the event loop. In-process tasks can easily access the shared Context and do not incur inter-process communication overhead. We will use asyncio to allow other tasks to run concurrently while one task awaits I/O. Essentially, each in-process task can be an async function or a normal function; if it’s CPU-bound and long-running, we might internally offload it to a thread pool to avoid blocking the event loop. The simplicity of in-process tasks is that results can be returned directly and errors caught immediately in our code.

- **Isolated Execution**: In this mode, tasks run in a separate environment – either a subprocess, a container (Docker), or even a remote worker. The idea is to protect the main service from failures (or to run untrusted code safely), and to allow parallelism beyond the Python GIL for CPU-heavy tasks. For runtime: `"subprocess"` (for example), the Task runner will spawn a new process using subprocess. Popen or the `asyncio.create_subprocess_exec` if available for `async`. It will pass necessary inputs (perhaps via command-line args, environment variables, or by writing a temp file) and then wait for the process to complete. The `stdout/stderr` can be captured for logging. Once done, the process exit code and output will determine success or failure of the task. This isolated mode can also be implemented with containers: e.g., if runtime: `"docker"`, we could use the Docker SDK to run a container with a given image that performs the task. In either case, the service will treat it similarly to a subprocess (just an external execution). The workflow will likely await the completion of the subprocess (so it’s asynchronous from the perspective of the FastAPI server thread). If multiple tasks are isolated, they can indeed run truly in parallel (multiple OS processes). We must handle error cases (non-zero exit codes, timeouts, etc.) and ensure to kill or clean up processes if a job is cancelled. A sandboxing or container mode is useful for long-running or CPU-bound tasks. We’ll design the Task execution to branch out: if `task.runtime == "isolated"`, use the appropriate mechanism (which can be extended easily if new isolation types are added, e.g., a Kubernetes job).

- **Callback (Asynchronous/External) Execution**: In this mode, the workflow task is performed by an external system or service, and our orchestrator is **not actively running the task code** – instead, it waits for a notification. For runtime: `"callback"` tasks, the general pattern is:
	1.	The orchestrator triggers the task by sending a request or message to an external service (for example, calling a webhook that initiates some job, or putting a message on a queue). The task definition will include the details necessary (perhaps an URL to call, or it may be predetermined how external systems know about this task).
	2.	The orchestrator then **pauses** the execution of this step and does not have a result yet. It records an event that the task is "pending external completion" and likely persist this state.
	3.	The external system will perform the work and, upon completion, send a callback to a designated API endpoint on our service (e.g., `POST /jobs/{job_id}/{step_id}/{task_id}/callback` with the result data).
	4.	Our FastAPI callback handler will locate the waiting job and task (using the job_id, step_id and task_id), update the `Context` with the result data, and record a completion event. Then it will signal the orchestrator to resume.

Implementation-wise, to achieve this pause/resume, we have a few options. One approach is to have the Task runner return a _Future_ or use an `asyncio.Event` that the callback will set. For example, when a callback task is invoked, we could create an `asyncio.Future` and store it (perhaps in a dictionary keyed by job_id and task_id). We also enqueue a special `"waiting"` state in the event store. The `Task` runner does not immediately have a result, so it awaits the Future. Meanwhile, the main FastAPI thread returns to the event loop (allowing other jobs to proceed). When the external call hits our callback endpoint, we fulfill the Future (set the result or exception), which unblocks the awaiting task in the event loop. The workflow can then continue to the next tasks or steps. This design transforms the external callback into a resumable awaitable, integrating with our async workflow. We will also incorporate timeouts or expiration for callbacks – if a callback never arrives within a specified time, the task should be marked failed or timed out. The event store will capture when a task switches to waiting and when it either completes or times out.

All these runtime modes will be abstracted such that adding a new mode is straightforward. For instance, we might implement a base `TaskExecutor` class or simply handle it in a `run_task` function that switches on an enum or string for runtime. By designing a uniform interface (each mode ultimately yields a result or raises an error), higher-level logic (`Step` and `Job`) can remain unchanged regardless of runtime. This ensures the orchestrator is **extensible**. In summary, the in-process mode leverages Python’s async concurrency (multiple tasks can run concurrently on the loop), isolated mode leverages system-level parallelism (processes or containers), and callback mode allows integration with external asynchronous processes.

## Event Sourcing with Postgres, Mongo, Firestore, JSON, etc

We will implement a robust **event-sourcing layer** using Postgres to track the state and progress of workflows. Event sourcing means we persist each change of state as a separate event record, rather than just storing the latest status. This provides a full history of the workflow execution, which is invaluable for debugging, auditing, and replaying executions.

**Event Model**: We will identify important events in the lifecycle of a workflow and ensure to emit them:
- Job-level events: `INIT_CONTEXT` (workflow initialization), `START_JOB`, `JOB_COMPLETED` or `JOB_FAILED`.
- Step-level events: `START_STEP` (when a step begins), `STEP_SUCCESS` (on normal completion), `STEP_FAILED` (if not recovered by error handling).
- Task-level events: `TASK_STARTED`, `TASK_SUCCESS` (with output), `TASK_FAILED` (with error info), and `TASK_RETRIED` (if a retry occurs), `TASK_WAITING` (for callbacks or long polls).
- Other events: `LOOP_ITERATION` (if a loop yields an iteration event), or `INFO` events for logging custom messages.

All events will include a reference to the relevant context: job ID (always), and possibly step name and task name (if applicable), a timestamp, and a payload with details. For example, on `TASK_SUCCESS`, payload might include the task’s return value (or a summary of it) and execution duration. On `TASK_FAILED`, payload would contain the error message/trace and maybe which attempt (if retries attempted).

Database Design: We will use a single table workflow_events with columns like:
- `id` (serial or UUID) – unique event ID
- `job_id` (text or UUID) – workflow instance identifier
- `step_name` (text, nullable) – which step this event relates to, if any
- `task_name` (text, nullable) – which task this event relates to, if any
- `event_type` (text) – e.g., "START_STEP", "ERROR_TASK"
- `timestamp` (timestamptz) – event time (default now())
- `data` (jsonb, nullable) – additional context, such as the snapshot of certain context variables or the result/error. We might store the entire context state at certain points (like job start) to aid reconstruction, but that can be large; instead, we store minimal needed info and references.

Using PostgreSQL for this log gives us durability and query capabilities (we can query how many workflows failed at a certain step, etc.). It also allows multiple orchestrator instances to share the event log if we scale out the service.

**Integration in Code**: The `State` and `Event` classes in the existing code will be extended to use the database. For example, currently `Job.__init__` does: `StorageFactory.get_storage({"storage_type": ..., "file_path": ...})` to initialize a storage backend. We will implement a `PostgresStorage` class that the factory can instantiate when `storage_type` is `"postgres"`. This storage class will manage a connection pool to Postgres and have methods like `write_event(event)` or `start(job_context)` and `save(state_update)` which ultimately perform `SQL INSERT`s. The `State` class has methods `start()` (to write initial state) and `save(payload)` to append events. We’ll modify those to construct event records and call the storage. Since the orchestrator is asynchronous, we’ll use an async DB client for executing the insert statements without blocking. Transactions are simple as each INSERT stands alone (append-only log).

By recording every state change, we achieve strong auditability. In the future, this event log can also be used to create **materialized views** or summary tables for quick lookup of current state without replaying all events, similar to patterns described in event-sourcing literature. For now, we can also maintain in-memory the latest status of each job (for quick API responses), but the database will have the ground truth if the service restarts.

Additionally, event sourcing enables interesting possibilities: e.g., **replaying** a workflow by feeding the same events to a new context, or implementing a **compensation mechanism** where a separate process listens to events and triggers compensating actions on failures. While those are beyond the initial scope, our design will allow them since all events are stored.

## Concurrency and Control Flow

To meet the requirements of parallel execution and dynamic decision-making in workflows, the service will implement rich control flow constructs:

**Parallel Task Execution**: Within a single step, if multiple tasks are independent, we want to execute them concurrently to reduce overall runtime. We will introduce a way to declare tasks as parallel in the playbook. This could be an explicit flag in the step definition (e.g., `parallel: true` meaning all tasks listed in this step run in parallel), or by grouping tasks in a single step versus separate steps. The `Step.execute()` logic will check if tasks should run in parallel. If yes, it will launch all task coroutines together using `asyncio.gather` or similar concurrency primitives. For example, it might do: `await asyncio.gather(*(task_runner(task) for task in tasks))` so that all tasks run asynchronously. In case tasks are CPU-bound and not just async I/O, using `asyncio.gather` alone won’t do true parallel CPU execution due to Python’s GIL. However, those tasks would likely be designated as isolated runtime (subprocess) in which case our orchestrator launching them asynchronously still achieves parallelism (multiple subprocesses truly run in parallel). Another aspect is limiting concurrency if needed (to avoid resource exhaustion); we could incorporate a semaphore or a configurable max parallelism if the environment demands it, but by default we’ll assume it’s manageable or let the OS handle load for subprocesses. The result of parallel tasks will be collected once all complete, and then the step can proceed. If any task fails and others succeed, we need to decide the step outcome: depending on error handling settings (see Error Handling section), we might either fail the step immediately (cancelling other tasks if possible), or let others finish and then handle the failure.

**Conditional Execution (If/Else)**: The playbook may specify conditional logic, e.g., only run a step or task if a certain condition is true. We plan to support conditions using Jinja2 expressions or a simple expression language within the YAML. For instance, a step definition could have an `case: "{{ context.some_result == 'OK' }}"`. When the orchestrator reaches this step, it will evaluate that expression against the current Context (which contains results from prior tasks). If the condition is `false`, it will skip the tasks in that step entirely and possibly jump to an alternative step. We might allow an `else_step` or an `else` clause in the definition to specify what to do if the condition fails. Alternatively, the playbook author can define two separate steps and use the condition to decide which one is executed (this is like a branch in the workflow). To implement this, the `Job.execute()` will not necessarily just loop linearly over a list of steps; instead, we can maintain an index or a pointer to the next step name. One approach is to treat steps in the YAML as a list of step definitions that also have names, and we convert it into a directed graph of steps in memory (each step may have a pointer to the next step on success and an alternate next on failure or condition). By default, the "next step on success" is just the next in the list, but if a rule condition is false, we could alter the next pointer to skip some entries or jump to a named step. Implementation detail: after executing a step, the Job can decide which step to execute next based on the Context. We might extend the Context or Step result to include a flag like `context['next_step']` which, if set, tells the Job to go to a specific step name. For example, step1’s definition might say next: step3 and else: step2, so if its condition fails, we set `next_step = step2`, else `next_step = step3`. The Job loop would then find that step by name (we can index the steps by name in a dict for O(1) lookup rather than linear search). This dynamic routing using evaluated expressions lets us fork and join flows arbitrarily. It’s essentially implementing a small state machine as defined by the playbook.

**Loops and Iteration**: The workflow engine will support looping constructs to handle repetitive tasks. The playbook spec might allow a task or step to repeat for each item in a list or until a condition is met. In the existing `Context` code, tasks can have a loop field. For instance, a task might be defined with:
```yaml
tasks:
  - task: send_request
    - action: http
      method: GET
      url: "https://api.example.com/item/{{ loop.item }}"
      loop:
        items: ["item1", "item2", "item3"]
```

In this case, the engine should execute the task three times with the loop variable set to each item. The `Context.new_item_context()` method facilitates injecting the current loop item into the context for each iteration. We will extend the Task runner to detect a loop configuration: if present, it will iterate over the provided sequence. We will also support loop constructs at the step level (e.g., a step could repeat until a condition is satisfied, or for a fixed number of iterations). However, implementing a while loop at step level might be done by having a step that jumps to a previous step if condition isn’t met (which is another form of dynamic routing). Initially, focusing on task-level loops covers many use cases, like batch processing a list of inputs.

**Retries**: Retries are a special kind of loop specifically for error handling, but they tie into control flow. A task (or step) can specify a retry policy (max attempts, optional delay or backoff strategy). For example:
```yaml
tasks:
  - task: fetch_data
    - action: http
      method: GET
      retries: 3
      retry_delay: 5  # seconds
```

If fetch_data fails (throws an exception or non-zero exit), the orchestrator should automatically catch the failure and, if the retry count is not exhausted, wait `retry_delay` seconds (could use `asyncio.sleep` for non-blocking wait) and attempt the task again. The event log would record each attempt (perhaps a `TASK_RETRY` event with attempt number). We will implement this in the Task runner: wrap the execution in a loop that runs up to N times or until success. If the final attempt fails, then it’s treated as a true failure. Retries can also be specified at step level meaning “redo the whole step” – but that is less common; typically it’s at task granularity. We’ll concentrate retries at the task level configuration. The `Context` or task definition will hold the counters or flags for retry. We ensure not to confuse this with the loop for data items: both can exist (e.g., loop over items and retry each item if fails). The code will handle them separately (retries being inner loop around a single execution).

With these mechanisms, the orchestrator can handle complex flows:
- **Sequential flow** (default): tasks/steps run one after another.
- **Parallel flow**: tasks in the same step execute together.
- **Branching**: some steps are skipped or alternative steps taken based on conditions (evaluated via Jinja2 expressions in context).
- **Looping**: tasks repeating over data or until conditions met.
- **Waiting**: built-in via callback tasks for external asynchronous events.

All these need to interplay correctly. We will thoroughly test scenarios like: parallel tasks where one fails and one succeeds, conditionals that branch, nested loops, etc. The event store will be very useful for verifying that the flow of control matched expectations (since it logs each path taken).

## Extensibility and Modular Design

The service is being designed with **modularity and extensibility** in mind. Many aspects of the workflow engine will use a plugin or factory pattern to allow adding new functionality without modifying the core logic heavily, embracing the Open/Closed principle.

Here are key extensibility points and how we’ll implement them:
- **Action Types**: We expect to support various action types (Python function, shell command, HTTP call, database query, etc.). We will create an extensible registry or factory for action execution behaviors. For example, we might have a dictionary ACTION_TYPES where keys are type names and values are callables or classes that know how to execute that type. E.g., `"python": PythonFunctionTaskExecutor`, `"shell": ShellTaskExecutor`, `"http": HttpTaskExecutor`. The Task runner will look up the action’s type in this registry to delegate execution. To add a new type (say, "sql" for running a SQL query), a developer can implement a new executor class and register it. This design keeps the code generic. The interp.py module can also be extended to support loading external Python code or modules if playbook refer to them (for instance, if a task's action needs to call a user-defined Python function, we might load a module or use importlib given a path).

- **Runtime Modes**: As described, we have `in-process`, `isolated`, `callback`. If in the future we want a new mode (for instance, a **distributed queue** mode where tasks are pushed to a message broker and a separate worker service processes them), we can extend the runtime handler. We’ll implement runtime handling likely in a single place (the Task runner logic), where a simple if/elif or dispatch covers known modes. To add a new mode, we add another branch or better, use a similar registry approach as action types. For instance, a registry mapping runtime name to an executor implementation. In fact, we can combine type and runtime: the actual execution strategy could be determined by both. We might implement it such that each action type handler knows how to handle different runtimes, or have layered strategies (first choose runtime, then within that have sub-handlers for types). To keep it simple: we may treat "isolated" as just another attribute and use existing type executors but wrap them in a subprocess call. Alternatively, create specialized executors like `PythonTaskExecutor` has two methods `run_in_process()` and `run_isolated()` for example. Regardless, the design will allow adding new strategies.

- **Event Storage**: We are initially using Postgres for events, but the `StorageFactory` pattern allows other implementations. For example, a JSON file storage is already in use (as per `storage_type: "json"`). We will ensure the `StorageFactory` can register new storage classes. The `StorageFactory.get_storage()` is already designed to choose based on a config dict. We simply plug our `PostgresStorage` in. In the future, if one wanted to use Kafka or an event streaming platform as the event sink, we could add another storage type (though that would be a bigger change given our state management). The key is that the rest of the system (`Event` and `State` classes) interact with an abstract storage interface, so as long as that interface is satisfied (methods like `start()` to initialize a job record, `save(event)` to append), the internals can vary.

- **Output and Formats**: Currently, the output of a workflow could just be the final state or collected results in JSON. We might want to allow different output formats or post-processing of results. We can design the `Job` execution to produce a result (it already returns a results dict of step outputs). If needed, we can introduce post-execution plugins – e.g., a mechanism to take the results and do something like generate an HTML report, or trigger another workflow. For now, we will simply return the results via API or CLI, but making the final step pluggable (perhaps via an `"on_complete"` hook in the playbook) could be an extension point. The architecture could allow specifying in the playbook something like `on_complete: export_results` and we have a module that knows how to export results to a file or database. This is speculative, but the design will not preclude it.

- **Plugin Architecture**: To formalize extensibility, we can use Python’s dynamic import capabilities or even entry points. For example, define an entry point group in setup (this a library) for `noetl.task_plugins` – then external packages could register new action types that our service will auto-discover. In simpler terms, we might just have a configuration where new classes can be specified. A registry dictionary approach might suffice. We will also structure the code so that each major piece is decoupled:
- The Context and interpreter don’t need to know about task execution details.
- The Job orchestrator doesn’t need to know specifics of how a task's action of type X runs, it delegates to Task runner.
- The Task runner doesn’t need to know how the event store works, it just fires events.
- The State/event manager doesn’t care what a task or step is, it just stores events.
This decoupling means a change in one area (like adding a new event type, or a new task kind) doesn’t ripple unnecessary changes through other areas.

- **Modifying Existing Modules**: We will extend the uploaded files accordingly:
- In `context.py`, we may add methods to evaluate conditions (e.g., a method `check_condition(expr: str) -> bool` that uses Jinja2 Template to render the expression with the current context and then truthiness) and to perhaps update or get results more conveniently. The context might also be extended to carry a pointer to the next step if dynamic routing is set by a step.
- In `interp.py`, we might add support for evaluating small templates on the fly (maybe a convenience function to render a string template with current context) since we will need to evaluate conditional expressions during execution. The `render_template` function can serve this purpose by passing it the expression string.
- In `job.py`, we will modify the `Job.execute` loop. Right now it assumes a simple sequential flow through a list of steps. Later, we will also integrate parallel execution if a step says so: that logic will be inside Step.execute, which Job simply awaits.
Additionally, we will add to Job the logic for handling callback resume. Possibly the `Job.execute()` will need to await not just steps but also could be suspended if waiting for external input. We might handle that by the callback setting something in the context that the job loop periodically checks, or more directly by the callback logic injecting the result and unblocking an await as described earlier.

- We will add new classes for `PostgresStorage` and a `TaskExecutor base if needed, integrating them via the existing factory patterns (like `StorageFactory`).
- Logging and monitoring: The code uses a logger; we will continue to use that for console logs. The event store is the formal log, but for debugging, logs are helpful. We should ensure logs contain the job and step identifiers (the `extra=self.context.scope.get_id()` in code have a structured logging with IDs).

In summary, by using factories (for storage, tasks) and designing the classes to be generic, we can extend the system in the future with minimal changes. The modular approach will allow adding new capabilities such as new actions, support for different databases or message queues, or even a different front-end (CLI vs HTTP) without reworking the core engine.

## Error Handling and Fallback Mechanisms

Error handling is crucial for long-running workflows. We will implement **structured error-handling** flow control as defined in the playbook, including retries, fallback steps, and proper failure reporting. The system should be resilient: a failure in one task doesn’t necessarily abort the entire workflow unless configured to do so.

**Task-Level Error Handling**: If a task fails (throws an exception in Python code, returns a non-zero exit in a shell, or an HTTP call returns an error status that we consider failure), the Task runner will catch that. The playbook may specify a `retries` count for the task – as described, the Task runner will attempt the execution again up to the limit, logging a warning event each time a retry happens. If all retries are exhausted and the task still fails, then we mark the task as failed. At this point, we consult the playbook for **fallback logic**. A task might have an `on_error` field, which could reference another task or an action to perform as a fallback. For example, a task might say `on_error: cleanup_temp_files` (referring to another task defined in the tasks list). If such a fallback is defined, the orchestrator will execute that fallback task immediately when the main task fails, before proceeding. The fallback task could be something like reversing partial changes or logging the issue to an external system. We will treat the fallback task as part of the same step (or possibly as its own step, but likely simpler as part of the step). If the fallback also fails, or if no fallback is provided, then the step is considered failed.

**Step-Level Error Handling**: On the step level, the playbook might declare an on_error step (or steps) to execute if any task in the step fails. In our design, if a task failure is not recovered by its own retry/fallback, the `Step.execute()` would catch the exception and see an on_error definition for the step. This could be a special step name or a list of tasks to run for recovery. For example:
```yaml
steps:
  - step: TransferFiles
    run: 
      - task: download_data
      - task: upload_backup
  - step: on_error
    run:
      - task: rollback_backup
      - step: EndWorkflow  # after handling error, jump to end or a specific cleanup step
```

In this case, if either download_data or upload_backup fails, the step’s on_error triggers: it will run rollback_backup task (attempt to undo changes) and then perhaps skip to EndWorkflow step, bypassing other normal steps. We will implement this by catching exceptions in Step.execute and, if on_error is present, executing those specified tasks (likely sequentially, and ignoring any further normal tasks in the step). We then need to communicate to the Job that after this step’s error handling, either the workflow should stop or jump to a given step. We can use the same mechanism of setting next_step in the context or returning it from Step.execute. If on_error.next is specified, we set that as the next step to run; if not, we might default to terminating the job after handling the error (since presumably it’s not recoverable enough to continue normal flow).

We will support terminal failure resolution: if a workflow ultimately fails (an error that isn’t caught by any error handler), the Job will record an ERROR_JOB event and mark the job as failed ￼. The Job.execute() should propagate the exception after logging if break_on_failure is true ￼ ￼, or if the design is to always stop on unhandled error. The provided code uses break_on_failure in Context (configurable) to decide whether to abort on first error or try to continue ￼. We will honor this flag: if break_on_failure is true (meaning the user wants a fail-fast behavior), then any unhandled task or step error will immediately stop the workflow and bubble up. If false, the orchestrator will attempt to continue with the next step even if one step failed (this is useful in scenarios where steps are somewhat independent and we want to gather as many results as possible despite some failures). Even in the continue case, we will still log the error events for the failed step/task, and the final job status might be “completed with errors” or just “failed” if any step failed (depending on interpretation – we might define that if break_on_failure is false, a job can end in a “completed” state even if some tasks failed, but capturing which ones failed in the event log). It might be more clear to mark the job as failed if anything failed, unless the playbook explicitly handles it. We’ll discuss with stakeholders, but likely if break_on_failure is false, the job runs all steps, and then we consider the job “completed” but some events are errors – the user can inspect those.

**Logging and Alerts**: The error handling will be tightly integrated with event logging. Using the event store, we can detect patterns of failures, and even implement alerts. The Astera guide on workflow orchestration notes the importance of alerts and notifications on errors ￼. In our plan, we won’t initially implement an alerting system, but we can suggest it for the future: e.g., a separate monitoring component that watches the event table for any ERROR_JOB events and sends an email or Slack message. Because we have all error contexts in the DB, it’s straightforward to plug such features later.

Testing Error Scenarios: We will create test playbooks to ensure the error handling works:
	- A task with a forced failure that has a retry count, to see it retry the specified times.
	- A step with multiple parallel tasks where one fails – ensure that the step on_error triggers after canceling any still-running tasks (for parallel, we would need to cancel the others if one fails and break_on_failure is true for that step).
	- A callback task where the callback never arrives – ensure it times out and marks failure.
	- Nested error handling: e.g., a task fallback task itself fails, causing step failure.

Cleanup and Finalization: We will also consider adding a global finally or cleanup step that always runs at the end of the workflow, if specified (common in some workflow systems). This could be represented in the playbook as a special step or a flag. If present, the orchestrator would ensure to execute it in a finally block of the Job (after all steps or after an error that causes abort). In code, this might be done in the finally: section of Job.execute (where currently they shut down the state worker). We could trigger a cleanup routine there if needed. This is optional and can be part of error handling design (to guarantee resource cleanup).

In summary, the error handling strategy is to make workflows resilient by using retries for transient errors, fallbacks for alternate actions when something fails, and clearly logging all errors with context. The playbook provides the instructions for what to do on errors, and the engine will carry them out, ensuring that an error in one part does not cascade uncontrolled. When an error is truly unrecoverable, the system will stop the workflow gracefully: mark the job as failed, record the error, and free any resources (stop any running tasks, close files, etc.).

## Playbook Definition and Templating

We will support a YAML-based playbook format to define workflows. The playbook will include sections for tasks (the reusable task definitions) and steps (the sequence or graph of execution using those tasks). It can also include other sections like variables and system (as seen in the code, these are used for templating and config overrides). We will either use the existing schema implied by the provided code or adjust it slightly for clarity, but maintain backward compatibility if that code is already in use.

**Playbook Structure**:
At minimum, the YAML will have:

```yaml
variables:
  # (optional) define any variables to be used in templating, e.g. environment-specific settings
tasks:
  - name: TaskName1   # or tasks: { TaskName1: { ... }, TaskName2: { ... } } using a dict
    - action: python      # type of action (could be "python", "shell", "http", etc.)
      runtime: in-process   # execution mode (default in-process if omitted)
      script: path/to/script.py  # or function to execute if type=python
      function: mymodule.myfunc  # (example: if we allow specifying a function to call)
      args: {"param1": "value1"} # parameters for the task
      loop:                   # optional loop config
       items: [1, 2, 3]     # iterate three times with loop.item = 1,2,3
      retries: 2              # optional retry count
      retry_delay: 5          # seconds between retries
  - task: TaskName2:
    - action: http
      runtime: isolated
      url: "http://example.com/api"
      method: POST
      body: '{"id": "{{ variables.run_id }}", "data": "{{ context.prev_result }}"}'
    ...
steps:
  - name: StepOne
    run: 
      - task: TaskName1
      - task: TaskName2   # run these tasks (could be sequential or parallel based on a flag)
    parallel: true                  # indicate they can run in parallel
    rule:
      - case: "{{ variables.run_flag }}"  # condition to execute this step
        run: 
          - step: StepTwo                   # name of next step if this one succeeds (optional if linear)
      - case: {{ on_error }}
        run:
          - task: CleanupTask      # run this task if any fail
          - step: EndStep                # jump to a cleanup step after handling error
  - name: StepTwo
    run: [ ... ]
    ...
  - name: EndStep
    run: 
     - task: CleanupTask
```

(This is a conceptual example; the actual format will be finalized in implementation.)

The tasks section defines each task once. We allow it as a list of task definitions or a mapping from task name to its definition. The Context class already handles both list and dict forms for tasks. Each task has a unique task name and its configuration: type, runtime, and any type-specific fields. For a Python task, fields might include a reference to the code to run (maybe inline or an import path). For shell, a command or script path. For http, a URL, method, headers, etc. We will decide on a set of common fields per type, but the playbook is declarative – it doesn’t contain actual code besides maybe short scripts or shell commands, making it declarative and easy to read.

The steps section defines the workflow logic. Each step has a step name (used for references and for logging). It then lists one or more task names under tasks to indicate what to run during that step. Additional keys control the flow:
- parallel (boolean) to run tasks concurrently.
- if (expression) to conditionally execute the step. We interpret this as: if the expression evaluates to false, skip to the next relevant step (possibly an else).
- We might also allow an elif/else structure, but it might be simpler to require separate steps for the alternate path with their own conditions.
- next to explicitly name the next step to go to after this one. This allows jumping over some steps or looping (if next refers to a previous step, that creates a loop).
- on_error to handle errors in this step. As described, it could contain a list of tasks to run if an error occurs, and possibly a next to go to after handling the error.

We will use Jinja2 templating heavily in these playbooks. Any string field can include {{ ... }} placeholders that will be replaced with values from the Context. For example, a URL or an argument can include a variable that was defined in variables or perhaps produced by an earlier task. We also support Jinja2 control flow in templates, though typically the YAML structure covers that (e.g., using the if field rather than writing a Jinja2 {% if %} block inside the YAML – the latter is possible but gets messy). The interpreter will do a first pass render of the playbook with the given variables and system context ￼. This handles static template usage (like injecting environment-specific values). For dynamic values that depend on runtime information (like results of previous tasks), we will evaluate those templates at execution time. To manage this, our plan is:
- Initially load the YAML and render with known static variables. Keep any placeholders that are truly dynamic as Jinja2 expressions in the Context (perhaps the Context could store a compiled Jinja template or just the string).
- When it’s time to use a field (say, when running a task), call a render function with the current context data. For instance, if a task’s body is "hello {{ context.user_name }}", by the time the task runs, context.user_name might have been set by a prior task. We then render it to get the actual body string.
- We will leverage functions like render_template in interp.py for this purpose ￼. That function uses Environment(undefined=DebugUndefined) which is great for preserving placeholders that can’t be resolved yet instead of failing. We can keep using this strategy.

The templating allows for dynamic routing as well. For example, the next step could be given as an expression: next: "{{ 'StepTwo' if context.success else 'EndStep' }}". Our engine will render that when determining the next step, resulting in the actual step name to go to. Essentially, anything that might change at runtime can be a template expression. We just need to document clearly which fields support Jinja2 and ensure that misuse (e.g., a template that doesn’t resolve to a valid step name) is handled (perhaps throw a clear error event).

We’ll provide documentation and examples of playbooks to users of this system so they know how to write them. The example above (or a refined version) will serve as a template. The design of the YAML is custom (specific to our orchestrator) but inspired by existing workflow tools (somewhat similar to AWS Step Functions definitions or Azure Durable Functions, but using YAML and Jinja for flexibility).

One more aspect is versioning and storage of playbooks: In a production setting, we might store playbooks in a database or git, and the service loads them by reference. For now, the assumption is the user supplies the YAML (via file or API request). We will use `yaml.safe_load` to parse it and our interpreter to handle templates. The system will treat the parsed playbook as read-only configuration (except templates that get resolved progressively). The Context contains this config and gets enriched with runtime data as execution proceeds.

In implementing this, we will reuse as much of the existing payload processing as possible. The noetl CLI currently expects a --config YAML and targets to run, which suggests it already parses YAML with tasks and steps. We see in usage examples (in the noetl.py comments) commands like noetl --target load_dict --config workflows/target.yaml, meaning run the target (task) load_dict. Our service will generalize this to running entire workflows by name. It’s likely the YAML format we design is aligned with what Job and Context expect. Indeed, Context.get_steps() simply returns self["steps"] ￼, and Context.get_tasks() returns all tasks with a unified list format. Context.new_step_context shows that in a step config, there’s a "tasks" key listing task names. So we will adhere to that: each step’s tasks is a list of names corresponding to those in the global tasks list.

Finally, we will ensure the playbook schema accounts for metadata like job naming, descriptions, etc. (perhaps under a top-level name or description field). Also, there might be a storageType or similar in the YAML to choose event store (the Context looks for “storageType” in config ￼), so if the user sets "storageType: postgres" in the YAML, the context will set storage_type accordingly and our Job will use Postgres storage. This is how we’ll toggle between JSON (maybe for local testing) and Postgres.

The playbook is a declarative specification of what to do, and our service is the runtime that interprets it. We will provide strong templating capabilities and control flow constructs in the spec, which, backed by the event-sourced engine, results in a powerful and extensible workflow system.

By building on the provided modules (noetl.py, context.py, interp.py, job.py and related components) and extending them, we will create a feature-rich workflow orchestration service. The plan covers the full stack: a FastAPI web service for interaction, an asynchronous engine for executing tasks in various modes, a database-backed event store for durability, and a flexible YAML+Jinja2 playbook format for users to define complex workflows. The architecture emphasizes modular design – making it easy to add new task types or execution modes – and reliability through event sourcing and careful error handling.

This design will result in a system where workflow definitions are easy to write and understand. Each component will be tested to ensure that parallelism, conditional logic, and error recoveries function as expected. With this plan, we can proceed to implement the service, iteratively test with sample playbooks, and refine the spec as needed. The end result will be a NoETL (not only, or no-code ETL) workflow service.


# NoETL System Architecture and Execution Flow

The NoETL system implements a rule-driven workflow engine based on the [NoETL DSL semantics](noetl_dsl_design.md). This document outlines how the system components work together to execute workflows defined in YAML.

## System Components

### 1. FastAPI Workflow Service

The entry point for the NoETL system is a FastAPI application that provides API endpoints for workflow operations:
- `/workflows/run`: Accepts a YAML playbook and triggers execution
- `/workflows/status/{workflow_id}`: Retrieves the status of a running workflow
- `/workflows/result/{workflow_id}`: Fetches the results of a completed workflow

The FastAPI service handles authentication, request validation, and delegates workflow execution to the engine.

### 2. Workflow Engine

The core component consists of several key modules:

#### 2.1 Playbook Parser and Validator

- **Parser**: Converts YAML into internal Python objects (Playbook, Step, Task, Action)
- **Validator**: Applies validation rules to ensure playbook correctness:
  - Unique step and task names
  - Valid references between steps and tasks
  - Properly structured rules and transitions
  - Correct action parameters based on action type

#### 2.2 Execution Context Manager

Maintains the state of execution, including:
- Environment variables from the playbook
- Variables created during execution
- Current execution state (active steps, completed steps)
- Results from executed actions

The context serves as the data store that Jinja2 expressions in rules and conditions evaluate against.

#### 2.3 Rule Evaluator

For each step execution:
1. Evaluates the step's rule cases in order
2. For the first matching case:
   - If `run` contains steps: schedules transition to those steps
   - If `run` contains tasks/actions: executes them within the current step
3. Handles branching logic for parallel execution paths

#### 2.4 Task Manager

- Resolves task names to their action definitions
- Manages the sequential or parallel execution of actions within tasks
- Tracks task completion status

#### 2.5 Action Executor

Provides handlers for different action types:
- **HTTP Handler**: Makes HTTP requests and processes responses
- **Postgres Handler**: Executes database queries and operations
- **Shell Handler**: Runs shell commands and captures output
- **Custom Action Handlers**: Extensible for additional action types

Each handler knows how to execute its specific action type and return results to be stored in the context.

#### 2.6 Event System

Emits events at key execution points:
- Workflow start/end
- Step transitions
- Task/action execution
- Errors and exceptions

These events enable monitoring, logging, and integration with external systems.

### 3. Data Persistence Layer

Optional components for persistence:
- **Playbook Storage**: Repository of workflow definitions
- **Instance Store**: Tracking of workflow instances and their state
- **Results Database**: Storage of workflow execution results

### 4. External Integration

The workflow engine interacts with external systems through action handlers:
- APIs (via HTTP actions)
- Databases (via database-specific actions)
- Local resources (via shell actions)
- Message brokers (via messaging actions)

## Execution Flow

### 1. Workflow Submission

1. Client submits a YAML playbook to the API
2. API validates request format and authentication
3. Parser loads YAML into Python objects
4. Validator ensures playbook correctness

### 2. Workflow Initialization

1. Engine creates a new workflow instance with unique ID
2. Initializes execution context with environment variables
3. Identifies starting step (first in sequence, or explicitly marked)

### 3. Step Execution Cycle

1. Engine begins with the starting step
2. For each active step:
   - Mark step as "executing"
   - Evaluate the step's rule cases in order
   - For the first matching case:
     - If `run` lists step(s): Schedule transition to those steps
     - If `run` lists task(s)/action(s): Execute them within current step
   - Mark step as "completed" after execution
   - If no case matches: End this execution branch

### 4. Task and Action Execution

1. For each task in a step's run:
   - Resolve task name to its action list
   - Execute each action sequentially (or in parallel if specified)
   - Store action results in context

2. For direct actions in a step's run:
   - Dispatch to appropriate action handler
   - Execute action with parameters
   - Store results in context

### 5. Branching and Parallelism

When a case transitions to multiple steps:
1. Engine creates a branch for each target step
2. Each branch executes independently
3. Branches may execute sequentially or concurrently
4. Workflow continues until all branches complete

### 6. Workflow Completion

1. Workflow is complete when all branches terminate
2. Engine compiles final results from context
3. API returns results or notification of completion
4. Events are emitted for workflow completion

## Implementation Considerations

### Concurrency Models

NoETL supports two concurrency models:
1. **Sequential**: Steps and branches execute one after another
2. **Parallel**: Steps with the `parallel: true` flag execute concurrently

For parallel execution, the engine can use:
- Python asyncio for non-blocking operations
- Threading for parallel task execution
- Process pools for CPU-intensive operations

### State Management

For long-running workflows:
- Checkpoint mechanism saves workflow state
- Resume capability restores execution from checkpoints
- Persistence layer maintains execution history

### Error Handling

The engine implements a robust error handling strategy:
- Action-level error capture
- Step-level error handling through rule cases
- Workflow-level error policies (retry, abort, continue)
- Comprehensive error reporting
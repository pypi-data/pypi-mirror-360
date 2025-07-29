
#
#
#
# from typing import Optional, Dict, List, Any
# from sqlmodel import SQLModel, Field, Column, JSON, TIMESTAMP
# from datetime import datetime
#
#
# class ResourceType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#
#
# class CatalogEntry(SQLModel, table=True):
#     resource_path: str = Field(primary_key=True)
#     resource_version: str = Field(primary_key=True)
#     resource_type: str = Field(foreign_key="resourcetype.name")
#     source: str = Field(default="inline")
#     resource_location: Optional[str] = None
#     content: Optional[str] = None
#     payload: dict = Field(sa_column=Column(JSON), nullable=False)
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     template: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# class EventType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#     template: str
#
#
# class Event(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     event_type: str = Field(foreign_key="eventtype.name")
#     event_message: Optional[str] = None
#     resource_path: str = Field(foreign_key="catalogentry.resource_path")
#     resource_version: str = Field(foreign_key="catalogentry.resource_version")
#     content: Optional[str] = None
#     payload: Optional[dict] = Field(sa_column=Column(JSON))
#     context: Optional[dict] = Field(sa_column=Column(JSON))
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#     class Config:
#         arbitrary_types_allowed = True
#
# # ---- Workflow Execution Core ----
#
# class ExecutionContext:
#     def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
#         self.data = initial_data or {}
#
#     def update(self, new_data: Dict[str, Any]):
#         self.data.update(new_data)
#
#     def get(self, key: str, default=None):
#         return self.data.get(key, default)
#
#
# class Token:
#     def __init__(self, step_name: str, context: ExecutionContext):
#         self.step_name = step_name
#         self.context = context
#
#
# class WorkflowExecutor:
#     def __init__(self, playbook: Dict[str, Any]):
#         self.playbook = playbook
#         self.tasks = playbook.get("tasks", {})
#         self.steps = {step["name"]: step for step in playbook.get("steps", [])}
#         self.tokens: List[Token] = []
#         self.context = ExecutionContext()
#
#     def start(self):
#         start_step = self.playbook.get("start") or list(self.steps.keys())[0]
#         self.tokens.append(Token(step_name=start_step, context=self.context))
#         self.run()
#
#     def run(self):
#         while self.tokens:
#             token = self.tokens.pop(0)
#             print(f"Executing Step: {token.step_name}")
#             self.execute_step(token)
#
#     def execute_step(self, token: Token):
#         step = self.steps.get(token.step_name)
#         if not step:
#             print(f"Step {token.step_name} not found!")
#             return
#
#         # Execute actions or tasks
#         actions = step.get("actions", [])
#         tasks = step.get("tasks", [])
#
#         for action in actions:
#             self.execute_action(action, token.context)
#
#         for task_name in tasks:
#             task = self.tasks.get(task_name)
#             if task:
#                 for action in task.get("actions", []):
#                     self.execute_action(action, token.context)
#
#         # Evaluate rules and proceed
#         rule = step.get("rule")
#         if rule:
#             for case in rule.get("cases", []):
#                 condition = case.get("condition", "true")
#                 if self.evaluate_condition(condition, token.context):
#                     run_steps = case.get("run", [])
#                     if isinstance(run_steps, str):
#                         run_steps = [run_steps]
#                     for next_step in run_steps:
#                         self.tokens.append(Token(step_name=next_step, context=token.context))
#                     break
#
#     def execute_action(self, action: Dict[str, Any], context: ExecutionContext):
#         action_type = action.get("type")
#         parameters = action.get("parameters", {})
#         print(f"Executing Action: {action_type} with params {parameters}")
#         # Dummy execution logic - real handlers would go here
#         result = {"status": "success", "output": f"Result of {action_type}"}
#         context.update(result)
#
#     def evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
#         # For now, naive evaluation: if "true", always pass
#         if condition.strip().lower() == "true":
#             return True
#         # Later: implement full Jinja2 or expression-based evaluation
#         return False
#
#
#
#
# ####
#
#
# from typing import Optional, Dict, List, Any
# from sqlmodel import SQLModel, Field, Column, JSON, TIMESTAMP
# from datetime import datetime
# import requests
# import subprocess
# import psycopg2
#
#
# class ResourceType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#
#
# class CatalogEntry(SQLModel, table=True):
#     resource_path: str = Field(primary_key=True)
#     resource_version: str = Field(primary_key=True)
#     resource_type: str = Field(foreign_key="resourcetype.name")
#     source: str = Field(default="inline")
#     resource_location: Optional[str] = None
#     content: Optional[str] = None
#     payload: dict = Field(sa_column=Column(JSON), nullable=False)
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     template: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# class EventType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#     template: str
#
#
# class Event(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     event_type: str = Field(foreign_key="eventtype.name")
#     event_message: Optional[str] = None
#     resource_path: str = Field(foreign_key="catalogentry.resource_path")
#     resource_version: str = Field(foreign_key="catalogentry.resource_version")
#     content: Optional[str] = None
#     payload: Optional[dict] = Field(sa_column=Column(JSON))
#     context: Optional[dict] = Field(sa_column=Column(JSON))
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#     class Config:
#         arbitrary_types_allowed = True
#
#
# # ---- Workflow Execution Core ----
#
# class ExecutionContext:
#     def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
#         self.data = initial_data or {}
#
#     def update(self, new_data: Dict[str, Any]):
#         self.data.update(new_data)
#
#     def get(self, key: str, default=None):
#         return self.data.get(key, default)
#
#
# class Token:
#     def __init__(self, step_name: str, context: ExecutionContext):
#         self.step_name = step_name
#         self.context = context
#
#
# class BaseActionHandler:
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         raise NotImplementedError
#
#
# class HttpActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         method = parameters.get("method", "GET").upper()
#         url = parameters.get("url")
#         data = parameters.get("data")
#         headers = parameters.get("headers", {})
#         if method == "GET":
#             response = requests.get(url, headers=headers)
#         elif method == "POST":
#             response = requests.post(url, json=data, headers=headers)
#         else:
#             raise ValueError(f"Unsupported HTTP method: {method}")
#         return {"status_code": response.status_code, "response": response.json() if response.content else {}}
#
#
# class PostgresActionHandler(BaseActionHandler):
#     def __init__(self, db_config: Dict[str, str]):
#         self.db_config = db_config
#
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         query = parameters.get("query")
#         if not query:
#             raise ValueError("No query provided for Postgres action.")
#         connection = psycopg2.connect(**self.db_config)
#         cursor = connection.cursor()
#         cursor.execute(query)
#         try:
#             result = cursor.fetchall()
#         except Exception:
#             result = []
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return {"result": result}
#
#
# class ShellActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         command = parameters.get("command")
#         if not command:
#             raise ValueError("No command provided for Shell action.")
#         completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
#         return {"stdout": completed_process.stdout, "stderr": completed_process.stderr, "returncode": completed_process.returncode}
#
#
# class ActionDispatcher:
#     def __init__(self, db_config: Optional[Dict[str, str]] = None):
#         self.handlers = {
#             "http": HttpActionHandler(),
#             "postgres": PostgresActionHandler(db_config=db_config or {}),
#             "shell": ShellActionHandler(),
#         }
#
#     def dispatch(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         handler = self.handlers.get(action_type)
#         if not handler:
#             raise ValueError(f"No handler for action type: {action_type}")
#         return handler.execute(parameters)
#
#
# class WorkflowExecutor:
#     def __init__(self, playbook: Dict[str, Any], db_config: Optional[Dict[str, str]] = None):
#         self.playbook = playbook
#         self.tasks = playbook.get("tasks", {})
#         self.steps = {step["name"]: step for step in playbook.get("steps", [])}
#         self.tokens: List[Token] = []
#         self.context = ExecutionContext()
#         self.dispatcher = ActionDispatcher(db_config=db_config)
#
#     def start(self):
#         start_step = self.playbook.get("start") or list(self.steps.keys())[0]
#         self.tokens.append(Token(step_name=start_step, context=self.context))
#         self.run()
#
#     def run(self):
#         while self.tokens:
#             token = self.tokens.pop(0)
#             print(f"Executing Step: {token.step_name}")
#             self.execute_step(token)
#
#     def execute_step(self, token: Token):
#         step = self.steps.get(token.step_name)
#         if not step:
#             print(f"Step {token.step_name} not found!")
#             return
#
#         actions = step.get("actions", [])
#         tasks = step.get("tasks", [])
#
#         for action in actions:
#             self.execute_action(action, token.context)
#
#         for task_name in tasks:
#             task = self.tasks.get(task_name)
#             if task:
#                 for action in task.get("actions", []):
#                     self.execute_action(action, token.context)
#
#         rule = step.get("rule")
#         if rule:
#             for case in rule.get("cases", []):
#                 condition = case.get("condition", "true")
#                 if self.evaluate_condition(condition, token.context):
#                     run_steps = case.get("run", [])
#                     if isinstance(run_steps, str):
#                         run_steps = [run_steps]
#                     for next_step in run_steps:
#                         self.tokens.append(Token(step_name=next_step, context=token.context))
#                     break
#
#     def execute_action(self, action: Dict[str, Any], context: ExecutionContext):
#         action_type = action.get("type")
#         parameters = action.get("parameters", {})
#         print(f"Executing Action: {action_type} with params {parameters}")
#         result = self.dispatcher.dispatch(action_type, parameters)
#         context.update(result)
#
#     def evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
#         if condition.strip().lower() == "true":
#             return True
#         return False
#
#
#
#
# ########################
#
#
# from typing import Optional, Dict, List, Any
# from sqlmodel import SQLModel, Field, Column, JSON, TIMESTAMP
# from datetime import datetime
# import requests
# import subprocess
# import psycopg2
# from jinja2 import Template
#
#
# class ResourceType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#
#
# class CatalogEntry(SQLModel, table=True):
#     resource_path: str = Field(primary_key=True)
#     resource_version: str = Field(primary_key=True)
#     resource_type: str = Field(foreign_key="resourcetype.name")
#     source: str = Field(default="inline")
#     resource_location: Optional[str] = None
#     content: Optional[str] = None
#     payload: dict = Field(sa_column=Column(JSON), nullable=False)
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     template: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# class EventType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#     template: str
#
#
# class Event(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     event_type: str = Field(foreign_key="eventtype.name")
#     event_message: Optional[str] = None
#     resource_path: str = Field(foreign_key="catalogentry.resource_path")
#     resource_version: str = Field(foreign_key="catalogentry.resource_version")
#     content: Optional[str] = None
#     payload: Optional[dict] = Field(sa_column=Column(JSON))
#     context: Optional[dict] = Field(sa_column=Column(JSON))
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#     class Config:
#         arbitrary_types_allowed = True
#
#
# # ---- Workflow Execution Core ----
#
# class ExecutionContext:
#     def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
#         self.data = initial_data or {}
#
#     def update(self, new_data: Dict[str, Any]):
#         self.data.update(new_data)
#
#     def get(self, key: str, default=None):
#         return self.data.get(key, default)
#
#
# class Token:
#     def __init__(self, step_name: str, context: ExecutionContext):
#         self.step_name = step_name
#         self.context = context
#
#
# class BaseActionHandler:
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         raise NotImplementedError
#
#
# class HttpActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         method = parameters.get("method", "GET").upper()
#         url = parameters.get("url")
#         data = parameters.get("data")
#         headers = parameters.get("headers", {})
#         if method == "GET":
#             response = requests.get(url, headers=headers)
#         elif method == "POST":
#             response = requests.post(url, json=data, headers=headers)
#         else:
#             raise ValueError(f"Unsupported HTTP method: {method}")
#         return {"status_code": response.status_code, "response": response.json() if response.content else {}}
#
#
# class PostgresActionHandler(BaseActionHandler):
#     def __init__(self, db_config: Dict[str, str]):
#         self.db_config = db_config
#
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         query = parameters.get("query")
#         if not query:
#             raise ValueError("No query provided for Postgres action.")
#         connection = psycopg2.connect(**self.db_config)
#         cursor = connection.cursor()
#         cursor.execute(query)
#         try:
#             result = cursor.fetchall()
#         except Exception:
#             result = []
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return {"result": result}
#
#
# class ShellActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         command = parameters.get("command")
#         if not command:
#             raise ValueError("No command provided for Shell action.")
#         completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
#         return {"stdout": completed_process.stdout, "stderr": completed_process.stderr, "returncode": completed_process.returncode}
#
#
# class ActionDispatcher:
#     def __init__(self, db_config: Optional[Dict[str, str]] = None):
#         self.handlers = {
#             "http": HttpActionHandler(),
#             "postgres": PostgresActionHandler(db_config=db_config or {}),
#             "shell": ShellActionHandler(),
#         }
#
#     def dispatch(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         handler = self.handlers.get(action_type)
#         if not handler:
#             raise ValueError(f"No handler for action type: {action_type}")
#         return handler.execute(parameters)
#
#
# class WorkflowExecutor:
#     def __init__(self, playbook: Dict[str, Any], db_config: Optional[Dict[str, str]] = None):
#         self.playbook = playbook
#         self.tasks = playbook.get("tasks", {})
#         self.steps = {step["name"]: step for step in playbook.get("steps", [])}
#         self.tokens: List[Token] = []
#         self.context = ExecutionContext()
#         self.dispatcher = ActionDispatcher(db_config=db_config)
#
#     def start(self):
#         start_step = self.playbook.get("start") or list(self.steps.keys())[0]
#         self.tokens.append(Token(step_name=start_step, context=self.context))
#         self.run()
#
#     def run(self):
#         while self.tokens:
#             token = self.tokens.pop(0)
#             print(f"Executing Step: {token.step_name}")
#             self.execute_step(token)
#
#     def execute_step(self, token: Token):
#         step = self.steps.get(token.step_name)
#         if not step:
#             print(f"Step {token.step_name} not found!")
#             return
#
#         actions = step.get("actions", [])
#         tasks = step.get("tasks", [])
#
#         for action in actions:
#             self.execute_action(action, token.context)
#
#         for task_name in tasks:
#             task = self.tasks.get(task_name)
#             if task:
#                 for action in task.get("actions", []):
#                     self.execute_action(action, token.context)
#
#         rule = step.get("rule")
#         if rule:
#             for case in rule.get("cases", []):
#                 condition = case.get("condition", "true")
#                 if self.evaluate_condition(condition, token.context):
#                     run_steps = case.get("run", [])
#                     if isinstance(run_steps, str):
#                         run_steps = [run_steps]
#                     for next_step in run_steps:
#                         self.tokens.append(Token(step_name=next_step, context=token.context))
#                     break
#
#     def execute_action(self, action: Dict[str, Any], context: ExecutionContext):
#         action_type = action.get("type")
#         parameters = action.get("parameters", {})
#         print(f"Executing Action: {action_type} with params {parameters}")
#         result = self.dispatcher.dispatch(action_type, parameters)
#         context.update(result)
#
#     def evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
#         try:
#             template = Template(condition)
#             rendered = template.render(context=context.data)
#             return rendered.strip().lower() == "true"
#         except Exception as e:
#             print(f"Condition evaluation error: {e}")
#             return False
#
# ###########
# # Event logging system
#
#
# from typing import Optional, Dict, List, Any
# from sqlmodel import SQLModel, Field, Column, JSON, TIMESTAMP, create_engine, Session
# from datetime import datetime
# import requests
# import subprocess
# import psycopg2
# import asyncio
# from jinja2 import Template
# import uuid
#
#
# class ResourceType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#
#
# class CatalogEntry(SQLModel, table=True):
#     resource_path: str = Field(primary_key=True)
#     resource_version: str = Field(primary_key=True)
#     resource_type: str = Field(foreign_key="resourcetype.name")
#     source: str = Field(default="inline")
#     resource_location: Optional[str] = None
#     content: Optional[str] = None
#     payload: dict = Field(sa_column=Column(JSON), nullable=False)
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     template: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# class EventType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#     template: str
#
#
# class Event(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     event_type: str = Field(foreign_key="eventtype.name")
#     event_message: Optional[str] = None
#     resource_path: str = Field(foreign_key="catalogentry.resource_path")
#     resource_version: str = Field(foreign_key="catalogentry.resource_version")
#     content: Optional[str] = None
#     payload: Optional[dict] = Field(sa_column=Column(JSON))
#     context: Optional[dict] = Field(sa_column=Column(JSON))
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#     class Config:
#         arbitrary_types_allowed = True
#
#
# # ---- Workflow Execution Core ----
#
# class ExecutionContext:
#     def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
#         self.data = initial_data or {}
#
#     def update(self, new_data: Dict[str, Any]):
#         self.data.update(new_data)
#
#     def get(self, key: str, default=None):
#         return self.data.get(key, default)
#
#
# class Token:
#     def __init__(self, step_name: str, context: ExecutionContext):
#         self.step_name = step_name
#         self.context = context
#
#
# class BaseActionHandler:
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         raise NotImplementedError
#
#
# class HttpActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         method = parameters.get("method", "GET").upper()
#         url = parameters.get("url")
#         data = parameters.get("data")
#         headers = parameters.get("headers", {})
#         if method == "GET":
#             response = requests.get(url, headers=headers)
#         elif method == "POST":
#             response = requests.post(url, json=data, headers=headers)
#         else:
#             raise ValueError(f"Unsupported HTTP method: {method}")
#         return {"status_code": response.status_code, "response": response.json() if response.content else {}}
#
#
# class PostgresActionHandler(BaseActionHandler):
#     def __init__(self, db_config: Dict[str, str]):
#         self.db_config = db_config
#
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         query = parameters.get("query")
#         if not query:
#             raise ValueError("No query provided for Postgres action.")
#         connection = psycopg2.connect(**self.db_config)
#         cursor = connection.cursor()
#         cursor.execute(query)
#         try:
#             result = cursor.fetchall()
#         except Exception:
#             result = []
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return {"result": result}
#
#
# class ShellActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         command = parameters.get("command")
#         if not command:
#             raise ValueError("No command provided for Shell action.")
#         completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
#         return {"stdout": completed_process.stdout, "stderr": completed_process.stderr, "returncode": completed_process.returncode}
#
#
# class ActionDispatcher:
#     def __init__(self, db_config: Optional[Dict[str, str]] = None):
#         self.handlers = {
#             "http": HttpActionHandler(),
#             "postgres": PostgresActionHandler(db_config=db_config or {}),
#             "shell": ShellActionHandler(),
#         }
#
#     def dispatch(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         handler = self.handlers.get(action_type)
#         if not handler:
#             raise ValueError(f"No handler for action type: {action_type}")
#         return handler.execute(parameters)
#
#
# class EventLogger:
#     def __init__(self, database_url: str):
#         self.queue = asyncio.Queue()
#         self.engine = create_engine(database_url)
#
#     async def log_event(self, event_type: str, resource_path: str, resource_version: str, payload: Optional[dict] = None, meta: Optional[dict] = None):
#         event = Event(
#             event_id=str(uuid.uuid4()),
#             event_type=event_type,
#             resource_path=resource_path,
#             resource_version=resource_version,
#             payload=payload,
#             meta=meta
#         )
#         await self.queue.put(event)
#
#     async def run(self):
#         while True:
#             event = await self.queue.get()
#             with Session(self.engine) as session:
#                 session.add(event)
#                 session.commit()
#             self.queue.task_done()
#
#
# class WorkflowExecutor:
#     def __init__(self, playbook: Dict[str, Any], db_config: Optional[Dict[str, str]] = None, event_logger: Optional[EventLogger] = None):
#         self.playbook = playbook
#         self.tasks = playbook.get("tasks", {})
#         self.steps = {step["name"]: step for step in playbook.get("steps", [])}
#         self.tokens: List[Token] = []
#         self.context = ExecutionContext()
#         self.dispatcher = ActionDispatcher(db_config=db_config)
#         self.event_logger = event_logger
#         self.resource_path = playbook.get("name", "unknown_workflow")
#         self.resource_version = playbook.get("version", "v1")
#
#     async def start(self):
#         if self.event_logger:
#             await self.event_logger.log_event("EXECUTION_STARTED", self.resource_path, self.resource_version)
#         start_step = self.playbook.get("start") or list(self.steps.keys())[0]
#         self.tokens.append(Token(step_name=start_step, context=self.context))
#         await self.run()
#         if self.event_logger:
#             await self.event_logger.log_event("EXECUTION_COMPLETED", self.resource_path, self.resource_version)
#
#     async def run(self):
#         while self.tokens:
#             token = self.tokens.pop(0)
#             if self.event_logger:
#                 await self.event_logger.log_event("STEP_STARTED", self.resource_path, self.resource_version, meta={"step": token.step_name})
#             print(f"Executing Step: {token.step_name}")
#             await self.execute_step(token)
#             if self.event_logger:
#                 await self.event_logger.log_event("STEP_COMPLETED", self.resource_path, self.resource_version, meta={"step": token.step_name})
#
#     async def execute_step(self, token: Token):
#         step = self.steps.get(token.step_name)
#         if not step:
#             print(f"Step {token.step_name} not found!")
#             return
#
#         actions = step.get("actions", [])
#         tasks = step.get("tasks", [])
#
#         for action in actions:
#             self.execute_action(action, token.context)
#
#         for task_name in tasks:
#             task = self.tasks.get(task_name)
#             if task:
#                 for action in task.get("actions", []):
#                     self.execute_action(action, token.context)
#
#         rule = step.get("rule")
#         if rule:
#             for case in rule.get("cases", []):
#                 condition = case.get("condition", "true")
#                 if self.evaluate_condition(condition, token.context):
#                     run_steps = case.get("run", [])
#                     if isinstance(run_steps, str):
#                         run_steps = [run_steps]
#                     for next_step in run_steps:
#                         self.tokens.append(Token(step_name=next_step, context=token.context))
#                     break
#
#     def execute_action(self, action: Dict[str, Any], context: ExecutionContext):
#         action_type = action.get("type")
#         parameters = action.get("parameters", {})
#         print(f"Executing Action: {action_type} with params {parameters}")
#         result = self.dispatcher.dispatch(action_type, parameters)
#         context.update(result)
#
#     def evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
#         try:
#             template = Template(condition)
#             rendered = template.render(context=context.data)
#             return rendered.strip().lower() == "true"
#         except Exception as e:
#             print(f"Condition evaluation error: {e}")
#             return False
#
#
# ### Plan for Parallel Execution
#
#
# from typing import Optional, Dict, List, Any
# from sqlmodel import SQLModel, Field, Column, JSON, TIMESTAMP, create_engine, Session
# from datetime import datetime
# import requests
# import subprocess
# import psycopg2
# import asyncio
# from jinja2 import Template
# import uuid
#
#
# class ResourceType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#
#
# class CatalogEntry(SQLModel, table=True):
#     resource_path: str = Field(primary_key=True)
#     resource_version: str = Field(primary_key=True)
#     resource_type: str = Field(foreign_key="resourcetype.name")
#     source: str = Field(default="inline")
#     resource_location: Optional[str] = None
#     content: Optional[str] = None
#     payload: dict = Field(sa_column=Column(JSON), nullable=False)
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     template: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# class EventType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#     template: str
#
#
# class Event(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     event_type: str = Field(foreign_key="eventtype.name")
#     event_message: Optional[str] = None
#     resource_path: str = Field(foreign_key="catalogentry.resource_path")
#     resource_version: str = Field(foreign_key="catalogentry.resource_version")
#     content: Optional[str] = None
#     payload: Optional[dict] = Field(sa_column=Column(JSON))
#     context: Optional[dict] = Field(sa_column=Column(JSON))
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#     class Config:
#         arbitrary_types_allowed = True
#
#
# # ---- Workflow Execution Core ----
#
# class ExecutionContext:
#     def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
#         self.data = initial_data or {}
#
#     def update(self, new_data: Dict[str, Any]):
#         self.data.update(new_data)
#
#     def get(self, key: str, default=None):
#         return self.data.get(key, default)
#
#
# class Token:
#     def __init__(self, step_name: str, context: ExecutionContext):
#         self.step_name = step_name
#         self.context = context
#
#
# class BaseActionHandler:
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         raise NotImplementedError
#
#
# class HttpActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         method = parameters.get("method", "GET").upper()
#         url = parameters.get("url")
#         data = parameters.get("data")
#         headers = parameters.get("headers", {})
#         if method == "GET":
#             response = requests.get(url, headers=headers)
#         elif method == "POST":
#             response = requests.post(url, json=data, headers=headers)
#         else:
#             raise ValueError(f"Unsupported HTTP method: {method}")
#         return {"status_code": response.status_code, "response": response.json() if response.content else {}}
#
#
# class PostgresActionHandler(BaseActionHandler):
#     def __init__(self, db_config: Dict[str, str]):
#         self.db_config = db_config
#
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         query = parameters.get("query")
#         if not query:
#             raise ValueError("No query provided for Postgres action.")
#         connection = psycopg2.connect(**self.db_config)
#         cursor = connection.cursor()
#         cursor.execute(query)
#         try:
#             result = cursor.fetchall()
#         except Exception:
#             result = []
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return {"result": result}
#
#
# class ShellActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         command = parameters.get("command")
#         if not command:
#             raise ValueError("No command provided for Shell action.")
#         completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
#         return {"stdout": completed_process.stdout, "stderr": completed_process.stderr, "returncode": completed_process.returncode}
#
#
# class ActionDispatcher:
#     def __init__(self, db_config: Optional[Dict[str, str]] = None):
#         self.handlers = {
#             "http": HttpActionHandler(),
#             "postgres": PostgresActionHandler(db_config=db_config or {}),
#             "shell": ShellActionHandler(),
#         }
#
#     def dispatch(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         handler = self.handlers.get(action_type)
#         if not handler:
#             raise ValueError(f"No handler for action type: {action_type}")
#         return handler.execute(parameters)
#
#
# class EventLogger:
#     def __init__(self, database_url: str):
#         self.queue = asyncio.Queue()
#         self.engine = create_engine(database_url)
#
#     async def log_event(self, event_type: str, resource_path: str, resource_version: str, payload: Optional[dict] = None, meta: Optional[dict] = None):
#         event = Event(
#             event_id=str(uuid.uuid4()),
#             event_type=event_type,
#             resource_path=resource_path,
#             resource_version=resource_version,
#             payload=payload,
#             meta=meta
#         )
#         await self.queue.put(event)
#
#     async def run(self):
#         while True:
#             event = await self.queue.get()
#             with Session(self.engine) as session:
#                 session.add(event)
#                 session.commit()
#             self.queue.task_done()
#
#
# class WorkflowExecutor:
#     def __init__(self, playbook: Dict[str, Any], db_config: Optional[Dict[str, str]] = None, event_logger: Optional[EventLogger] = None):
#         self.playbook = playbook
#         self.tasks = playbook.get("tasks", {})
#         self.steps = {step["name"]: step for step in playbook.get("steps", [])}
#         self.tokens: List[Token] = []
#         self.context = ExecutionContext()
#         self.dispatcher = ActionDispatcher(db_config=db_config)
#         self.event_logger = event_logger
#         self.resource_path = playbook.get("name", "unknown_workflow")
#         self.resource_version = playbook.get("version", "v1")
#
#     async def start(self):
#         if self.event_logger:
#             await self.event_logger.log_event("EXECUTION_STARTED", self.resource_path, self.resource_version)
#         start_step = self.playbook.get("start") or list(self.steps.keys())[0]
#         self.tokens.append(Token(step_name=start_step, context=self.context))
#         await self.run()
#         if self.event_logger:
#             await self.event_logger.log_event("EXECUTION_COMPLETED", self.resource_path, self.resource_version)
#
#     async def run(self):
#         while self.tokens:
#             token = self.tokens.pop(0)
#             if self.event_logger:
#                 await self.event_logger.log_event("STEP_STARTED", self.resource_path, self.resource_version, meta={"step": token.step_name})
#             print(f"Executing Step: {token.step_name}")
#             await self.execute_step(token)
#             if self.event_logger:
#                 await self.event_logger.log_event("STEP_COMPLETED", self.resource_path, self.resource_version, meta={"step": token.step_name})
#
#     async def execute_step(self, token: Token):
#         step = self.steps.get(token.step_name)
#         if not step:
#             print(f"Step {token.step_name} not found!")
#             return
#
#         actions = step.get("actions", [])
#         tasks = step.get("tasks", [])
#
#         for action in actions:
#             self.execute_action(action, token.context)
#
#         for task_name in tasks:
#             task = self.tasks.get(task_name)
#             if task:
#                 for action in task.get("actions", []):
#                     self.execute_action(action, token.context)
#
#         rule = step.get("rule")
#         if rule:
#             for case in rule.get("cases", []):
#                 condition = case.get("condition", "true")
#                 if self.evaluate_condition(condition, token.context):
#                     run_steps = case.get("run", [])
#                     if isinstance(run_steps, str):
#                         run_steps = [run_steps]
#                     for next_step in run_steps:
#                         self.tokens.append(Token(step_name=next_step, context=token.context))
#                     break
#
#     def execute_action(self, action: Dict[str, Any], context: ExecutionContext):
#         action_type = action.get("type")
#         parameters = action.get("parameters", {})
#         print(f"Executing Action: {action_type} with params {parameters}")
#         result = self.dispatcher.dispatch(action_type, parameters)
#         context.update(result)
#
#     def evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
#         try:
#             template = Template(condition)
#             rendered = template.render(context=context.data)
#             return rendered.strip().lower() == "true"
#         except Exception as e:
#             print(f"Condition evaluation error: {e}")
#             return False
#
#
#
# #### Parallel Execution ####
#
#
# from typing import Optional, Dict, List, Any
# from sqlmodel import SQLModel, Field, Column, JSON, TIMESTAMP, create_engine, Session
# from datetime import datetime
# import requests
# import subprocess
# import psycopg2
# import asyncio
# from jinja2 import Template
# import uuid
#
#
# class ResourceType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#
#
# class CatalogEntry(SQLModel, table=True):
#     resource_path: str = Field(primary_key=True)
#     resource_version: str = Field(primary_key=True)
#     resource_type: str = Field(foreign_key="resourcetype.name")
#     source: str = Field(default="inline")
#     resource_location: Optional[str] = None
#     content: Optional[str] = None
#     payload: dict = Field(sa_column=Column(JSON), nullable=False)
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     template: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# class EventType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#     template: str
#
#
# class Event(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     event_type: str = Field(foreign_key="eventtype.name")
#     event_message: Optional[str] = None
#     resource_path: str = Field(foreign_key="catalogentry.resource_path")
#     resource_version: str = Field(foreign_key="catalogentry.resource_version")
#     content: Optional[str] = None
#     payload: Optional[dict] = Field(sa_column=Column(JSON))
#     context: Optional[dict] = Field(sa_column=Column(JSON))
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#     class Config:
#         arbitrary_types_allowed = True
#
#
# # ---- Workflow Execution Core ----
#
# class ExecutionContext:
#     def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
#         self.data = initial_data or {}
#
#     def update(self, new_data: Dict[str, Any]):
#         self.data.update(new_data)
#
#     def get(self, key: str, default=None):
#         return self.data.get(key, default)
#
#
# class Token:
#     def __init__(self, step_name: str, context: ExecutionContext):
#         self.step_name = step_name
#         self.context = context
#
#
# class BaseActionHandler:
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         raise NotImplementedError
#
#
# class HttpActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         method = parameters.get("method", "GET").upper()
#         url = parameters.get("url")
#         data = parameters.get("data")
#         headers = parameters.get("headers", {})
#         if method == "GET":
#             response = requests.get(url, headers=headers)
#         elif method == "POST":
#             response = requests.post(url, json=data, headers=headers)
#         else:
#             raise ValueError(f"Unsupported HTTP method: {method}")
#         return {"status_code": response.status_code, "response": response.json() if response.content else {}}
#
#
# class PostgresActionHandler(BaseActionHandler):
#     def __init__(self, db_config: Dict[str, str]):
#         self.db_config = db_config
#
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         query = parameters.get("query")
#         if not query:
#             raise ValueError("No query provided for Postgres action.")
#         connection = psycopg2.connect(**self.db_config)
#         cursor = connection.cursor()
#         cursor.execute(query)
#         try:
#             result = cursor.fetchall()
#         except Exception:
#             result = []
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return {"result": result}
#
#
# class ShellActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         command = parameters.get("command")
#         if not command:
#             raise ValueError("No command provided for Shell action.")
#         completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
#         return {"stdout": completed_process.stdout, "stderr": completed_process.stderr, "returncode": completed_process.returncode}
#
#
# class ActionDispatcher:
#     def __init__(self, db_config: Optional[Dict[str, str]] = None):
#         self.handlers = {
#             "http": HttpActionHandler(),
#             "postgres": PostgresActionHandler(db_config=db_config or {}),
#             "shell": ShellActionHandler(),
#         }
#
#     def dispatch(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         handler = self.handlers.get(action_type)
#         if not handler:
#             raise ValueError(f"No handler for action type: {action_type}")
#         return handler.execute(parameters)
#
#
# class EventLogger:
#     def __init__(self, database_url: str):
#         self.queue = asyncio.Queue()
#         self.engine = create_engine(database_url)
#
#     async def log_event(self, event_type: str, resource_path: str, resource_version: str, payload: Optional[dict] = None, meta: Optional[dict] = None):
#         event = Event(
#             event_id=str(uuid.uuid4()),
#             event_type=event_type,
#             resource_path=resource_path,
#             resource_version=resource_version,
#             payload=payload,
#             meta=meta
#         )
#         await self.queue.put(event)
#
#     async def run(self):
#         while True:
#             event = await self.queue.get()
#             with Session(self.engine) as session:
#                 session.add(event)
#                 session.commit()
#             self.queue.task_done()
#
#
# class WorkflowExecutor:
#     def __init__(self, playbook: Dict[str, Any], db_config: Optional[Dict[str, str]] = None, event_logger: Optional[EventLogger] = None):
#         self.playbook = playbook
#         self.tasks = playbook.get("tasks", {})
#         self.steps = {step["name"]: step for step in playbook.get("steps", [])}
#         self.tokens: List[Token] = []
#         self.context = ExecutionContext()
#         self.dispatcher = ActionDispatcher(db_config=db_config)
#         self.event_logger = event_logger
#         self.resource_path = playbook.get("name", "unknown_workflow")
#         self.resource_version = playbook.get("version", "v1")
#
#     async def start(self):
#         if self.event_logger:
#             await self.event_logger.log_event("EXECUTION_STARTED", self.resource_path, self.resource_version)
#         start_step = self.playbook.get("start") or list(self.steps.keys())[0]
#         self.tokens.append(Token(step_name=start_step, context=self.context))
#         await self.run()
#         if self.event_logger:
#             await self.event_logger.log_event("EXECUTION_COMPLETED", self.resource_path, self.resource_version)
#
#     async def run(self):
#         while self.tokens:
#             running_tokens = list(self.tokens)
#             self.tokens.clear()
#             await asyncio.gather(*(self.process_token(token) for token in running_tokens))
#
#     async def process_token(self, token: Token):
#         if self.event_logger:
#             await self.event_logger.log_event("STEP_STARTED", self.resource_path, self.resource_version, meta={"step": token.step_name})
#         print(f"Executing Step: {token.step_name}")
#         await self.execute_step(token)
#         if self.event_logger:
#             await self.event_logger.log_event("STEP_COMPLETED", self.resource_path, self.resource_version, meta={"step": token.step_name})
#
#     async def execute_step(self, token: Token):
#         step = self.steps.get(token.step_name)
#         if not step:
#             print(f"Step {token.step_name} not found!")
#             return
#
#         actions = step.get("actions", [])
#         tasks = step.get("tasks", [])
#         parallel = step.get("parallel", False)
#
#         if parallel:
#             await asyncio.gather(*(self.execute_action_async(action, token.context) for action in actions))
#             for task_name in tasks:
#                 task = self.tasks.get(task_name)
#                 if task:
#                     await asyncio.gather(*(self.execute_action_async(a, token.context) for a in task.get("actions", [])))
#         else:
#             for action in actions:
#                 await self.execute_action_async(action, token.context)
#             for task_name in tasks:
#                 task = self.tasks.get(task_name)
#                 if task:
#                     for action in task.get("actions", []):
#                         await self.execute_action_async(action, token.context)
#
#         rule = step.get("rule")
#         if rule:
#             for case in rule.get("cases", []):
#                 condition = case.get("condition", "true")
#                 if self.evaluate_condition(condition, token.context):
#                     run_steps = case.get("run", [])
#                     if isinstance(run_steps, str):
#                         run_steps = [run_steps]
#                     for next_step in run_steps:
#                         self.tokens.append(Token(step_name=next_step, context=token.context))
#                     break
#
#     async def execute_action_async(self, action: Dict[str, Any], context: ExecutionContext):
#         action_type = action.get("type")
#         parameters = action.get("parameters", {})
#         print(f"Executing Action: {action_type} with params {parameters}")
#         result = self.dispatcher.dispatch(action_type, parameters)
#         context.update(result)
#
#     def evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
#         try:
#             template = Template(condition)
#             rendered = template.render(context=context.data)
#             return rendered.strip().lower() == "true"
#         except Exception as e:
#             print(f"Condition evaluation error: {e}")
#             return False
#
#
#
# ### Worker claim management
#
#
# from typing import Optional, Dict, List, Any
# from sqlmodel import SQLModel, Field, Column, JSON, TIMESTAMP, create_engine, Session, select
# from datetime import datetime
# import requests
# import subprocess
# import psycopg2
# import asyncio
# from jinja2 import Template
# import uuid
#
#
# class ResourceType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#
#
# class CatalogEntry(SQLModel, table=True):
#     resource_path: str = Field(primary_key=True)
#     resource_version: str = Field(primary_key=True)
#     resource_type: str = Field(foreign_key="resourcetype.name")
#     source: str = Field(default="inline")
#     resource_location: Optional[str] = None
#     content: Optional[str] = None
#     payload: dict = Field(sa_column=Column(JSON), nullable=False)
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     template: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# class EventType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#     template: str
#
#
# class Event(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     event_type: str = Field(foreign_key="eventtype.name")
#     event_message: Optional[str] = None
#     resource_path: str = Field(foreign_key="catalogentry.resource_path")
#     resource_version: str = Field(foreign_key="catalogentry.resource_version")
#     content: Optional[str] = None
#     payload: Optional[dict] = Field(sa_column=Column(JSON))
#     context: Optional[dict] = Field(sa_column=Column(JSON))
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#     class Config:
#         arbitrary_types_allowed = True
#
#
# class EventClaim(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     worker_id: str = Field(primary_key=True)
#     job_id: str
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# # ---- Worker Claim Management ----
#
# class WorkerClaimManager:
#     def __init__(self, database_url: str):
#         self.engine = create_engine(database_url)
#
#     def claim_event(self, event_id: str, worker_id: str, job_id: str):
#         claim = EventClaim(
#             event_id=event_id,
#             worker_id=worker_id,
#             job_id=job_id
#         )
#         with Session(self.engine) as session:
#             session.add(claim)
#             session.commit()
#
#     def check_ownership(self, event_id: str, worker_id: str) -> bool:
#         with Session(self.engine) as session:
#             statement = select(EventClaim).where(EventClaim.event_id == event_id).order_by(EventClaim.timestamp.asc())
#             claims = session.exec(statement).all()
#             if not claims:
#                 return False
#             first_claim = claims[0]
#             return first_claim.worker_id == worker_id
#
#     def release_claim(self, event_id: str, worker_id: str):
#         with Session(self.engine) as session:
#             statement = select(EventClaim).where(EventClaim.event_id == event_id, EventClaim.worker_id == worker_id)
#             claim = session.exec(statement).first()
#             if claim:
#                 session.delete(claim)
#                 session.commit()
#
#
# # ---- Workflow Execution Core ----
#
# class ExecutionContext:
#     def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
#         self.data = initial_data or {}
#
#     def update(self, new_data: Dict[str, Any]):
#         self.data.update(new_data)
#
#     def get(self, key: str, default=None):
#         return self.data.get(key, default)
#
#
# class Token:
#     def __init__(self, step_name: str, context: ExecutionContext):
#         self.step_name = step_name
#         self.context = context
#
#
# class BaseActionHandler:
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         raise NotImplementedError
#
#
# class HttpActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         method = parameters.get("method", "GET").upper()
#         url = parameters.get("url")
#         data = parameters.get("data")
#         headers = parameters.get("headers", {})
#         if method == "GET":
#             response = requests.get(url, headers=headers)
#         elif method == "POST":
#             response = requests.post(url, json=data, headers=headers)
#         else:
#             raise ValueError(f"Unsupported HTTP method: {method}")
#         return {"status_code": response.status_code, "response": response.json() if response.content else {}}
#
#
# class PostgresActionHandler(BaseActionHandler):
#     def __init__(self, db_config: Dict[str, str]):
#         self.db_config = db_config
#
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         query = parameters.get("query")
#         if not query:
#             raise ValueError("No query provided for Postgres action.")
#         connection = psycopg2.connect(**self.db_config)
#         cursor = connection.cursor()
#         cursor.execute(query)
#         try:
#             result = cursor.fetchall()
#         except Exception:
#             result = []
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return {"result": result}
#
#
# class ShellActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         command = parameters.get("command")
#         if not command:
#             raise ValueError("No command provided for Shell action.")
#         completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
#         return {"stdout": completed_process.stdout, "stderr": completed_process.stderr, "returncode": completed_process.returncode}
#
#
# class ActionDispatcher:
#     def __init__(self, db_config: Optional[Dict[str, str]] = None):
#         self.handlers = {
#             "http": HttpActionHandler(),
#             "postgres": PostgresActionHandler(db_config=db_config or {}),
#             "shell": ShellActionHandler(),
#         }
#
#     def dispatch(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         handler = self.handlers.get(action_type)
#         if not handler:
#             raise ValueError(f"No handler for action type: {action_type}")
#         return handler.execute(parameters)
#
#
# # EventLogger and WorkflowExecutor classes remain as before, can reference above
#
# #####
#
#
# from typing import Optional, Dict, List, Any
# from sqlmodel import SQLModel, Field, Column, JSON, TIMESTAMP, create_engine, Session, select
# from datetime import datetime
# import requests
# import subprocess
# import psycopg2
# import asyncio
# from jinja2 import Template
# import uuid
#
#
# class ResourceType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#
#
# class CatalogEntry(SQLModel, table=True):
#     resource_path: str = Field(primary_key=True)
#     resource_version: str = Field(primary_key=True)
#     resource_type: str = Field(foreign_key="resourcetype.name")
#     source: str = Field(default="inline")
#     resource_location: Optional[str] = None
#     content: Optional[str] = None
#     payload: dict = Field(sa_column=Column(JSON), nullable=False)
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     template: Optional[str] = None
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# class EventType(SQLModel, table=True):
#     name: str = Field(primary_key=True)
#     template: str
#
#
# class Event(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     event_type: str = Field(foreign_key="eventtype.name")
#     event_message: Optional[str] = None
#     resource_path: str = Field(foreign_key="catalogentry.resource_path")
#     resource_version: str = Field(foreign_key="catalogentry.resource_version")
#     content: Optional[str] = None
#     payload: Optional[dict] = Field(sa_column=Column(JSON))
#     context: Optional[dict] = Field(sa_column=Column(JSON))
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#     class Config:
#         arbitrary_types_allowed = True
#
#
# class EventClaim(SQLModel, table=True):
#     event_id: str = Field(primary_key=True)
#     worker_id: str = Field(primary_key=True)
#     job_id: str
#     meta: Optional[dict] = Field(sa_column=Column(JSON))
#     timestamp: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(TIMESTAMP(timezone=True)))
#
#
# # ---- Worker Claim Management ----
#
# class WorkerClaimManager:
#     def __init__(self, database_url: str):
#         self.engine = create_engine(database_url)
#
#     def claim_event(self, event_id: str, worker_id: str, job_id: str):
#         claim = EventClaim(
#             event_id=event_id,
#             worker_id=worker_id,
#             job_id=job_id
#         )
#         with Session(self.engine) as session:
#             session.add(claim)
#             session.commit()
#
#     def check_ownership(self, event_id: str, worker_id: str) -> bool:
#         with Session(self.engine) as session:
#             statement = select(EventClaim).where(EventClaim.event_id == event_id).order_by(EventClaim.timestamp.asc())
#             claims = session.exec(statement).all()
#             if not claims:
#                 return False
#             first_claim = claims[0]
#             return first_claim.worker_id == worker_id
#
#     def release_claim(self, event_id: str, worker_id: str):
#         with Session(self.engine) as session:
#             statement = select(EventClaim).where(EventClaim.event_id == event_id, EventClaim.worker_id == worker_id)
#             claim = session.exec(statement).first()
#             if claim:
#                 session.delete(claim)
#                 session.commit()
#
#
# # ---- Workflow Execution Core ----
#
# class ExecutionContext:
#     def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
#         self.data = initial_data or {}
#
#     def update(self, new_data: Dict[str, Any]):
#         self.data.update(new_data)
#
#     def get(self, key: str, default=None):
#         return self.data.get(key, default)
#
#
# class Token:
#     def __init__(self, step_name: str, context: ExecutionContext):
#         self.step_name = step_name
#         self.context = context
#
#
# class BaseActionHandler:
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         raise NotImplementedError
#
#
# class HttpActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         method = parameters.get("method", "GET").upper()
#         url = parameters.get("url")
#         data = parameters.get("data")
#         headers = parameters.get("headers", {})
#         if method == "GET":
#             response = requests.get(url, headers=headers)
#         elif method == "POST":
#             response = requests.post(url, json=data, headers=headers)
#         else:
#             raise ValueError(f"Unsupported HTTP method: {method}")
#         return {"status_code": response.status_code, "response": response.json() if response.content else {}}
#
#
# class PostgresActionHandler(BaseActionHandler):
#     def __init__(self, db_config: Dict[str, str]):
#         self.db_config = db_config
#
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         query = parameters.get("query")
#         if not query:
#             raise ValueError("No query provided for Postgres action.")
#         connection = psycopg2.connect(**self.db_config)
#         cursor = connection.cursor()
#         cursor.execute(query)
#         try:
#             result = cursor.fetchall()
#         except Exception:
#             result = []
#         connection.commit()
#         cursor.close()
#         connection.close()
#         return {"result": result}
#
#
# class ShellActionHandler(BaseActionHandler):
#     def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         command = parameters.get("command")
#         if not command:
#             raise ValueError("No command provided for Shell action.")
#         completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
#         return {"stdout": completed_process.stdout, "stderr": completed_process.stderr, "returncode": completed_process.returncode}
#
#
# class ActionDispatcher:
#     def __init__(self, db_config: Optional[Dict[str, str]] = None):
#         self.handlers = {
#             "http": HttpActionHandler(),
#             "postgres": PostgresActionHandler(db_config=db_config or {}),
#             "shell": ShellActionHandler(),
#         }
#
#     def dispatch(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
#         handler = self.handlers.get(action_type)
#         if not handler:
#             raise ValueError(f"No handler for action type: {action_type}")
#         return handler.execute(parameters)
#
#
# # EventLogger and WorkflowExecutor classes remain as before, can reference above

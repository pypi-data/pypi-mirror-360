# NoETL DSL Semantic Design

The NoETL workflow engine interprets a YAML playbook as a state-machine: steps are states, and the control flow is dictated by explicit rules and transitions. We also map these concepts to well-established models from process mining, event-driven process chains (EPC), and Petri nets to ensure the design is theoretically sound and easy to reason about. 

We will design data models for Playbooks, Steps, Tasks, and Actions to reflect the Workflow DSL YAML structure. The relationships are as follows:

- **Playbook**: Top-level workflow definition containing an environment (global variables/config), a dictionary of reusable tasks definitions, and a list of steps that form the workflow. (Other metadata like name, version, etc., can be included as needed.)
- **Step**: A unit of workflow logic that can include a sequence of task calls and/or inline actions. Each step may have:
- A **name** (identifier for routing).
- A list of **tasks** (by reference to the named tasks defined in the playbook).
- A list of **actions** (inlined actions to execute directly in this step).
- A **rule** block for transition (conditional routing) after execution of the step.
- A **parallel** flag (boolean) indicating if the tasks/actions in this step should run concurrently.
- **Task**: A reusable sequence of actions, defined once and referenced by steps. Each task has:
- A **name** (identifier to call the task).
- A list of **actions** (the commands or calls that comprise this task’s procedure).
- A **parallel** flag indicating if its actions should execute in parallel.
- _Note_: Tasks serve as modular building blocks (similar to subroutines). Defining tasks separately allows reuse in multiple steps and clarifies the distinction between grouping of actions (tasks) vs. individual actions.
- **Action**: The smallest execution unit, representing a single operation. Each action is defined by:
- A **action** (identifying the category or executor, e.g., postgres, http, shell).
- A **method** (specific operation to perform, e.g., create_table for a database, get for an HTTP request).
- Parameters necessary for that action (e.g., SQL statement, API endpoint, shell command, etc.).
- An optional **parallel** flag (if an action can spawn internal parallel operations – usually this is not needed at the single action level, so it may be reserved for future extension or simply ignored in normal actions).

- **Environment/Context**: A dictionary of variables provided in `environment` (e.g. configuration like DB connection strings, or initial workflow variables). This will be loaded into a **Context** object at runtime and used for templating and passing data between actions. As the workflow runs, the context is updated with results from actions (e.g., an action can store output into a context variable). This context is what Jinja2 expressions will evaluate against.

- **Tasks vs Actions**: tasks are containers of actions, not executable on their own. An **Action** knows how to execute something concrete, whereas a **Task** simply holds a sequence of actions to execute (optionally in parallel). Steps can call tasks by name (to execute all actions in that task) or include actions directly. This clear separation ensures that adding a new low-level operation means adding a new **Action** type rather than a new **Task**. **Tasks** are more about organizing and reusing sequences of **Actions**.

- **Internal Data Structure**: We will create Python classes (or Pydantic models for validation) for each component:
  - `Action`: with fields for method, type, parameters, etc., and an `execute(context)` method.
  - `Task`: with a name and list of Action objects (and possibly a flag for parallel execution of its actions).
  - `Step`: with a name, lists of Task references and/or Action objects, a Rule/Condition, and parallel flag.
  - `Playbook`: containing environment data, lists of tasks and steps (possibly convertable to dicts).  

  These classes will make it easier to manipulate the workflow in code (as opposed to raw dicts). The `interp.py` module can be adapted to parse the YAML into these classes. For example, `interp.py` can be updated to distinguish between entries under a step: if an entry matches a task name, it links the corresponding Task object; if it’s a dict with method/type, it creates an Action object. That way tasks and actions will be properly separated in the code.

## Step Semantics: Rule-Driven Transitions

Each **step** in the workflow represents a state or node in the process. We enforce a clear, explicit semantics for steps and their transitions, driven by a `rule` block within each step. The step’s `rule` determines what happens when that step is executed, much like a switch/gateway that decides the next move. Key rules for step semantics include:

- **Mandatory Rule per Step:** Every step must define a `rule` consisting of one or more cases. This rule block drives all control flow leaving the step – no implicit progression. Each case in the rule has:
  - a `case` **condition** (a Jinja2 boolean expression) that is evaluated in the context, and
  - a `run` clause that specifies what to do if the condition is true.
- **Case Run: Transition vs In-Place Execution:** The `run` clause can take one of two forms:
  - **Transition to other step(s):** If the `run` lists one or more step names, it signifies a **transition**. The current step will complete, and execution jumps to the referenced step(s). This is analogous to an explicit "goto" or branch in the workflow graph. If multiple steps are listed, it represents a fork into multiple branches (concurrent execution of those steps).
  - **In-place task execution:** If the run lists tasks or inline actions (execution steps with a `type`, see Action Semantics below), those will be executed **within the context of the current step**. The step does not end at this point – it is performing work in-place. No state transition occurs during these actions. After the actions complete, the step’s rule evaluation is considered satisfied. Unless another rule case triggers a transition afterward, the workflow stays in the same step until completion of that case’s actions.
- **No Mixed Run Modes:** A single `case` cannot mix step transitions and in-place actions in the same run list. Each case is either a pure transition or pure in-place execution. For example, a case that tries to both execute a task and jump to another step is **invalid**. This constraint will be enforced at validation time (see Validation Rules below). It ensures that the outcome of a case is unambiguous – either move to new step(s), or do some work here but never both.
- **Exclusive or Priority-based Cases:** The rule’s cases are evaluated in order (top to bottom). The first matching case will trigger its `run` and others will be skipped (similar to an if/elif chain). If no `case` condition evaluates to true, then the rule has no matching case – which means that this step leads nowhere and the workflow execution for this branch will end. If a case condition is true but its `run` is empty or not specified (which would be unusual), that would also result in no action and thus an end of that branch. This design makes each step a well-defined decision point.
- **Explicit Branch Termination:** If no case matches, or if a matched case has an empty `run`, it signals **the end of that execution path** (a terminal state). The workflow engine will recognize that no further steps are forthcoming from this step and will mark the branch as complete. This is akin to reaching an end event in a process diagram.
- **No Implicit Step Sequencing:** Critically, there is no notion of "fall-through" or moving to the next step by default. All step-to-step progressions must be explicitly defined in a rule’s run. The YAML playbook cannot rely on the ordering of steps in the file to imply execution order. This prevents ambiguity. Every transition is declared, making the workflow’s directed graph of steps and transitions explicit and easier to visualize and trace. (In formal terms, the workflow is an ordered graph of steps connected by explicit rules, much like an EPC where events/functions are connected only via defined connectors.)

**Example:** Suppose we have a step VerifyUser. Its rule might have two cases – one case where the user is verified (condition passes) causing a transition to step FetchData, and another case where verification fails causing a transition to step HandleError.
```yaml
steps:
  - name: VerifyUser
    rule:
      - case: "{{ user_id is not None }}"
        run: 
          - step: FetchData      # Transition to another step
      - case: "{{ user_id is None }}"
        run: 
          - step: HandleError    # Transition to an error-handling step
```
In this example, `VerifyUser` will immediately transition to one of two steps based on the condition. No tasks are done within `VerifyUser` itself; it purely routes to the next step. If neither condition met (say `user_id` is undefined), the branch would end at `VerifyUser` with no next step.

Now consider a step FetchData that performs some actions then ends:
```yaml
  - name: FetchData
    rule:
      - case: "{{ True }}"
        run:
          - action: http        # In-place actions (no transition)
            method: GET
            url: "https://api.example.com/data/{{ user_id }}"
          - action: postgres
            query: "INSERT INTO records VALUES (...)" 
```

Here `FetchData` has a single case that always runs (condition `True`). Its run executes two actions (an HTTP call and a database query) in-place. It does not transition to any other step. After those actions, there are no further cases and no transitions, so that branch of the workflow ends after `FetchData` completes the tasks. This illustrates a step that acts as a terminal node doing some final work.


## Validation Rules for Workflow Playbooks
To enforce the above semantics and catch design errors early, the YAML playbook will be subject to strict validation. We will implement a schema and validator (using Pydantic or a custom checker) to ensure playbooks are well-formed before execution. The validation will check the following:
- **Unique Step and Task Names:** All step names in the playbook must be unique, and all task names (if tasks are defined separately) must be unique. No duplicate identifiers are allowed in their respective namespaces. This uniqueness is important because steps and tasks serve as references; for example, if two steps had the same name, a transition reference would be ambiguous. The validator will raise an error if it finds duplicate `steps` keys or duplicate `tasks` keys in the YAML.
- **Valid Step References:** Any step name referenced in a `rule.run` list must correspond to a defined step in the playbook. We will perform a cross-reference check: for each case that has a `run` with step names, verify that each name indeed exists under the `steps` section. This catches typos or references to removed/undefined steps. If an invalid reference is found, the playbook is invalid. (Similarly, if tasks are referenced by name in a `run`, those must exist in the `tasks` definitions.)
- **No Mixing Actions with Step Transitions:** The validator will ensure that each case’s run is homogeneous. If any case’s `run` list contains at least one step name (transition) and at least one action/task (in-place execution), that is an error. This check may be implemented by examining the list: e.g., if the list items are supposed to be either all strings (step references) or all mappings (action definitions). We can enforce this via schema (using oneOf logic – the `run` field can be either a list of strings or a list of action objects). A playbook that violates this (mixes types in one list) will be rejected as invalid. This rule upholds the design principle that a single step’s case cannot have a hybrid outcome.
- **Rule and Case Structure:** Each step must have a `rule` key. Each rule should have at least one case. Optionally, we might also validate that there is at least one terminal condition (either an unconditional case or some way the workflow can end) to ensure no infinite loops, but this veers into logical validation. Primarily, the syntax and structural validity are enforced. We will also ensure each `case` entry has a `case` condition expression (except perhaps we might allow a default case if written as `case: default` or `case: "{{ True }}"` convention) and a `run` key (even if run can sometimes be empty to indicate an end).
- **No Orphan Tasks:** If the playbook defines a separate `tasks` section (reusable task definitions), the validator will warn or error if any task is defined but never used, or if tasks reference undefined sub-tasks (depending on playbook capabilities). This is to catch potential mistakes, though it might be a warning rather than a strict error. (This is an additional rule for completeness – focusing on steps is primary.)

All these validation rules ensure the workflow playbook is internally consistent. By catching issues at upload/registration time (before execution), we can fail fast and provide clear error messages to the user. For example, if a `run` references a step "ReviewOrder" that doesn’t exist, the error might be: _"Step 'ReviewOrder' referenced in step 'ApproveOrder' is not defined."_ If a case mixes actions and steps, the error might be: _"Invalid workflow definition: step 'X' has a case that mixes transitions and actions in one run block."_

The validation schema can be expressed in JSON Schema or Python classes. For instance:
```yaml
Step:
  type: object
  properties:
    rule:
      type: array
      items: 
        type: object
        properties:
          case: { type: string }      # Jinja2 condition expression
          run:                       
            oneOf:
              - type: array          # Option 1: list of step transitions (strings)
                items: { type: string }
              - type: array          # Option 2: list of action objects
                items: { $ref: '#/definitions/Action' }
```

This conveys that run must be either an array of strings (step names) or an array of Action objects (not a mix). Additional checks (unique names, valid references) go beyond basic schema and will be handled in code after parsing the YAML.

## Action Model: Tasks and Actions

In our workflow model, actions are the smallest execution primitives, and tasks are named collections of actions. We clarify their semantics as follows:
- **Actions as Atomic Operations:** An **action** is a single, atomic operation with a specified `type`. For example, an action could be of type "http" (to make an HTTP request), "postgres" (to run an SQL query), "shell" (to execute a shell command), etc. All the keys under an action (besides it's type) are parameters for that action type. For instance, a HTTP action might have keys like `method`, `url`, `headers`, etc. Actions do not have intrinsic names; they are defined in-line. They are executed in the context they appear and are not directly reusable by name – think of them as one-off commands or calls. The engine will have a dispatcher that looks at the action corresponding field value and invokes the corresponding handler (e.g., an HTTP client, a database client, etc., with the given parameters).
- **Tasks as Named Sequences:** A **task** is essentially a wrapper that gives a name to one or more actions (or even a sequence of other tasks, if nesting is supported). Tasks are the reusable logic units. They DO have names, and they can be referenced in step `run` lists. For example, one might define a task named `send_welcome_email` composed of a series of actions (perhaps an HTTP call to an email API followed by a database update). Then in a step’s `rule`, you could put `run: [send_welcome_email]` to execute all the actions defined in that task. When a task is referenced by name in a `run`, the engine will lookup the task definition and execute its actions in sequence if `parallel` attribute is not flaged.
- **Only Steps and Tasks are Referable:** The design choice that only steps and tasks have names (identifiers) is intentional. Steps and tasks represent higher-level logical units that you might want to jump to or reuse in multiple places. Actions, on the other hand, are meant to be executed where they are declared. This prevents confusion between reusing a block of logic (task) vs executing a singular action. It also aligns with typical workflow/BPMN design: you name activities (tasks) and states, but the atomic actions inside them don’t need global names. By not naming actions, we avoid an explosion of identifiers and keep the YAML definitions concise.
- **Action Execution Context:** Actions execute within the context of the current step and possibly produce outputs or modify the workflow state (for example, an HTTP action might fetch data and store it into a context variable). The YAML might allow capturing action results into variables which can then be used in later conditions or actions (this is likely handled by a `context` object in code). The action handlers will update the execution context accordingly. Tasks being just groupings of actions means they don’t have their own scope; they execute actions back-to-back as if they were inlined at the call site.
- Example: An illustrative snippet for actions and tasks:
```yaml
tasks:
  - name: send_welcome_email
    - action: http
      method: POST
      url: "https://api.mailservice.com/send"
      body: "{{ user.email_body }}"
    - action: postgres
      query: "UPDATE users SET welcome_sent=true WHERE user_id={{ user.id }}"

steps:
  - name: WelcomeUser
    rule:
      - case: "{{ user.new_account }}"
        run:
          - task: send_welcome_email   # refers to the named task
      - case: "{{ not user.new_account }}"
        run: []  # do nothing (end branch)
```

In this example, `send_welcome_email` is a reusable task composed of two actions. The step `WelcomeUser` uses the task name in its `run`. The engine will execute the HTTP action then the Postgres action as part of the `WelcomeUser` step when the condition matches. Neither the HTTP nor Postgres action has a name – they’re identified only by action type and executed immediately in sequence. This demonstrates the clear distinction: `WelcomeUser` (step) and `send_welcome_email` (task) have names and appear as nodes in the workflow logic, whereas the actions are implementation details encapsulated by those nodes.

- **Error Handling for Actions:** If an action fails (throws an exception, returns an error), how the engine handles it can be configured (perhaps via retry strategies or error cases in the rule definitions). While not the main focus here, the architecture will include error propagation or the ability for steps to catch errors (possibly via special case conditions like `case: "{{ last_error }}"` to handle failures).

By structuring actions and tasks this way, we maintain clarity in the YAML: high-level flow is driven by steps and tasks (named and reusable), and the low-level implementation of what each step/task does is defined by actions (with concrete parameters). This separation also simplifies extending the system with new action types (just add a new handler for that type, without affecting the workflow schema or execution logic).

---

# DSL Specification Overview
The specification defines the data models, semantics, and validation rules for Playbooks, Steps, Tasks, and Actions to reflect the Workflow DSL YAML structure. The relationships are as follows:

## Playbook Specification
- **Playbook**: Top-level workflow definition containing:
  - An **environment** (global variables/config).
  - A list of reusable **tasks** definitions.
  - A list of **steps** that form the workflow.
  - Other metadata like name, version, etc., as needed.

## Step Specification
- **Step**: A unit of workflow logic that can include:
  - A **name** (identifier for routing).
  - A list of **tasks** (by reference to the named tasks defined in the playbook).
  - A list of **actions** (inlined actions to execute directly in this step).
  - A **rule** block for transition (conditional routing) after execution of the step.
  - A **parallel** flag (boolean) indicating if the tasks/actions in this step should run concurrently.

## Task Specification
- **Task**: A reusable sequence of actions, defined once and referenced by steps. Each task has:
  - A **name** (identifier to call the task).
  - A list of **actions** (the commands or calls that comprise this task’s procedure).
  - A **parallel** flag indicating if its actions should execute in parallel.

## Action Specification
- **Action**: The smallest execution unit, representing a single operation. Each action is defined by:
  - An **action** (identifying the category or executor, e.g., postgres, http, shell).
  - A **method** (specific operation to perform, e.g., create_table for a database, get for an HTTP request).
  - Parameters necessary for that action (e.g., SQL statement, API endpoint, shell command, etc.).
  - An optional **parallel** flag (if an action can spawn internal parallel operations – usually this is not needed at the single action level, so it may be reserved for future extension or simply ignored in normal actions).

---

## Environment and Context Specification

- **Environment/Context**: A dictionary of variables provided in `environment` (e.g., configuration like DB connection strings, or initial workflow variables). This will be loaded into a **Context** object at runtime and used for templating and passing data between actions.
  - As the workflow runs, the context is updated with results from actions (e.g., an action can store output into a context variable).
  - This context is what Jinja2 expressions will evaluate against.

---

## Tasks vs Actions Specification

- **Tasks**: Containers of actions, not executable on their own. Tasks are modular building blocks (similar to subroutines) and are reusable across steps.
- **Actions**: Concrete, atomic operations that perform specific tasks (e.g., API calls, database queries). Actions are executed where they are declared and are not reusable by name.

---

## Step Semantics Specification: Rule-Driven Transitions

Each **step** in the workflow represents a state or node in the process. The `rule` block within each step drives transitions and defines the workflow's control flow. Key rules include:

1. **Mandatory Rule per Step**: Every step must define a `rule` consisting of one or more cases.
2. **Case Run Modes**:
   - **Transition to other steps**: Specifies a transition to another step(s).
   - **In-place task execution**: Executes tasks or actions within the current step.
3. **No Mixed Run Modes**: A single `case` cannot mix transitions and in-place actions.
4. **Exclusive or Priority-based Cases**: Cases are evaluated in order, and the first matching case is executed.
5. **Explicit Branch Termination**: If no case matches, the branch ends.
6. **No Implicit Step Sequencing**: All transitions must be explicitly defined.

---

## Validation Rules Specification

To ensure playbooks are well-formed, the following validation rules will be enforced:

1. **Unique Step and Task Names**: All step and task names must be unique.
2. **Valid Step References**: All step references in `rule.run` must correspond to defined steps.
3. **No Mixing Actions with Step Transitions**: Each case’s `run` must be homogeneous (either all transitions or all actions).
4. **Rule and Case Structure**: Each step must have a `rule` with at least one case.
5. **No Orphan Tasks**: Tasks must be referenced in steps; unused tasks will raise warnings.

---

# Alignment with Formal Process Models (Process Mining, EPC, Petri Nets)

The NoETL DSL is aligned with formal process modeling standards:

- **Event-Driven Process Chains (EPC)**: Steps and rules correspond to functions and connectors in EPCs.
- **Petri Nets**: Steps act as places, and rules act as transitions, enabling token-based execution.
- **Process Mining**: Structured event logs enable conformance checking and process analysis.

Our step-based rule execution approach is aligned with process-oriented modeling standards. By making the workflow an explicit state machine, we can leverage the theory and best practices of well-known process modeling formalisms:

![Local Diagram](./images/event_driven_process_chain.png)

_An Event-Driven Process Chain example: an Activity (green) splits into two Events (pink) via a connector, leading to two different follow-up Activities. This illustrates explicit branching logic, similar to how a step’s rule can direct the workflow down different paths._
## Event-Driven Process Chains
**Event-Driven Process Chains (EPC):** EPCs represent processes as an **ordered graph of events and functions**, connected by logical connectors (AND, OR, XOR) to model decisions and parallelism. Our workflow steps mirror the functions/activities in EPC, and the conditions in `rule.case` act like the _events/conditions_ that determine which path follows. Notably, EPC requires that you cannot have two functions directly following each other without a connector – there must be a rule (connector) between them. This corresponds to our rule that no two steps implicitly follow one another without an explicit transition. Every fork or decision in our YAML is explicitly encoded in the `rule` logic (analogous to an XOR/AND connector). For example, a step with two possible next steps is akin to an XOR-split in EPC (one or the other branch taken based on a condition), or if both next steps are taken, an AND-split. By enforcing explicit case conditions and not allowing implicit fall-through, we ensure the workflow structure can be interpreted as a clear directed graph of states with connectors, much like an EPC diagram. This makes the process easy to understand and visualize (a major strength of EPC is its simplicity and readability).

## Petri Nets
**Petri Nets:** Petri nets are a more formal foundation for process modeling, defining processes as a bipartite graph of _places_ (states) and _transitions_ (events) with tokens flowing through the net. Our architecture can be mapped to a Petri net interpretation: **steps** in the workflow can be seen as _places_ (holding a token (context) when that step is active), and the evaluation and firing of a rule’s case acts as a _transition_ that consumes the token from the current step and produces token(s) in the next step(s). When a step transitions to multiple steps, it’s like a Petri net transition with multiple output places – resulting in multiple tokens (branches) and thus parallel execution (similar to an AND-split). The rule conditions are like guards enabling certain transitions. Importantly, Petri nets provide an exact mathematical semantics for execution, meaning the behavior of the net (reachability, concurrency, deadlocks) is well-defined. By modeling our workflow as a state-transition system, we can leverage these semantics. In fact, our workflow engine is essentially executing a state-transition system (token-based). For example, when no case matches and the branch ends, that is analogous to a token reaching a place with no outbound transitions (an end place). Petri nets also highlight properties like **concurrency** and **synchronization**. While our current design allows concurrency via parallel transitions, it does not yet detail synchronization (an AND-join where two branches must converge before continuing). However, the structure would allow adding a special step that waits for multiple branches to complete (similar to a join place in a Petri net). By keeping the model close to Petri nets, we ensure that we can analyze the workflow for soundness (e.g., no infinite loops or deadlocks if the Petri net is bounded and acyclic, etc.). It also means we could visualize a YAML playbook as a Petri net diagram, aiding understanding.

Tokens in the Petri net correspond to the context being passed through the workflow execution.

| **Petri Net Concept**         | **Workflow Concept**                                                   |
|------------------------------|------------------------------------------------------------------------|
| **Place**                    | A **step** (holding state; can be active/inactive)                     |
| **Token**                    | The **context object** flowing through execution                       |
| **Transition**               | The evaluation/firing of a **case in a rule**                          |
| **Arc from place to transition** | Indicates a step is ready to evaluate its rule                   |
| **Arc from transition to place** | Indicates which step(s) are activated after a case fires         |
| **Multiple output places**   | A transition to **multiple next steps (parallel execution)**           |
| **Multiple input places**    | A join step waiting for **multiple branches to finish (not yet in)**   |

- Holding a context (token) in a step (place)
- Evaluating the rule block (transition guard)
- Consuming the context from the current step
- Producing one or more new active steps with copies (or branches) of the context

This Petri net analogy isn’t just academic — it means we can:
- Reason about reachability, concurrency, and branch coverage
- Validate for deadlocks, infinite loops, or soundness
- Visualize the workflow graphically as tokens flowing between labeled places

If we need to model joins, you’ll need to track token presence in multiple steps and define a rule like:
```yaml
rule:
  - case: "{{ all(branch1_done, branch2_done) }}"
    run:
      - step: continue_step
```
Or we could add engine-level semantics for an AND-join, which is directly Petri net-native.

## Process Mining
**Process Mining:** In process mining, event logs from executed processes are analyzed to discover the underlying process model or check conformance to a model. Our workflow service is designed to produce structured events (step start, step end, task run, etc.), which can serve as an event log for process mining tools. Because our execution model is explicitly defined (no hidden transitions), the event log can be directly mapped back to the defined workflow model, or even used to rediscover the model. Techniques exist to derive Petri nets, BPMN diagrams, or EPCs from event logs, and our approach ensures the log and the model correspond closely (each step and transition in the log is expected by the design). This alignment makes **conformance checking** straightforward – one can verify that the workflow executed as per the defined rules (any deviation would indicate either a bug or an out-of-spec scenario). Moreover, the explicit modeling of rules and transitions is in the spirit of process mining’s goal to make sense of real execution data. By having a formal underpinning, we can answer questions like: _Did the workflow ever enter an unexpected state? Which conditions were most frequently true? How often did we fork into parallel steps?_ – all using the event data. Additionally, if we ever needed to integrate with process mining frameworks or export our workflows, the fact that we essentially implement a state-transition (Petri-net-like) system means we can export to standard representations like [PNML](https://en.wikipedia.org/wiki/Petri_Net_Markup_Language) (Petri Net Markup) or BPMN diagrams.

--- 
## Conformance to Standards
By incorporating these **principles**, we ensure our architecture isn’t reinventing process flow concepts in an incompatible way, but rather conforms to well-known patterns. For instance, **BPMN (Business Process Model and Notation)**, while not explicitly mentioned, is another process standard that has tasks, gateways (for decisions), and sequence flows – our steps and rules fulfill similar roles. In BPMN terms, each step with a rule is like a gateway that can lead to different tasks. The prohibition of implicit transitions echoes BPMN’s requirement that each task must flow into another via sequence flow connectors. Our approach is essentially a code-based (YAML-defined) realization of these modeling concepts.  




In summary, the proposed architecture stands on a solid theoretical foundation: it uses explicit state transitions (like Petri nets, where the engine is operating like a token-driven Petri net, with all the clarity and analytical power that brings) and branching logic (like EPC connectors) to define the workflow, which ensures the process is well-structured and analyzable. This not only helps during design and implementation (we avoid ambiguous cases and can reason about the flow clearly), but also later during maintenance and analysis (logs can be interpreted with the help of process mining to improve or audit the workflows). The simplicity of the step-case model combined with the rigor of explicit transitions achieves the balance highlighted in EPC’s success – simplicity and clarity of notation with the power to model complex behavior. Each development decision in this roadmap was made to uphold these principles and to ensure the workflow service is aligned with industry standards for process modeling and execution.

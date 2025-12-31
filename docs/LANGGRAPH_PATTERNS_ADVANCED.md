# 🔥 LangGraph Advanced Patterns & Architectures

> **Part 2 of LangChain/LangGraph Documentation Series**  
> **Focus:** Advanced patterns, complex workflows, and production architectures

---

## 📑 Table of Contents

1. [State Management Deep Dive](#1-state-management-deep-dive)
2. [Graph Patterns](#2-graph-patterns)
3. [Multi-Agent Architectures](#3-multi-agent-architectures)
4. [Workflow Patterns](#4-workflow-patterns)
5. [Persistence & Checkpointing](#5-persistence--checkpointing)
6. [Production Deployment](#6-production-deployment)

---

# 1. State Management Deep Dive

## 1.1 State Schema Patterns

### Immutable State Pattern

```python
from typing import TypedDict, Annotated
from dataclasses import dataclass, field
import operator

# Pattern 1: TypedDict with Annotations
class ImmutableState(TypedDict):
    messages: Annotated[list, operator.add]  # Append-only
    context: Annotated[dict, lambda old, new: {**old, **new}]  # Merge
    
# Pattern 2: Dataclass for complex state
@dataclass(frozen=True)
class AgentConfig:
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096

class ComplexState(TypedDict):
    config: AgentConfig
    messages: Annotated[list, operator.add]
    counters: Annotated[dict[str, int], lambda a, b: {k: a.get(k, 0) + b.get(k, 0) for k in set(a) | set(b)}]
```

### State with Validation

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class ValidatedState(BaseModel):
    messages: List[str] = Field(default_factory=list)
    current_step: str = Field(default="start")
    error_count: int = Field(default=0, ge=0, le=5)
    
    @validator('current_step')
    def validate_step(cls, v):
        valid_steps = ['start', 'process', 'review', 'complete']
        if v not in valid_steps:
            raise ValueError(f"Step must be one of {valid_steps}")
        return v
    
    class Config:
        validate_assignment = True
```

## 1.2 State Reducers

```python
from typing import Callable, Any

# Custom reducer for complex merging
def merge_with_priority(old: dict, new: dict) -> dict:
    """Merge dicts with priority levels."""
    result = old.copy()
    for key, value in new.items():
        if key in result and isinstance(value, dict):
            result[key] = merge_with_priority(result[key], value)
        else:
            result[key] = value
    return result

# Reducer for list operations
def list_operations(old: list, new: dict) -> list:
    """Support append, prepend, remove operations."""
    result = old.copy()
    if 'append' in new:
        result.extend(new['append'])
    if 'prepend' in new:
        result = new['prepend'] + result
    if 'remove' in new:
        result = [x for x in result if x not in new['remove']]
    return result

class AdvancedState(TypedDict):
    data: Annotated[dict, merge_with_priority]
    items: Annotated[list, list_operations]
```

---

# 2. Graph Patterns

## 2.1 Linear Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       LINEAR PIPELINE PATTERN                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐            │
│   │ START│───►│NODE 1│───►│NODE 2│───►│NODE 3│───►│ END  │            │
│   └──────┘    └──────┘    └──────┘    └──────┘    └──────┘            │
│                                                                         │
│   Use Case: Sequential processing, ETL pipelines, document processing  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```python
from langgraph.graph import StateGraph, END, START

class PipelineState(TypedDict):
    data: str
    processed: list

def step1(state):
    return {"data": state["data"].upper(), "processed": ["step1"]}

def step2(state):
    return {"data": state["data"] + " - PROCESSED", "processed": ["step2"]}

def step3(state):
    return {"data": f"Final: {state['data']}", "processed": ["step3"]}

graph = StateGraph(PipelineState)
graph.add_node("step1", step1)
graph.add_node("step2", step2)
graph.add_node("step3", step3)

graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)

pipeline = graph.compile()
```

## 2.2 Branching Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       BRANCHING PATTERN                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                           ┌──────────┐                                  │
│                           │  START   │                                  │
│                           └────┬─────┘                                  │
│                                │                                        │
│                           ┌────▼─────┐                                  │
│                           │ CLASSIFY │                                  │
│                           └────┬─────┘                                  │
│                                │                                        │
│              ┌─────────────────┼─────────────────┐                     │
│              │                 │                 │                      │
│         ┌────▼────┐       ┌────▼────┐       ┌────▼────┐                │
│         │ PATH A  │       │ PATH B  │       │ PATH C  │                │
│         └────┬────┘       └────┬────┘       └────┬────┘                │
│              │                 │                 │                      │
│              └─────────────────┼─────────────────┘                     │
│                                │                                        │
│                           ┌────▼─────┐                                  │
│                           │   END    │                                  │
│                           └──────────┘                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```python
class BranchingState(TypedDict):
    input: str
    category: str
    result: str

def classify(state):
    # Classify input
    text = state["input"].lower()
    if "urgent" in text:
        return {"category": "urgent"}
    elif "question" in text:
        return {"category": "question"}
    else:
        return {"category": "general"}

def handle_urgent(state):
    return {"result": "🚨 URGENT: Prioritized handling"}

def handle_question(state):
    return {"result": "❓ QUESTION: Providing answer..."}

def handle_general(state):
    return {"result": "📝 GENERAL: Standard processing"}

def route(state):
    return state["category"]

graph = StateGraph(BranchingState)
graph.add_node("classify", classify)
graph.add_node("urgent", handle_urgent)
graph.add_node("question", handle_question)
graph.add_node("general", handle_general)

graph.add_edge(START, "classify")
graph.add_conditional_edges(
    "classify",
    route,
    {
        "urgent": "urgent",
        "question": "question",
        "general": "general"
    }
)
graph.add_edge("urgent", END)
graph.add_edge("question", END)
graph.add_edge("general", END)

app = graph.compile()
```

## 2.3 Cyclic Pattern (Retry/Refinement)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CYCLIC PATTERN (WITH RETRY)                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│           ┌──────┐                                                      │
│           │START │                                                      │
│           └──┬───┘                                                      │
│              │                                                          │
│              ▼                                                          │
│        ┌──────────┐                                                     │
│   ┌───►│ GENERATE │                                                     │
│   │    └────┬─────┘                                                     │
│   │         │                                                           │
│   │         ▼                                                           │
│   │    ┌──────────┐                                                     │
│   │    │ VALIDATE │                                                     │
│   │    └────┬─────┘                                                     │
│   │         │                                                           │
│   │    ┌────┴────┐                                                      │
│   │    │         │                                                      │
│   │   FAIL      PASS                                                    │
│   │    │         │                                                      │
│   │    ▼         ▼                                                      │
│   │ ┌──────┐  ┌──────┐                                                  │
│   └─┤REFINE│  │ END  │                                                  │
│     └──────┘  └──────┘                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```python
class CyclicState(TypedDict):
    input: str
    output: str
    valid: bool
    attempts: int
    max_attempts: int

def generate(state):
    # Generate output
    return {
        "output": f"Generated from: {state['input']}",
        "attempts": state.get("attempts", 0) + 1
    }

def validate(state):
    # Validate output
    is_valid = len(state["output"]) > 10
    return {"valid": is_valid}

def refine(state):
    # Refine the output
    return {"input": f"Improved: {state['input']}"}

def should_continue(state):
    if state["valid"]:
        return "end"
    elif state["attempts"] >= state.get("max_attempts", 3):
        return "end"
    else:
        return "refine"

graph = StateGraph(CyclicState)
graph.add_node("generate", generate)
graph.add_node("validate", validate)
graph.add_node("refine", refine)

graph.add_edge(START, "generate")
graph.add_edge("generate", "validate")
graph.add_conditional_edges(
    "validate",
    should_continue,
    {
        "end": END,
        "refine": "refine"
    }
)
graph.add_edge("refine", "generate")  # Cycle back

app = graph.compile()
```

## 2.4 Parallel Execution Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PARALLEL EXECUTION PATTERN                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                        ┌──────────┐                                     │
│                        │  START   │                                     │
│                        └────┬─────┘                                     │
│                             │                                           │
│                        ┌────▼─────┐                                     │
│                        │  SPLIT   │                                     │
│                        └────┬─────┘                                     │
│                             │                                           │
│         ┌───────────────────┼───────────────────┐                      │
│         │                   │                   │                       │
│    ┌────▼────┐         ┌────▼────┐         ┌────▼────┐                 │
│    │ WORKER1 │         │ WORKER2 │         │ WORKER3 │                 │
│    │ (async) │         │ (async) │         │ (async) │                 │
│    └────┬────┘         └────┬────┘         └────┬────┘                 │
│         │                   │                   │                       │
│         └───────────────────┼───────────────────┘                      │
│                             │                                           │
│                        ┌────▼─────┐                                     │
│                        │  MERGE   │                                     │
│                        └────┬─────┘                                     │
│                             │                                           │
│                        ┌────▼─────┐                                     │
│                        │   END    │                                     │
│                        └──────────┘                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```python
import asyncio
from typing import Annotated
import operator

class ParallelState(TypedDict):
    input: str
    results: Annotated[list, operator.add]
    final: str

def split_work(state):
    # Split work into chunks
    return {"input": state["input"]}

async def worker1(state):
    await asyncio.sleep(0.5)  # Simulate work
    return {"results": [f"Worker1: {state['input'][:10]}"]}

async def worker2(state):
    await asyncio.sleep(0.5)
    return {"results": [f"Worker2: {state['input'][10:20]}"]}

async def worker3(state):
    await asyncio.sleep(0.5)
    return {"results": [f"Worker3: {state['input'][20:]}"]}

def merge_results(state):
    return {"final": " | ".join(state["results"])}

# For true parallel execution, use subgraphs with fan-out/fan-in
graph = StateGraph(ParallelState)
graph.add_node("split", split_work)
graph.add_node("worker1", worker1)
graph.add_node("worker2", worker2)
graph.add_node("worker3", worker3)
graph.add_node("merge", merge_results)

graph.add_edge(START, "split")
# Fan-out to workers
graph.add_edge("split", "worker1")
graph.add_edge("split", "worker2")
graph.add_edge("split", "worker3")
# Fan-in to merge
graph.add_edge("worker1", "merge")
graph.add_edge("worker2", "merge")
graph.add_edge("worker3", "merge")
graph.add_edge("merge", END)

app = graph.compile()
```

---

# 3. Multi-Agent Architectures

## 3.1 Hierarchical Multi-Agent

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HIERARCHICAL MULTI-AGENT                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                         ┌─────────────────┐                             │
│                         │   ORCHESTRATOR  │                             │
│                         │   ─────────────  │                             │
│                         │   High-level    │                             │
│                         │   planning      │                             │
│                         └────────┬────────┘                             │
│                                  │                                      │
│            ┌─────────────────────┼─────────────────────┐               │
│            │                     │                     │                │
│    ┌───────▼───────┐    ┌───────▼───────┐    ┌───────▼───────┐        │
│    │  SUPERVISOR A │    │  SUPERVISOR B │    │  SUPERVISOR C │        │
│    │  ───────────  │    │  ───────────  │    │  ───────────  │        │
│    │  Team lead    │    │  Team lead    │    │  Team lead    │        │
│    └───────┬───────┘    └───────┬───────┘    └───────┬───────┘        │
│            │                    │                    │                  │
│    ┌───────┴───────┐    ┌───────┴───────┐    ┌───────┴───────┐        │
│    │               │    │               │    │               │         │
│  ┌─▼─┐  ┌─▼─┐  ┌─▼─┐  ┌─▼─┐  ┌─▼─┐  ┌─▼─┐  ┌─▼─┐  ┌─▼─┐  ┌─▼─┐      │
│  │W1 │  │W2 │  │W3 │  │W4 │  │W5 │  │W6 │  │W7 │  │W8 │  │W9 │      │
│  └───┘  └───┘  └───┘  └───┘  └───┘  └───┘  └───┘  └───┘  └───┘      │
│                                                                         │
│   Workers: Specialized agents for specific tasks                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```python
class HierarchicalState(TypedDict):
    task: str
    current_supervisor: str
    assigned_worker: str
    worker_results: Annotated[list, operator.add]
    final_result: str

class Orchestrator:
    """Top-level coordinator."""
    
    def __init__(self, llm):
        self.llm = llm
        self.supervisors = ["design", "development", "testing"]
    
    def plan(self, state: HierarchicalState) -> HierarchicalState:
        # Create high-level plan
        prompt = f"""
        Task: {state['task']}
        Available teams: {self.supervisors}
        
        Create a plan assigning work to teams.
        """
        response = self.llm.invoke(prompt)
        return {"current_supervisor": "design"}

class Supervisor:
    """Team lead managing workers."""
    
    def __init__(self, llm, workers: list):
        self.llm = llm
        self.workers = workers
    
    def delegate(self, state: HierarchicalState) -> HierarchicalState:
        # Assign to appropriate worker
        return {"assigned_worker": self.workers[0]}

class Worker:
    """Specialized worker agent."""
    
    def __init__(self, llm, specialty: str):
        self.llm = llm
        self.specialty = specialty
    
    def execute(self, state: HierarchicalState) -> HierarchicalState:
        # Do the actual work
        return {"worker_results": [f"{self.specialty}: Completed"]}
```

## 3.2 Collaborative Multi-Agent

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COLLABORATIVE MULTI-AGENT                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│          ┌─────────────────────────────────────────────┐                │
│          │              SHARED WORKSPACE               │                │
│          │  ─────────────────────────────────────────  │                │
│          │  • Messages    • Documents    • State       │                │
│          └───────────────────────┬─────────────────────┘                │
│                                  │                                      │
│      ┌───────────────────────────┼───────────────────────────┐         │
│      │                           │                           │          │
│  ┌───▼───┐                   ┌───▼───┐                   ┌───▼───┐     │
│  │AGENT A│◄─────────────────►│AGENT B│◄─────────────────►│AGENT C│     │
│  │───────│                   │───────│                   │───────│     │
│  │Critic │   Collaboration   │Writer │   Collaboration   │Editor │     │
│  └───────┘                   └───────┘                   └───────┘     │
│      │                           │                           │          │
│      │                           │                           │          │
│      └───────────────────────────┴───────────────────────────┘         │
│                         Peer-to-peer interaction                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```python
class CollaborativeState(TypedDict):
    task: str
    discussion: Annotated[list[dict], operator.add]
    consensus_reached: bool
    final_output: str

class CollaborativeAgent:
    def __init__(self, llm, name: str, role: str):
        self.llm = llm
        self.name = name
        self.role = role
    
    def discuss(self, state: CollaborativeState) -> CollaborativeState:
        # Review previous discussion
        history = "\n".join([
            f"{d['agent']}: {d['message']}" 
            for d in state.get("discussion", [])
        ])
        
        prompt = f"""
        You are {self.name}, a {self.role}.
        Task: {state['task']}
        
        Discussion so far:
        {history}
        
        Provide your input or agree with others' suggestions:
        """
        
        response = self.llm.invoke(prompt)
        
        return {
            "discussion": [{
                "agent": self.name,
                "role": self.role,
                "message": response.content
            }]
        }

def check_consensus(state: CollaborativeState) -> str:
    # Check if agents have reached agreement
    if len(state["discussion"]) >= 6:  # 2 rounds each
        return "end"
    return "continue"

# Build collaborative graph
graph = StateGraph(CollaborativeState)

critic = CollaborativeAgent(llm, "Critic", "critical reviewer")
writer = CollaborativeAgent(llm, "Writer", "content creator")
editor = CollaborativeAgent(llm, "Editor", "quality editor")

graph.add_node("critic", critic.discuss)
graph.add_node("writer", writer.discuss)
graph.add_node("editor", editor.discuss)

# Round-robin discussion
graph.add_edge(START, "writer")
graph.add_edge("writer", "critic")
graph.add_edge("critic", "editor")
graph.add_conditional_edges(
    "editor",
    check_consensus,
    {"continue": "writer", "end": END}
)
```

## 3.3 Competitive Multi-Agent

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    COMPETITIVE MULTI-AGENT                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                           ┌───────────┐                                 │
│                           │   JUDGE   │                                 │
│                           │ ───────── │                                 │
│                           │ Evaluates │                                 │
│                           │ all       │                                 │
│                           │ solutions │                                 │
│                           └─────┬─────┘                                 │
│                                 │                                       │
│               ┌─────────────────┼─────────────────┐                    │
│               │                 │                 │                     │
│         ┌─────▼─────┐     ┌─────▼─────┐     ┌─────▼─────┐             │
│         │ SOLVER A  │     │ SOLVER B  │     │ SOLVER C  │             │
│         │ ───────── │     │ ───────── │     │ ───────── │             │
│         │ Approach 1│     │ Approach 2│     │ Approach 3│             │
│         └───────────┘     └───────────┘     └───────────┘             │
│                                                                         │
│   Each solver proposes solution, judge selects best                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

```python
class CompetitiveState(TypedDict):
    problem: str
    solutions: Annotated[list[dict], operator.add]
    winner: dict
    explanation: str

class Solver:
    def __init__(self, llm, approach: str):
        self.llm = llm
        self.approach = approach
    
    def solve(self, state: CompetitiveState) -> CompetitiveState:
        prompt = f"""
        Problem: {state['problem']}
        Approach: {self.approach}
        
        Provide your solution using this approach.
        """
        response = self.llm.invoke(prompt)
        return {
            "solutions": [{
                "approach": self.approach,
                "solution": response.content,
                "score": 0  # To be filled by judge
            }]
        }

class Judge:
    def __init__(self, llm):
        self.llm = llm
    
    def evaluate(self, state: CompetitiveState) -> CompetitiveState:
        solutions_text = "\n\n".join([
            f"Approach: {s['approach']}\nSolution: {s['solution']}"
            for s in state["solutions"]
        ])
        
        prompt = f"""
        Problem: {state['problem']}
        
        Solutions:
        {solutions_text}
        
        Evaluate each solution and select the best one.
        Explain your reasoning.
        """
        
        response = self.llm.invoke(prompt)
        
        # Parse winner (simplified)
        return {
            "winner": state["solutions"][0],
            "explanation": response.content
        }

# Build competitive graph
graph = StateGraph(CompetitiveState)

solver_a = Solver(llm, "divide-and-conquer")
solver_b = Solver(llm, "dynamic-programming")
solver_c = Solver(llm, "greedy")
judge = Judge(llm)

graph.add_node("solver_a", solver_a.solve)
graph.add_node("solver_b", solver_b.solve)
graph.add_node("solver_c", solver_c.solve)
graph.add_node("judge", judge.evaluate)

graph.add_edge(START, "solver_a")
graph.add_edge(START, "solver_b")
graph.add_edge(START, "solver_c")
graph.add_edge("solver_a", "judge")
graph.add_edge("solver_b", "judge")
graph.add_edge("solver_c", "judge")
graph.add_edge("judge", END)
```

---

# 4. Workflow Patterns

## 4.1 Approval Workflow

```python
from enum import Enum

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION = "revision_needed"

class ApprovalState(TypedDict):
    document: str
    author: str
    approvers: list[str]
    current_approver_index: int
    statuses: dict[str, ApprovalStatus]
    final_status: ApprovalStatus
    comments: Annotated[list, operator.add]

def submit_for_approval(state):
    return {
        "current_approver_index": 0,
        "statuses": {}
    }

def get_approval(state):
    """Simulate getting approval (would be interrupted in real app)."""
    approver = state["approvers"][state["current_approver_index"]]
    # In production, this would be interrupted for human input
    return {
        "statuses": {**state["statuses"], approver: ApprovalStatus.APPROVED},
        "comments": [f"{approver}: Approved"]
    }

def check_all_approved(state) -> str:
    all_approved = all(
        s == ApprovalStatus.APPROVED 
        for s in state["statuses"].values()
    )
    
    if len(state["statuses"]) < len(state["approvers"]):
        return "next_approver"
    elif all_approved:
        return "finalize"
    else:
        return "revision"

def next_approver(state):
    return {"current_approver_index": state["current_approver_index"] + 1}

def finalize(state):
    return {"final_status": ApprovalStatus.APPROVED}

def request_revision(state):
    return {"final_status": ApprovalStatus.REVISION}

graph = StateGraph(ApprovalState)
graph.add_node("submit", submit_for_approval)
graph.add_node("approval", get_approval)
graph.add_node("next", next_approver)
graph.add_node("finalize", finalize)
graph.add_node("revision", request_revision)

graph.add_edge(START, "submit")
graph.add_edge("submit", "approval")
graph.add_conditional_edges(
    "approval",
    check_all_approved,
    {
        "next_approver": "next",
        "finalize": "finalize",
        "revision": "revision"
    }
)
graph.add_edge("next", "approval")
graph.add_edge("finalize", END)
graph.add_edge("revision", END)
```

## 4.2 Error Recovery Pattern

```python
class ErrorRecoveryState(TypedDict):
    input: str
    output: str
    error: str | None
    error_count: int
    max_errors: int
    recovery_attempts: list

def main_process(state):
    try:
        # Main processing logic
        result = f"Processed: {state['input']}"
        return {"output": result, "error": None}
    except Exception as e:
        return {"error": str(e)}

def error_handler(state):
    return {
        "error_count": state.get("error_count", 0) + 1,
        "recovery_attempts": [f"Attempt {state.get('error_count', 0) + 1}"]
    }

def should_retry(state) -> str:
    if not state.get("error"):
        return "success"
    elif state.get("error_count", 0) >= state.get("max_errors", 3):
        return "fail"
    else:
        return "retry"

def recovery(state):
    # Attempt recovery/cleanup
    return {"input": f"Fixed: {state['input']}"}

def success(state):
    return {"output": f"✅ {state['output']}"}

def failure(state):
    return {"output": f"❌ Failed after {state['error_count']} attempts"}

graph = StateGraph(ErrorRecoveryState)
graph.add_node("process", main_process)
graph.add_node("error_handler", error_handler)
graph.add_node("recovery", recovery)
graph.add_node("success", success)
graph.add_node("failure", failure)

graph.add_edge(START, "process")
graph.add_conditional_edges(
    "process",
    should_retry,
    {
        "success": "success",
        "retry": "error_handler",
        "fail": "failure"
    }
)
graph.add_edge("error_handler", "recovery")
graph.add_edge("recovery", "process")
graph.add_edge("success", END)
graph.add_edge("failure", END)
```

---

# 5. Persistence & Checkpointing

## 5.1 SQLite Checkpointing

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Create SQLite checkpointer
checkpointer = SqliteSaver.from_conn_string("./checkpoints.db")

# Compile graph with persistence
app = graph.compile(checkpointer=checkpointer)

# Run with thread ID
config = {"configurable": {"thread_id": "session-123"}}
result = app.invoke({"input": "Hello"}, config)

# Later: Resume from checkpoint
state = app.get_state(config)
print(f"Current state: {state.values}")

# Get state history
history = app.get_state_history(config)
for checkpoint in history:
    print(f"Checkpoint: {checkpoint.config}")
```

## 5.2 PostgreSQL Checkpointing

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Create Postgres checkpointer
DATABASE_URL = "postgresql://user:pass@localhost/db"
checkpointer = PostgresSaver.from_conn_string(DATABASE_URL)

# Initialize tables
checkpointer.setup()

app = graph.compile(checkpointer=checkpointer)
```

## 5.3 State Rewind

```python
# Get state history
config = {"configurable": {"thread_id": "task-1"}}
history = list(app.get_state_history(config))

# Rewind to specific checkpoint
target_config = history[2].config  # Third state
app.update_state(config, history[2].values)

# Resume from that point
result = app.invoke(None, config)
```

---

# 6. Production Deployment

## 6.1 FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from langgraph.checkpoint.sqlite import SqliteSaver
import uuid

app = FastAPI()
checkpointer = SqliteSaver.from_conn_string("./production.db")
workflow = graph.compile(checkpointer=checkpointer)

class TaskRequest(BaseModel):
    input: str
    thread_id: Optional[str] = None

class TaskResponse(BaseModel):
    thread_id: str
    status: str
    result: Optional[dict] = None

@app.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        result = await workflow.ainvoke({"input": request.input}, config)
        return TaskResponse(
            thread_id=thread_id,
            status="completed",
            result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{thread_id}")
async def get_task(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = workflow.get_state(config)
    return {"thread_id": thread_id, "state": state.values}

@app.get("/tasks/{thread_id}/history")
async def get_task_history(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    history = list(workflow.get_state_history(config))
    return {"thread_id": thread_id, "history": [h.values for h in history]}
```

## 6.2 Monitoring & Observability

```python
from langchain.callbacks import OpenAICallbackHandler
from langsmith import traceable
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoredWorkflow:
    def __init__(self, workflow):
        self.workflow = workflow
        self.metrics = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "avg_duration": 0
        }
    
    @traceable(name="workflow_execution")
    async def run(self, input_data: dict, config: dict):
        start_time = time.time()
        self.metrics["total_runs"] += 1
        
        try:
            result = await self.workflow.ainvoke(input_data, config)
            self.metrics["successful_runs"] += 1
            duration = time.time() - start_time
            self._update_avg_duration(duration)
            
            logger.info(f"Workflow completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            self.metrics["failed_runs"] += 1
            logger.error(f"Workflow failed: {e}")
            raise
    
    def _update_avg_duration(self, new_duration):
        total = self.metrics["successful_runs"]
        old_avg = self.metrics["avg_duration"]
        self.metrics["avg_duration"] = (old_avg * (total - 1) + new_duration) / total
    
    def get_metrics(self):
        return self.metrics
```

---

> **📌 Next:** See `LANGGRAPH_EXAMPLES.md` for complete real-world examples

*Part 2 of 3 | LangChain/LangGraph Documentation Series*

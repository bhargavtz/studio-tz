# 🚀 LangChain & LangGraph - Complete Technical Documentation

> **Version:** 2.0 | **Last Updated:** December 2024  
> **Author:** Developer Documentation Team  
> **Style:** Teaching + Developer-to-Developer Technical Guide

---

## 📑 Table of Contents

1. [Introduction & Overview](#1-introduction--overview)
2. [Core Architecture](#2-core-architecture)
3. [LangChain Deep Dive](#3-langchain-deep-dive)
4. [LangGraph Deep Dive](#4-langgraph-deep-dive)
5. [Flowcharts & Diagrams](#5-flowcharts--diagrams)
6. [Practical Examples](#6-practical-examples)
7. [Advanced Patterns](#7-advanced-patterns)
8. [Best Practices](#8-best-practices)
9. [Troubleshooting Guide](#9-troubleshooting-guide)
10. [API Reference](#10-api-reference)

---

## 1. Introduction & Overview

## 1.1 What is LangChain?

**LangChain** is a powerful framework for developing applications powered by Large Language Models (LLMs). It provides:

| Feature | Description |
|---------|-------------|
| **Chains** | Sequences of LLM calls with logic |
| **Agents** | LLMs that can use tools and make decisions |
| **Memory** | Persistent conversation state |
| **Retrievers** | Document retrieval for RAG |
| **Tools** | External capabilities for agents |

### Why LangChain?

```text
┌─────────────────────────────────────────────────────────────┐
│                    WITHOUT LANGCHAIN                        │
├─────────────────────────────────────────────────────────────┤
│  ❌ Manual prompt engineering                               │
│  ❌ No memory management                                    │
│  ❌ Complex tool integration                                │
│  ❌ Difficult to chain multiple LLM calls                  │
│  ❌ No standardized patterns                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     WITH LANGCHAIN                          │
├─────────────────────────────────────────────────────────────┤
│  ✅ Structured prompt templates                             │
│  ✅ Built-in memory systems                                 │
│  ✅ Easy tool integration                                   │
│  ✅ Composable chains                                       │
│  ✅ Production-ready patterns                               │
└─────────────────────────────────────────────────────────────┘
```

## 1.2 What is LangGraph?

**LangGraph** extends LangChain to build **stateful, multi-actor applications** with LLMs. Think of it as:

> 🎯 **LangGraph = LangChain + State Machine + Graph-Based Workflows**

### Key Differences

```text
┌────────────────────┬────────────────────┬────────────────────┐
│     FEATURE        │     LANGCHAIN      │     LANGGRAPH      │
├────────────────────┼────────────────────┼────────────────────┤
│ Flow Control       │ Linear/Sequential  │ Graph-based        │
│ State Management   │ Basic Memory       │ Full State Machine │
│ Branching          │ Limited            │ Conditional Edges  │
│ Cycles             │ Not Supported      │ Full Support       │
│ Human-in-Loop      │ Manual             │ Built-in           │
│ Streaming          │ Basic              │ Advanced           │
│ Persistence        │ External           │ Built-in           │
└────────────────────┴────────────────────┴────────────────────┘
```

---

## 2. Core Architecture

## 2.1 LangChain Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         LANGCHAIN ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   Models    │    │   Prompts   │    │   Memory    │                 │
│  │  ─────────  │    │  ─────────  │    │  ─────────  │                 │
│  │  • LLMs     │    │  • Templates│    │  • Buffer   │                 │
│  │  • Chat     │    │  • Examples │    │  • Summary  │                 │
│  │  • Embed    │    │  • Selectors│    │  • Vector   │                 │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                 │
│         │                  │                  │                         │
│         └──────────────────┼──────────────────┘                         │
│                            ▼                                            │
│                    ┌───────────────┐                                    │
│                    │    CHAINS     │                                    │
│                    │  ───────────  │                                    │
│                    │  • LLMChain   │                                    │
│                    │  • Sequential │                                    │
│                    │  • Router     │                                    │
│                    └───────┬───────┘                                    │
│                            ▼                                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   Agents    │    │  Retrievers │    │    Tools    │                 │
│  │  ─────────  │    │  ─────────  │    │  ─────────  │                 │
│  │  • ReAct    │◄──►│  • Vector   │◄──►│  • Search   │                 │
│  │  • OpenAI   │    │  • BM25     │    │  • Code     │                 │
│  │  • Custom   │    │  • Hybrid   │    │  • API      │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2.2 LangGraph Architecture Overview

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         LANGGRAPH ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                        ┌───────────────────┐                            │
│                        │   STATE SCHEMA    │                            │
│                        │  ───────────────  │                            │
│                        │  TypedDict/Class  │                            │
│                        └─────────┬─────────┘                            │
│                                  │                                      │
│         ┌────────────────────────┼────────────────────────┐             │
│         ▼                        ▼                        ▼             │
│  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐     │
│  │   NODE 1    │          │   NODE 2    │          │   NODE 3    │     │
│  │  ─────────  │          │  ─────────  │          │  ─────────  │     │
│  │  Function   │ ──────►  │  Function   │ ──────►  │  Function   │     │
│  │  or Agent   │  edge    │  or Agent   │  edge    │  or Agent   │     │
│  └─────────────┘          └──────┬──────┘          └─────────────┘     │
│                                  │                                      │
│                           conditional                                   │
│                              edge                                       │
│                                  │                                      │
│                    ┌─────────────┴─────────────┐                       │
│                    ▼                           ▼                        │
│             ┌─────────────┐             ┌─────────────┐                │
│             │   NODE 4    │             │   NODE 5    │                │
│             │  ─────────  │             │  ─────────  │                │
│             │  Branch A   │             │  Branch B   │                │
│             └─────────────┘             └─────────────┘                │
│                    │                           │                        │
│                    └───────────┬───────────────┘                       │
│                                ▼                                        │
│                        ┌───────────────┐                               │
│                        │      END      │                               │
│                        └───────────────┘                               │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      CHECKPOINTER                                │   │
│  │  ─────────────────────────────────────────────────────────────  │   │
│  │  Persistence Layer: SQLite, PostgreSQL, Redis, Memory           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. LangChain Deep Dive

## 3.1 Installation

```bash
# Core LangChain
pip install langchain langchain-core langchain-community

# For specific providers
pip install langchain-openai        # OpenAI
pip install langchain-google-genai  # Google Gemini
pip install langchain-anthropic     # Anthropic Claude

# For vector stores
pip install chromadb faiss-cpu pinecone-client

# Complete installation
pip install langchain langchain-openai langchain-community chromadb
```

## 3.2 LLM Models

### 3.2.1 Basic LLM Usage

```python
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

# OpenAI GPT-4
openai_llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.7,
    max_tokens=4096,
    api_key="your-api-key"
)

# Google Gemini
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    google_api_key="your-api-key"
)

# Anthropic Claude
claude_llm = ChatAnthropic(
    model="claude-3-opus-20240229",
    temperature=0.7,
    anthropic_api_key="your-api-key"
)

# Invoke the model
response = openai_llm.invoke("Explain quantum computing in simple terms")
print(response.content)
```

### 3.2.2 Model Configuration Patterns

```python
from langchain_core.callbacks import StreamingStdOutCallbackHandler

# Streaming configuration
streaming_llm = ChatOpenAI(
    model="gpt-4",
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

# With retry logic
from langchain.llms.utils import retry

@retry(max_retries=3, backoff_factor=2)
def safe_invoke(llm, prompt):
    return llm.invoke(prompt)
```

## 3.3 Prompt Templates

### 3.3.1 Basic Templates

```python
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)

# Simple string template
simple_template = PromptTemplate(
    template="Tell me a {adjective} joke about {topic}",
    input_variables=["adjective", "topic"]
)

# Format the template
formatted = simple_template.format(adjective="funny", topic="programming")
# Output: "Tell me a funny joke about programming"
```

### 3.3.2 Chat Prompt Templates

```python
# Chat-style template with roles
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} assistant. Be {personality}."),
    ("human", "{user_input}"),
])

# With message history placeholder
chat_with_history = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])
```

### 3.3.3 Advanced Template Patterns

```python
from langchain_core.prompts import FewShotPromptTemplate

# Few-shot learning template
examples = [
    {"input": "happy", "output": "sad"},
    {"input": "tall", "output": "short"},
    {"input": "fast", "output": "slow"},
]

example_template = PromptTemplate(
    template="Input: {input}\nOutput: {output}",
    input_variables=["input", "output"]
)

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_template,
    prefix="Give the antonym of every input:",
    suffix="Input: {query}\nOutput:",
    input_variables=["query"]
)
```

## 3.4 Chains

### 3.4.1 LCEL (LangChain Expression Language)

```python
from langchain_core.output_parsers import StrOutputParser

# Modern LCEL chain
chain = (
    ChatPromptTemplate.from_template("Tell me about {topic}")
    | ChatOpenAI(model="gpt-4")
    | StrOutputParser()
)

# Invoke the chain
result = chain.invoke({"topic": "machine learning"})
```

### 3.4.2 Chain Composition

```python
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

# Parallel execution
parallel_chain = RunnableParallel(
    summary=summary_chain,
    analysis=analysis_chain,
    keywords=keyword_chain
)

# With passthrough
chain_with_context = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

## 3.5 Memory Systems

### 3.5.1 Conversation Buffer Memory

```python
from langchain.memory import ConversationBufferMemory

# Basic buffer memory
memory = ConversationBufferMemory(
    memory_key="history",
    return_messages=True
)

# Add messages
memory.save_context(
    {"input": "Hi, I'm John"},
    {"output": "Hello John! How can I help you?"}
)

# Retrieve history
history = memory.load_memory_variables({})
```

### 3.5.2 Summary Memory

```python
from langchain.memory import ConversationSummaryMemory

# Summary memory (compresses long conversations)
summary_memory = ConversationSummaryMemory(
    llm=ChatOpenAI(model="gpt-3.5-turbo"),
    memory_key="history"
)
```

### 3.5.3 Vector Store Memory

```python
from langchain.memory import VectorStoreRetrieverMemory
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# Vector memory for semantic search
vector_memory = VectorStoreRetrieverMemory(
    retriever=retriever
)
```

## 3.6 Tools & Agents

### 3.6.1 Creating Custom Tools

```python
from langchain.tools import Tool, StructuredTool
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Simple tool with decorator
@tool
def search_database(query: str) -> str:
    """Search the database for relevant information."""
    # Your search logic here
    return f"Results for: {query}"

# Structured tool with schema
class CalculatorInput(BaseModel):
    a: float = Field(description="First number")
    b: float = Field(description="Second number")
    operation: str = Field(description="Operation: add, subtract, multiply, divide")

@tool(args_schema=CalculatorInput)
def calculator(a: float, b: float, operation: str) -> float:
    """Perform basic arithmetic operations."""
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero"
    }
    return operations.get(operation, "Unknown operation")
```

### 3.6.2 Agent Creation

```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub

# Get a prompt for the agent
prompt = hub.pull("hwchase17/openai-functions-agent")

# Create tools
tools = [search_database, calculator]

# Create agent
agent = create_openai_functions_agent(
    llm=ChatOpenAI(model="gpt-4"),
    tools=tools,
    prompt=prompt
)

# Create executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)

# Run agent
result = agent_executor.invoke({"input": "What is 25 * 4?"})
```

## 3.7 RAG (Retrieval Augmented Generation)

### 3.7.1 Complete RAG Pipeline

```python
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. Load documents
loader = WebBaseLoader("https://example.com/docs")
documents = loader.load()

# 2. Split documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
splits = text_splitter.split_documents(documents)

# 3. Create embeddings and vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

# 4. Create retriever
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

# 5. Create RAG chain
rag_prompt = ChatPromptTemplate.from_template("""
Answer the question based only on the following context:
{context}

Question: {question}
""")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | ChatOpenAI(model="gpt-4")
    | StrOutputParser()
)

# 6. Query
answer = rag_chain.invoke("What is the main topic?")
```

---

## 4. LangGraph Deep Dive

## 4.1 Installation

```bash
pip install langgraph langgraph-checkpoint-sqlite
```

## 4.2 Core Concepts

### 4.2.1 State Definition

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

# Basic state
class BasicState(TypedDict):
    input: str
    output: str

# State with message history
class MessageState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# Complex state
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    current_step: str
    context: dict
    error: str | None
    final_output: str | None
```

### 4.2.2 Graph Building

```python
from langgraph.graph import StateGraph, END, START

# Initialize graph
graph = StateGraph(AgentState)

# Define nodes (functions)
def process_input(state: AgentState) -> AgentState:
    """Process the initial input."""
    return {"current_step": "processing"}

def generate_response(state: AgentState) -> AgentState:
    """Generate AI response."""
    # Your LLM logic here
    return {"final_output": "Generated response"}

def handle_error(state: AgentState) -> AgentState:
    """Handle any errors."""
    return {"error": None, "current_step": "recovered"}

# Add nodes to graph
graph.add_node("process", process_input)
graph.add_node("generate", generate_response)
graph.add_node("error_handler", handle_error)

# Add edges
graph.add_edge(START, "process")
graph.add_edge("process", "generate")
graph.add_edge("generate", END)

# Compile graph
app = graph.compile()
```

### 4.2.3 Conditional Edges

```python
def should_continue(state: AgentState) -> str:
    """Determine next step based on state."""
    if state.get("error"):
        return "error_handler"
    elif state.get("needs_review"):
        return "review"
    else:
        return "generate"

# Add conditional edge
graph.add_conditional_edges(
    "process",
    should_continue,
    {
        "error_handler": "error_handler",
        "review": "review",
        "generate": "generate"
    }
)
```

## 4.3 Complete Multi-Agent System

```python
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.sqlite import SqliteSaver
import operator

# State definition
class MultiAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    current_agent: str
    task_complete: bool
    final_result: str

# Initialize LLM
llm = ChatOpenAI(model="gpt-4")

# Agent prompts
RESEARCHER_PROMPT = """You are a research specialist. Analyze the topic and provide detailed findings."""
WRITER_PROMPT = """You are a content writer. Create engaging content based on the research."""
REVIEWER_PROMPT = """You are a quality reviewer. Review and improve the content."""

# Agent functions
def researcher_agent(state: MultiAgentState) -> MultiAgentState:
    messages = state["messages"]
    research_prompt = RESEARCHER_PROMPT + f"\n\nTopic: {messages[-1].content}"
    response = llm.invoke([HumanMessage(content=research_prompt)])
    return {
        "messages": [AIMessage(content=f"[Researcher]: {response.content}")],
        "current_agent": "writer"
    }

def writer_agent(state: MultiAgentState) -> MultiAgentState:
    messages = state["messages"]
    context = "\n".join([m.content for m in messages])
    writer_prompt = WRITER_PROMPT + f"\n\nContext:\n{context}"
    response = llm.invoke([HumanMessage(content=writer_prompt)])
    return {
        "messages": [AIMessage(content=f"[Writer]: {response.content}")],
        "current_agent": "reviewer"
    }

def reviewer_agent(state: MultiAgentState) -> MultiAgentState:
    messages = state["messages"]
    context = "\n".join([m.content for m in messages])
    reviewer_prompt = REVIEWER_PROMPT + f"\n\nContent:\n{context}"
    response = llm.invoke([HumanMessage(content=reviewer_prompt)])
    return {
        "messages": [AIMessage(content=f"[Reviewer]: {response.content}")],
        "final_result": response.content,
        "task_complete": True
    }

# Router function
def route_agent(state: MultiAgentState) -> Literal["writer", "reviewer", "end"]:
    if state.get("task_complete"):
        return "end"
    return state.get("current_agent", "writer")

# Build graph
workflow = StateGraph(MultiAgentState)

# Add nodes
workflow.add_node("researcher", researcher_agent)
workflow.add_node("writer", writer_agent)
workflow.add_node("reviewer", reviewer_agent)

# Add edges
workflow.add_edge(START, "researcher")
workflow.add_conditional_edges(
    "researcher",
    route_agent,
    {"writer": "writer", "reviewer": "reviewer", "end": END}
)
workflow.add_conditional_edges(
    "writer",
    route_agent,
    {"reviewer": "reviewer", "end": END}
)
workflow.add_edge("reviewer", END)

# Add checkpointer for persistence
checkpointer = SqliteSaver.from_conn_string(":memory:")

# Compile
app = workflow.compile(checkpointer=checkpointer)

# Execute
config = {"configurable": {"thread_id": "task-1"}}
result = app.invoke(
    {"messages": [HumanMessage(content="Write about AI in healthcare")]},
    config
)
```

## 4.4 Human-in-the-Loop

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END, START

class HumanLoopState(TypedDict):
    input: str
    draft: str
    approved: bool
    final: str

def create_draft(state: HumanLoopState) -> HumanLoopState:
    return {"draft": f"Draft for: {state['input']}"}

def human_review(state: HumanLoopState) -> HumanLoopState:
    # This node will be interrupted for human input
    return state

def finalize(state: HumanLoopState) -> HumanLoopState:
    return {"final": f"Approved: {state['draft']}"}

def check_approval(state: HumanLoopState) -> str:
    if state.get("approved"):
        return "finalize"
    return "create_draft"  # Redo if not approved

# Build graph with interrupt
graph = StateGraph(HumanLoopState)
graph.add_node("create_draft", create_draft)
graph.add_node("human_review", human_review)
graph.add_node("finalize", finalize)

graph.add_edge(START, "create_draft")
graph.add_edge("create_draft", "human_review")
graph.add_conditional_edges("human_review", check_approval)
graph.add_edge("finalize", END)

# Compile with interrupt before human_review
memory = MemorySaver()
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)

# First run - will pause at human_review
config = {"configurable": {"thread_id": "review-1"}}
result = app.invoke({"input": "Create a report"}, config)

# Human provides feedback
app.update_state(config, {"approved": True})

# Resume execution
final_result = app.invoke(None, config)
```

---

## 5. Flowcharts & Diagrams

## 5.1 LangChain Request Flow

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                        LANGCHAIN REQUEST FLOW                            │
└──────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │  USER   │
    │ REQUEST │
    └────┬────┘
         │
         ▼
    ┌─────────────────────┐
    │   PROMPT TEMPLATE   │
    │  ─────────────────  │
    │  Format user input  │
    │  with context       │
    └──────────┬──────────┘
               │
         ┌─────┴─────┐
         │           │
         ▼           ▼
    ┌─────────┐  ┌─────────┐
    │ MEMORY  │  │RETRIEVER│
    │ LOOKUP  │  │ (RAG)   │
    └────┬────┘  └────┬────┘
         │            │
         └─────┬──────┘
               │
               ▼
    ┌─────────────────────┐
    │     LLM MODEL       │
    │  ─────────────────  │
    │  Process with AI    │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │   OUTPUT PARSER     │
    │  ─────────────────  │
    │  Structure response │
    └──────────┬──────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌─────────┐         ┌─────────┐
│  TOOLS  │         │ RETURN  │
│ NEEDED? │───No───►│ RESULT  │
└────┬────┘         └─────────┘
     │Yes
     ▼
┌─────────────────────┐
│    TOOL EXECUTOR    │
│  ─────────────────  │
│  Execute tools      │
│  Get results        │
└──────────┬──────────┘
           │
           │ ┌─────────────────┐
           └►│ LOOP BACK TO    │
             │ LLM FOR FINAL   │
             │ ANSWER          │
             └─────────────────┘
```

## 5.2 LangGraph State Machine Flow

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                      LANGGRAPH STATE MACHINE                             │
└──────────────────────────────────────────────────────────────────────────┘

                           ┌─────────────┐
                           │   START     │
                           └──────┬──────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │      INITIALIZE         │
                    │    ───────────────      │
                    │  Set up initial state   │
                    │  Load checkpointer      │
                    └────────────┬────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────┐
         │              NODE EXECUTION               │
         └────────────────────┬──────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
      ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
      │   NODE A    │ │   NODE B    │ │   NODE C    │
      │  ─────────  │ │  ─────────  │ │  ─────────  │
      │  Agent 1    │ │  Agent 2    │ │  Agent 3    │
      └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
             │               │               │
             │      ┌────────┴────────┐      │
             │      │                 │      │
             │      ▼                 ▼      │
             │ ┌─────────┐     ┌─────────┐   │
             │ │ EDGE A  │     │ EDGE B  │   │
             │ └────┬────┘     └────┬────┘   │
             │      │               │        │
             └──────┴───────┬───────┴────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ CONDITIONAL EDGE  │
                  │  ───────────────  │
                  │  Evaluate state   │
                  │  Determine path   │
                  └─────────┬─────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
      ┌───────────┐   ┌───────────┐   ┌───────────┐
      │  PATH A   │   │  PATH B   │   │  PATH C   │
      └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
            │               │               │
            └───────────────┴───────────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │    CHECKPOINT     │
                  │  ───────────────  │
                  │  Save state       │
                  │  Enable resume    │
                  └─────────┬─────────┘
                            │
               ┌────────────┴────────────┐
               │                         │
               ▼                         ▼
        ┌─────────────┐           ┌─────────────┐
        │  CONTINUE   │           │     END     │
        │  EXECUTION  │           │   ───────   │
        │  ─────────  │           │  Return     │
        │  Next node  │           │  final      │
        └──────┬──────┘           │  state      │
               │                  └─────────────┘
               │
               └──────► (Loop to NODE EXECUTION)
```

## 5.3 Multi-Agent Communication Flow

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT COMMUNICATION                             │
└──────────────────────────────────────────────────────────────────────────┘

           USER INPUT
               │
               ▼
    ┌─────────────────────┐
    │   SUPERVISOR AGENT  │◄───────────────────────────────┐
    │  ─────────────────  │                                │
    │  • Route requests   │                                │
    │  • Coordinate work  │                                │
    │  • Aggregate results│                                │
    └──────────┬──────────┘                                │
               │                                           │
     ┌─────────┼─────────┬─────────────┐                  │
     │         │         │             │                   │
     ▼         ▼         ▼             ▼                   │
┌─────────┐┌─────────┐┌─────────┐┌─────────┐              │
│RESEARCHER│ ANALYST │ │ WRITER  ││REVIEWER │              │
│ AGENT   ││ AGENT   ││ AGENT   ││ AGENT   │              │
│─────────││─────────││─────────││─────────│              │
│Search   ││Process  ││Create   ││Quality  │              │
│Gather   ││Analyze  ││Write    ││Check    │              │
│Data     ││Data     ││Content  ││Review   │              │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘              │
     │          │          │          │                    │
     │    ┌─────┴──────────┴──────────┘                   │
     │    │                                                │
     ▼    ▼                                                │
┌─────────────────────┐                                   │
│   SHARED MEMORY     │                                   │
│  ─────────────────  │                                   │
│  • Messages         │                                   │
│  • Context          │                                   │
│  • Intermediate     │                                   │
│    results          │                                   │
└──────────┬──────────┘                                   │
           │                                               │
           └───────────────────────────────────────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │   OUTPUT    │
                        │  ─────────  │
                        │ Final result│
                        │ to user     │
                        └─────────────┘
```

## 5.4 RAG Pipeline Visualization

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE                                     │
└──────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        INDEXING PHASE (Offline)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │  DOCUMENTS  │    │   LOADER    │    │  SPLITTER   │                 │
│  │  ─────────  │───►│  ─────────  │───►│  ─────────  │                 │
│  │  PDF, Web,  │    │  PDF, HTML  │    │  Chunk by   │                 │
│  │  TXT, etc   │    │  TXT parser │    │  size/token │                 │
│  └─────────────┘    └─────────────┘    └──────┬──────┘                 │
│                                               │                         │
│                                               ▼                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │VECTOR STORE │◄───│  EMBEDDING  │◄───│   CHUNKS    │                 │
│  │  ─────────  │    │  ─────────  │    │  ─────────  │                 │
│  │  ChromaDB,  │    │  OpenAI,    │    │  Text       │                 │
│  │  Pinecone   │    │  Cohere     │    │  segments   │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        RETRIEVAL PHASE (Online)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   QUERY     │───►│  EMBEDDING  │───►│  SIMILARITY │                 │
│  │  ─────────  │    │  ─────────  │    │   SEARCH    │                 │
│  │  User       │    │  Same model │    │  ─────────  │                 │
│  │  question   │    │  as index   │    │  k-nearest  │                 │
│  └─────────────┘    └─────────────┘    └──────┬──────┘                 │
│                                               │                         │
│                                               ▼                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   ANSWER    │◄───│     LLM     │◄───│  RETRIEVED  │                 │
│  │  ─────────  │    │  ─────────  │    │  DOCUMENTS  │                 │
│  │  Generated  │    │  Generate   │    │  ─────────  │                 │
│  │  response   │    │  with ctx   │    │  Top-k docs │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Practical Examples

## 6.1 Chatbot with Memory

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# Store for session histories
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Create chain
llm = ChatOpenAI(model="gpt-4")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Be concise and friendly."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm

# Wrap with history
with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# Use the chatbot
config = {"configurable": {"session_id": "user-123"}}

response1 = with_history.invoke({"input": "Hi, I'm Alice!"}, config)
print(response1.content)

response2 = with_history.invoke({"input": "What's my name?"}, config)
print(response2.content)  # Will remember "Alice"
```

## 6.2 Code Generation Agent

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import subprocess

@tool
def execute_python(code: str) -> str:
    """Execute Python code and return the output."""
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def read_file(filepath: str) -> str:
    """Read contents of a file."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def write_file(filepath: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error: {str(e)}"

# Create code agent
tools = [execute_python, read_file, write_file]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Python developer. 
    You can write, execute, and debug code.
    Always test your code before providing the final answer."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

llm = ChatOpenAI(model="gpt-4", temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Use the agent
result = executor.invoke({
    "input": "Write a function to calculate fibonacci numbers and test it"
})
```

## 6.3 Document QA System

```python
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class DocumentQA:
    def __init__(self, docs_directory: str):
        self.docs_directory = docs_directory
        self.vectorstore = None
        self.chain = None
        
    def load_documents(self):
        """Load and process documents."""
        loader = DirectoryLoader(
            self.docs_directory,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = splitter.split_documents(documents)
        
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=OpenAIEmbeddings(),
            persist_directory="./doc_qa_db"
        )
        
    def setup_chain(self):
        """Set up the QA chain."""
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 4}
        )
        
        prompt = ChatPromptTemplate.from_template("""
        Answer the question based on the context below. 
        If you cannot answer from the context, say "I don't have enough information."
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        self.chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | ChatOpenAI(model="gpt-4")
            | StrOutputParser()
        )
        
    def ask(self, question: str) -> str:
        """Ask a question about the documents."""
        if not self.chain:
            self.setup_chain()
        return self.chain.invoke(question)

# Usage
qa = DocumentQA("./documents")
qa.load_documents()
answer = qa.ask("What are the main findings in the report?")
```

---

## 7. Advanced Patterns

## 7.1 Supervisor Pattern (LangGraph)

```python
from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
import operator

class SupervisorState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    next_worker: str
    task_status: dict

# Worker agents
workers = ["researcher", "coder", "writer"]

def create_supervisor():
    """Create supervisor that routes to workers."""
    llm = ChatOpenAI(model="gpt-4")
    
    def supervisor(state: SupervisorState) -> SupervisorState:
        messages = state["messages"]
        
        prompt = f"""Given the conversation history, determine which worker should act next.
        Workers: {workers}
        Or respond 'FINISH' if task is complete.
        
        History: {messages}
        
        Next worker:"""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        next_worker = response.content.strip().lower()
        
        if next_worker == "finish":
            return {"next_worker": "end"}
        return {"next_worker": next_worker}
    
    return supervisor

def researcher_node(state: SupervisorState) -> SupervisorState:
    # Research logic
    return {"messages": [HumanMessage(content="[Researcher] Research completed")]}

def coder_node(state: SupervisorState) -> SupervisorState:
    # Coding logic
    return {"messages": [HumanMessage(content="[Coder] Code written")]}

def writer_node(state: SupervisorState) -> SupervisorState:
    # Writing logic
    return {"messages": [HumanMessage(content="[Writer] Content created")]}

# Build graph
graph = StateGraph(SupervisorState)
graph.add_node("supervisor", create_supervisor())
graph.add_node("researcher", researcher_node)
graph.add_node("coder", coder_node)
graph.add_node("writer", writer_node)

# Routing
def route_to_worker(state: SupervisorState) -> str:
    return state.get("next_worker", "end")

graph.add_edge(START, "supervisor")
graph.add_conditional_edges(
    "supervisor",
    route_to_worker,
    {
        "researcher": "researcher",
        "coder": "coder",
        "writer": "writer",
        "end": END
    }
)

# Workers return to supervisor
for worker in workers:
    graph.add_edge(worker, "supervisor")

app = graph.compile()
```

## 7.2 Tool Calling with Structured Output

```python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List

class SearchQuery(BaseModel):
    """Search query with filters."""
    query: str = Field(description="The search query")
    filters: List[str] = Field(description="Filter categories")
    max_results: int = Field(default=10, description="Maximum results")

class AnalysisResult(BaseModel):
    """Structured analysis result."""
    summary: str = Field(description="Brief summary")
    key_points: List[str] = Field(description="Key points")
    sentiment: str = Field(description="Overall sentiment")
    confidence: float = Field(description="Confidence score 0-1")

@tool(args_schema=SearchQuery)
def advanced_search(query: str, filters: List[str], max_results: int) -> str:
    """Perform advanced search with filters."""
    return f"Found {max_results} results for '{query}' with filters: {filters}"

# Structured output
llm = ChatOpenAI(model="gpt-4")
structured_llm = llm.with_structured_output(AnalysisResult)

result = structured_llm.invoke(
    "Analyze the sentiment of: 'This product exceeded my expectations!'"
)
print(result.summary)
print(result.key_points)
print(result.sentiment)
```

## 7.3 Parallel Execution

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")

# Define parallel tasks
def summarize(text: str) -> str:
    return llm.invoke(f"Summarize: {text}").content

def extract_keywords(text: str) -> str:
    return llm.invoke(f"Extract 5 keywords from: {text}").content

def analyze_sentiment(text: str) -> str:
    return llm.invoke(f"Analyze sentiment of: {text}").content

# Create parallel chain
parallel_analysis = RunnableParallel(
    summary=RunnableLambda(summarize),
    keywords=RunnableLambda(extract_keywords),
    sentiment=RunnableLambda(analyze_sentiment)
)

# Execute in parallel
text = "LangChain is an amazing framework for building AI applications..."
results = parallel_analysis.invoke(text)

print("Summary:", results["summary"])
print("Keywords:", results["keywords"])
print("Sentiment:", results["sentiment"])
```

---

## 8. Best Practices

## 8.1 Error Handling

```python
from langchain_core.runnables import RunnableConfig
from langchain.callbacks import get_openai_callback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustChain:
    def __init__(self, chain):
        self.chain = chain
        
    async def invoke_with_retry(
        self, 
        input_data: dict, 
        max_retries: int = 3,
        config: RunnableConfig = None
    ):
        """Invoke chain with retry logic and error handling."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                with get_openai_callback() as cb:
                    result = await self.chain.ainvoke(input_data, config)
                    logger.info(f"Tokens used: {cb.total_tokens}")
                    return result
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if "rate_limit" in str(e).lower():
                    import asyncio
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
        raise RuntimeError(f"All {max_retries} attempts failed. Last error: {last_error}")
```

## 8.2 Token Management

```python
from langchain.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI

def token_aware_invoke(chain, input_data, max_tokens=4000):
    """Invoke chain with token awareness."""
    with get_openai_callback() as cb:
        result = chain.invoke(input_data)
        
        if cb.total_tokens > max_tokens * 0.9:
            print(f"⚠️ Warning: Used {cb.total_tokens}/{max_tokens} tokens")
        
        return {
            "result": result,
            "tokens_used": cb.total_tokens,
            "cost": cb.total_cost
        }
```

## 8.3 Caching

```python
from langchain.cache import InMemoryCache, SQLiteCache
from langchain.globals import set_llm_cache

# In-memory cache (for development)
set_llm_cache(InMemoryCache())

# SQLite cache (persistent)
set_llm_cache(SQLiteCache(database_path=".langchain.db"))

# Now LLM calls are cached automatically
llm = ChatOpenAI(model="gpt-4")
response1 = llm.invoke("What is 2+2?")  # API call
response2 = llm.invoke("What is 2+2?")  # Cached (instant)
```

## 8.4 Streaming

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

async def stream_response(prompt: str):
    """Stream LLM response token by token."""
    llm = ChatOpenAI(model="gpt-4", streaming=True)
    
    async for chunk in llm.astream([HumanMessage(content=prompt)]):
        if chunk.content:
            print(chunk.content, end="", flush=True)
    print()  # Newline at end

# Usage
import asyncio
asyncio.run(stream_response("Tell me a story about AI"))
```

---

## 9. Troubleshooting Guide

## 9.1 Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `RateLimitError` | Too many API calls | Implement exponential backoff |
| `ContextLengthExceeded` | Token limit hit | Use text splitter, summarize |
| `InvalidAPIKey` | Wrong/expired key | Check environment variables |
| `OutputParsingError` | LLM output malformed | Use `handle_parsing_errors=True` |
| `TimeoutError` | Slow API response | Increase timeout, use retry |

## 9.2 Debug Mode

```python
import langchain
langchain.debug = True  # Enable verbose logging

# Or for specific chain
chain.invoke(input, config={"callbacks": [ConsoleCallbackHandler()]})
```

## 9.3 Memory Issues

```python
# Clear memory periodically
if len(memory.chat_memory.messages) > 20:
    memory.chat_memory.clear()

# Or use windowed memory
from langchain.memory import ConversationBufferWindowMemory
memory = ConversationBufferWindowMemory(k=10)  # Keep last 10 exchanges
```

---

## 10. API Reference

## 10.1 Core Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `ChatOpenAI` | `langchain_openai` | OpenAI chat models |
| `ChatGoogleGenerativeAI` | `langchain_google_genai` | Google Gemini |
| `PromptTemplate` | `langchain_core.prompts` | Basic prompt templates |
| `ChatPromptTemplate` | `langchain_core.prompts` | Chat-style prompts |
| `StrOutputParser` | `langchain_core.output_parsers` | String output parsing |
| `StateGraph` | `langgraph.graph` | LangGraph state machine |
| `MemorySaver` | `langgraph.checkpoint.memory` | In-memory persistence |

## 10.2 Common Imports

```python
# LangChain Core
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

# LangChain Models
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# LangChain Agents
from langchain.agents import create_openai_functions_agent, AgentExecutor

# LangChain Memory
from langchain.memory import ConversationBufferMemory

# LangGraph
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
```

---

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith (Tracing)](https://smith.langchain.com/)
- [LangChain Templates](https://github.com/langchain-ai/langchain/tree/master/templates)

---

> **📝 Note:** This documentation is designed for teaching and developer reference. Code examples are production-ready patterns that can be adapted for your specific use cases.

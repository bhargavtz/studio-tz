# 📋 LangChain & LangGraph Quick Reference Cheatsheet

> **Quick lookup for common patterns and syntax**

---

## 🔧 Installation

```bash
# Core packages
pip install langchain langchain-core langchain-community

# LLM Providers
pip install langchain-openai          # OpenAI
pip install langchain-google-genai    # Google Gemini
pip install langchain-anthropic       # Anthropic Claude

# LangGraph
pip install langgraph langgraph-checkpoint-sqlite

# Vector stores
pip install chromadb faiss-cpu pinecone-client

# Full installation
pip install langchain langchain-openai langchain-community langgraph chromadb
```

---

## 📦 Common Imports

```python
# ═══════════════════════════════════════════════════════════════
# LANGCHAIN CORE
# ═══════════════════════════════════════════════════════════════

# Prompts
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
    FewShotPromptTemplate
)

# Messages
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    BaseMessage
)

# Output Parsers
from langchain_core.output_parsers import (
    StrOutputParser,
    JsonOutputParser,
    PydanticOutputParser
)

# Runnables (LCEL)
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableParallel,
    RunnableLambda,
    RunnableConfig
)

# Tools
from langchain_core.tools import tool, StructuredTool

# ═══════════════════════════════════════════════════════════════
# LLM PROVIDERS
# ═══════════════════════════════════════════════════════════════

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

# ═══════════════════════════════════════════════════════════════
# LANGGRAPH
# ═══════════════════════════════════════════════════════════════

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver

# ═══════════════════════════════════════════════════════════════
# AGENTS & MEMORY
# ═══════════════════════════════════════════════════════════════

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory
)

# ═══════════════════════════════════════════════════════════════
# VECTOR STORES
# ═══════════════════════════════════════════════════════════════

from langchain_community.vectorstores import Chroma, FAISS, Pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    WebBaseLoader,
    PyPDFLoader,
    DirectoryLoader
)
```

---

## 🤖 LLM Quick Setup

```python
# OpenAI GPT-4
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.7,
    api_key="sk-..."
)

# Google Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    google_api_key="..."
)

# Anthropic Claude
llm = ChatAnthropic(
    model="claude-3-opus-20240229",
    temperature=0.7,
    anthropic_api_key="..."
)

# Invoke
response = llm.invoke("Hello!")
print(response.content)

# Stream
for chunk in llm.stream("Tell me a story"):
    print(chunk.content, end="")

# Async
response = await llm.ainvoke("Hello!")
```

---

## 📝 Prompt Templates

```python
# Simple template
template = PromptTemplate(
    template="Tell me about {topic}",
    input_variables=["topic"]
)

# Chat template
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}."),
    ("human", "{input}")
])

# With history
chat_with_history = ChatPromptTemplate.from_messages([
    ("system", "You are helpful."),
    MessagesPlaceholder("history"),
    ("human", "{input}")
])

# Invoke
prompt = chat_template.invoke({"role": "helpful assistant", "input": "Hi!"})
```

---

## ⛓️ LCEL Chains

```python
# Basic chain
chain = prompt | llm | StrOutputParser()

# Invoke
result = chain.invoke({"input": "Hello"})

# With passthrough
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Parallel chains
parallel = RunnableParallel(
    summary=summary_chain,
    analysis=analysis_chain
)

# Batch processing
results = chain.batch([{"input": "A"}, {"input": "B"}])

# Streaming
for chunk in chain.stream({"input": "Hello"}):
    print(chunk)
```

---

## 🛠️ Tools

```python
# Simple tool
@tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"

# Structured tool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    a: float = Field(description="First number")
    b: float = Field(description="Second number")
    op: str = Field(description="Operation")

@tool(args_schema=CalculatorInput)
def calculator(a: float, b: float, op: str) -> float:
    """Perform calculation."""
    ops = {"add": a + b, "sub": a - b, "mul": a * b, "div": a / b}
    return ops.get(op, 0)

# Use tools with agent
tools = [search, calculator]
```

---

## 🔄 LangGraph State

```python
from typing import TypedDict, Annotated
import operator

# Basic state
class State(TypedDict):
    input: str
    output: str

# State with message accumulation
class MessageState(TypedDict):
    messages: Annotated[list, operator.add]

# Complex state
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    current_step: str
    data: dict
    error: str | None
```

---

## 📊 LangGraph Patterns

### Linear Pipeline
```python
graph = StateGraph(State)
graph.add_node("step1", step1_fn)
graph.add_node("step2", step2_fn)
graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", END)
app = graph.compile()
```

### Conditional Branching
```python
def router(state) -> str:
    if state.get("error"):
        return "error_handler"
    return "process"

graph.add_conditional_edges(
    "classify",
    router,
    {"error_handler": "error_handler", "process": "process"}
)
```

### Cyclic (Retry)
```python
graph.add_edge("process", "validate")
graph.add_conditional_edges(
    "validate",
    lambda s: "end" if s["valid"] else "process",
    {"end": END, "process": "process"}
)
```

---

## 💾 Checkpointing

```python
# Memory (development)
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

# SQLite
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("./app.db")

# PostgreSQL
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://...")

# Compile with checkpointer
app = graph.compile(checkpointer=checkpointer)

# Run with thread ID
config = {"configurable": {"thread_id": "session-123"}}
result = app.invoke(state, config)

# Get state
current_state = app.get_state(config)

# Get history
history = list(app.get_state_history(config))
```

---

## 🔍 RAG Quick Setup

```python
# 1. Load documents
loader = WebBaseLoader("https://example.com")
docs = loader.load()

# 2. Split
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = splitter.split_documents(docs)

# 3. Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(splits, embeddings)

# 4. Create retriever
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# 5. RAG chain
def format_docs(docs):
    return "\n\n".join(d.page_content for d in docs)

rag_prompt = ChatPromptTemplate.from_template("""
Answer based on context:
{context}

Question: {question}
""")

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("What is...?")
```

---

## 🐛 Debugging

```python
# Enable debug mode
import langchain
langchain.debug = True

# Token tracking
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    result = chain.invoke({"input": "Hello"})
    print(f"Tokens: {cb.total_tokens}")
    print(f"Cost: ${cb.total_cost:.4f}")

# Caching
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache

set_llm_cache(SQLiteCache(database_path=".langchain.db"))
```

---

## 📐 Common Patterns

| Pattern | Use Case | Key Feature |
|---------|----------|-------------|
| **Chain** | Sequential processing | `a \| b \| c` |
| **Branch** | Conditional routing | `add_conditional_edges` |
| **Parallel** | Concurrent tasks | `RunnableParallel` |
| **Cycle** | Retry/refinement | Edge back to earlier node |
| **Human-in-Loop** | Approval workflows | `interrupt_before` |
| **Supervisor** | Multi-agent orchestration | Central router node |

---

## ⚡ Performance Tips

1. **Use caching** for repeated calls
2. **Batch processing** for multiple inputs
3. **Streaming** for real-time responses
4. **Async** for concurrent operations
5. **Token limits** - monitor and manage

---

## 🔗 Quick Links

- [LangChain Docs](https://python.langchain.com/docs/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangSmith](https://smith.langchain.com/)
- [LCEL Guide](https://python.langchain.com/docs/expression_language/)

---

*Quick Reference v2.0 | December 2024*

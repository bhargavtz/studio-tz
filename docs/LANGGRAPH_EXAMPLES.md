# 💻 LangGraph Real-World Examples

> **Part 3 of LangChain/LangGraph Documentation Series**  
> **Focus:** Complete, copy-paste ready code examples for real applications

---

## 📑 Table of Contents

- [💻 LangGraph Real-World Examples](#-langgraph-real-world-examples)
  - [📑 Table of Contents](#-table-of-contents)
  - [1. AI Code Review System](#1-ai-code-review-system)
    - [Implementation: Code Review System](#implementation-code-review-system)
  - [2. Customer Support Agent](#2-customer-support-agent)
    - [Implementation: Customer Support Agent](#implementation-customer-support-agent)
  - [3. Research Assistant](#3-research-assistant)
    - [Implementation: Research Assistant](#implementation-research-assistant)
  - [4. Content Generation Pipeline](#4-content-generation-pipeline)
    - [Implementation: Content Generation Pipeline](#implementation-content-generation-pipeline)
  - [5. Data Processing Workflow](#5-data-processing-workflow)
    - [Implementation: Data Processing Workflow](#implementation-data-processing-workflow)
  - [6. Interactive Tutorial System](#6-interactive-tutorial-system)
    - [Implementation: Interactive Tutorial System](#implementation-interactive-tutorial-system)

---

## 1. AI Code Review System

### Implementation: Code Review System

```python
"""
AI Code Review System using LangGraph
=====================================
A multi-agent system that reviews code for:
- Style and formatting
- Security vulnerabilities
- Performance issues
- Best practices
"""

from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.sqlite import SqliteSaver
import operator

# ============= STATE DEFINITION =============

class CodeReviewState(TypedDict):
    code: str
    language: str
    messages: Annotated[list[BaseMessage], operator.add]
    style_review: dict | None
    security_review: dict | None
    performance_review: dict | None
    final_report: str | None
    current_reviewer: str

# ============= AGENTS =============

class StyleReviewer:
    """Reviews code style and formatting."""
    
    PROMPT = """You are an expert code style reviewer.
    Analyze the following {language} code for:
    1. Naming conventions
    2. Code formatting
    3. Documentation/comments
    4. Code organization
    5. Readability
    
    Code:
    ```{language}
    {code}
    ```
    
    Provide structured feedback with severity levels (info, warning, error).
    Format as JSON with 'issues' array and 'score' (0-100).
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def review(self, state: CodeReviewState) -> CodeReviewState:
        prompt = self.PROMPT.format(
            language=state["language"],
            code=state["code"]
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "style_review": {
                "agent": "style_reviewer",
                "feedback": response.content
            },
            "messages": [AIMessage(content=f"[Style Review]\n{response.content}")],
            "current_reviewer": "security"
        }


class SecurityReviewer:
    """Reviews code for security vulnerabilities."""
    
    PROMPT = """You are a security expert reviewing code for vulnerabilities.
    Analyze the following {language} code for:
    1. SQL Injection vulnerabilities
    2. XSS vulnerabilities
    3. Authentication issues
    4. Data exposure risks
    5. Input validation problems
    6. Hardcoded secrets
    
    Code:
    ```{language}
    {code}
    ```
    
    Provide structured feedback with severity levels (low, medium, high, critical).
    Format as JSON with 'vulnerabilities' array and 'risk_score' (0-100).
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def review(self, state: CodeReviewState) -> CodeReviewState:
        prompt = self.PROMPT.format(
            language=state["language"],
            code=state["code"]
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "security_review": {
                "agent": "security_reviewer",
                "feedback": response.content
            },
            "messages": [AIMessage(content=f"[Security Review]\n{response.content}")],
            "current_reviewer": "performance"
        }


class PerformanceReviewer:
    """Reviews code for performance issues."""
    
    PROMPT = """You are a performance optimization expert.
    Analyze the following {language} code for:
    1. Time complexity issues
    2. Space complexity issues
    3. Unnecessary computations
    4. Memory leaks potential
    5. Inefficient algorithms
    6. Database query optimization
    
    Code:
    ```{language}
    {code}
    ```
    
    Provide structured feedback with impact levels (low, medium, high).
    Format as JSON with 'issues' array and 'performance_score' (0-100).
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def review(self, state: CodeReviewState) -> CodeReviewState:
        prompt = self.PROMPT.format(
            language=state["language"],
            code=state["code"]
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "performance_review": {
                "agent": "performance_reviewer",
                "feedback": response.content
            },
            "messages": [AIMessage(content=f"[Performance Review]\n{response.content}")],
            "current_reviewer": "final"
        }


class ReportGenerator:
    """Generates final comprehensive report."""
    
    PROMPT = """Based on the following code reviews, generate a comprehensive report.
    
    Style Review:
    {style_review}
    
    Security Review:
    {security_review}
    
    Performance Review:
    {performance_review}
    
    Create a markdown report with:
    1. Executive Summary
    2. Critical Issues (must fix)
    3. Warnings (should fix)
    4. Suggestions (nice to have)
    5. Overall Score (0-100)
    6. Recommendations for next steps
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate(self, state: CodeReviewState) -> CodeReviewState:
        prompt = self.PROMPT.format(
            style_review=state["style_review"]["feedback"],
            security_review=state["security_review"]["feedback"],
            performance_review=state["performance_review"]["feedback"]
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "final_report": response.content,
            "messages": [AIMessage(content=f"[Final Report]\n{response.content}")]
        }


# ============= GRAPH CONSTRUCTION =============

def create_code_review_graph(llm=None):
    """Create the code review workflow graph."""
    
    if llm is None:
        llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    # Initialize agents
    style_reviewer = StyleReviewer(llm)
    security_reviewer = SecurityReviewer(llm)
    performance_reviewer = PerformanceReviewer(llm)
    report_generator = ReportGenerator(llm)
    
    # Create graph
    graph = StateGraph(CodeReviewState)
    
    # Add nodes
    graph.add_node("style", style_reviewer.review)
    graph.add_node("security", security_reviewer.review)
    graph.add_node("performance", performance_reviewer.review)
    graph.add_node("report", report_generator.generate)
    
    # Add edges (linear pipeline)
    graph.add_edge(START, "style")
    graph.add_edge("style", "security")
    graph.add_edge("security", "performance")
    graph.add_edge("performance", "report")
    graph.add_edge("report", END)
    
    # Compile with checkpointing
    checkpointer = SqliteSaver.from_conn_string(":memory:")
    return graph.compile(checkpointer=checkpointer)


# ============= USAGE =============

def review_code(code: str, language: str = "python"):
    """Review code and return the report."""
    
    app = create_code_review_graph()
    
    config = {"configurable": {"thread_id": f"review-{hash(code)}"}}
    
    result = app.invoke({
        "code": code,
        "language": language,
        "messages": [],
        "style_review": None,
        "security_review": None,
        "performance_review": None,
        "final_report": None,
        "current_reviewer": "style"
    }, config)
    
    return result["final_report"]


# Example usage
if __name__ == "__main__":
    sample_code = '''
    def get_user(id):
        query = f"SELECT * FROM users WHERE id = {id}"
        result = db.execute(query)
        return result
    '''
    
    report = review_code(sample_code, "python")
    print(report)
```

---

## 2. Customer Support Agent

### Implementation: Customer Support Agent

```python
"""
Customer Support Agent using LangGraph
======================================
An intelligent support agent that:
- Understands customer queries
- Routes to appropriate specialists
- Escalates when needed
- Maintains conversation context
"""

from typing import TypedDict, Annotated, Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.sqlite import SqliteSaver
import operator
from enum import Enum

# ============= ENUMS =============

class Department(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    GENERAL = "general"
    SALES = "sales"
    ESCALATION = "escalation"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# ============= STATE =============

class SupportState(TypedDict):
    customer_id: str
    customer_name: str
    messages: Annotated[list, operator.add]
    department: Department
    priority: Priority
    issue_summary: str
    solution: str | None
    escalated: bool
    satisfaction_score: int | None
    context: dict

# ============= AGENTS =============

class IntentClassifier:
    """Classifies customer intent and routes appropriately."""
    
    PROMPT = """Analyze the customer message and classify:
    1. Department: billing, technical, general, sales
    2. Priority: low, medium, high, urgent
    3. Issue Summary: Brief description of the issue
    
    Customer Message: {message}
    
    Respond in JSON format:
    {{"department": "...", "priority": "...", "issue_summary": "..."}}
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def classify(self, state: SupportState) -> SupportState:
        last_message = state["messages"][-1].content
        prompt = self.PROMPT.format(message=last_message)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse response (simplified)
        import json
        try:
            result = json.loads(response.content)
            return {
                "department": Department(result.get("department", "general")),
                "priority": Priority(result.get("priority", "medium")),
                "issue_summary": result.get("issue_summary", "")
            }
        except:
            return {
                "department": Department.GENERAL,
                "priority": Priority.MEDIUM,
                "issue_summary": last_message[:100]
            }


class BillingSpecialist:
    """Handles billing-related queries."""
    
    SYSTEM_PROMPT = """You are a billing specialist. You can help with:
    - Invoice questions
    - Payment issues
    - Subscription changes
    - Refund requests
    
    Be professional, empathetic, and solution-oriented.
    If the issue is complex, recommend escalation.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def handle(self, state: SupportState) -> SupportState:
        messages = [SystemMessage(content=self.SYSTEM_PROMPT)]
        messages.extend(state["messages"])
        
        response = self.llm.invoke(messages)
        
        # Check if escalation needed
        needs_escalation = "escalate" in response.content.lower()
        
        return {
            "messages": [AIMessage(content=response.content)],
            "solution": response.content if not needs_escalation else None,
            "escalated": needs_escalation
        }


class TechnicalSpecialist:
    """Handles technical support queries."""
    
    SYSTEM_PROMPT = """You are a technical support specialist. You can help with:
    - Software issues
    - Integration problems
    - API questions
    - Bug reports
    
    Provide step-by-step solutions when possible.
    Ask clarifying questions if needed.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def handle(self, state: SupportState) -> SupportState:
        messages = [SystemMessage(content=self.SYSTEM_PROMPT)]
        messages.extend(state["messages"])
        
        response = self.llm.invoke(messages)
        needs_escalation = "escalate" in response.content.lower()
        
        return {
            "messages": [AIMessage(content=response.content)],
            "solution": response.content if not needs_escalation else None,
            "escalated": needs_escalation
        }


class GeneralSupport:
    """Handles general inquiries."""
    
    SYSTEM_PROMPT = """You are a friendly customer support agent.
    Help with general questions about products, services, and company.
    Be helpful and direct customers to appropriate resources.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def handle(self, state: SupportState) -> SupportState:
        messages = [SystemMessage(content=self.SYSTEM_PROMPT)]
        messages.extend(state["messages"])
        
        response = self.llm.invoke(messages)
        
        return {
            "messages": [AIMessage(content=response.content)],
            "solution": response.content
        }


class EscalationHandler:
    """Handles escalated issues."""
    
    def handle(self, state: SupportState) -> SupportState:
        escalation_message = f"""
        Your issue has been escalated to a senior specialist.
        
        **Ticket Summary:**
        - Issue: {state['issue_summary']}
        - Priority: {state['priority']}
        - Department: {state['department']}
        
        A specialist will contact you within 24 hours.
        Reference ID: ESC-{hash(state['customer_id'])%10000:04d}
        """
        
        return {
            "messages": [AIMessage(content=escalation_message)],
            "escalated": True
        }


class SatisfactionSurvey:
    """Collects customer satisfaction."""
    
    def prompt(self, state: SupportState) -> SupportState:
        if state.get("escalated"):
            return state
        
        survey_message = """
        Thank you for contacting us!
        
        How would you rate your experience today?
        1 ⭐ - Poor
        2 ⭐⭐ - Fair
        3 ⭐⭐⭐ - Good
        4 ⭐⭐⭐⭐ - Very Good
        5 ⭐⭐⭐⭐⭐ - Excellent
        
        Reply with 1-5 to rate.
        """
        
        return {
            "messages": [AIMessage(content=survey_message)]
        }


# ============= ROUTING =============

def route_to_department(state: SupportState) -> str:
    """Route to appropriate department."""
    if state.get("escalated"):
        return "escalation"
    
    department = state.get("department", Department.GENERAL)
    
    routing = {
        Department.BILLING: "billing",
        Department.TECHNICAL: "technical",
        Department.SALES: "general",  # Sales goes to general for now
        Department.GENERAL: "general",
        Department.ESCALATION: "escalation"
    }
    
    return routing.get(department, "general")


def should_escalate(state: SupportState) -> str:
    """Check if issue needs escalation."""
    if state.get("escalated"):
        return "escalation"
    if state.get("solution"):
        return "survey"
    return "escalation"


# ============= GRAPH =============

def create_support_graph(llm=None):
    """Create customer support workflow."""
    
    if llm is None:
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    
    # Initialize agents
    classifier = IntentClassifier(llm)
    billing = BillingSpecialist(llm)
    technical = TechnicalSpecialist(llm)
    general = GeneralSupport(llm)
    escalation = EscalationHandler()
    survey = SatisfactionSurvey()
    
    # Create graph
    graph = StateGraph(SupportState)
    
    # Add nodes
    graph.add_node("classify", classifier.classify)
    graph.add_node("billing", billing.handle)
    graph.add_node("technical", technical.handle)
    graph.add_node("general", general.handle)
    graph.add_node("escalation", escalation.handle)
    graph.add_node("survey", survey.prompt)
    
    # Add edges
    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        route_to_department,
        {
            "billing": "billing",
            "technical": "technical",
            "general": "general",
            "escalation": "escalation"
        }
    )
    
    # Each specialist can escalate or complete
    for specialist in ["billing", "technical", "general"]:
        graph.add_conditional_edges(
            specialist,
            should_escalate,
            {
                "escalation": "escalation",
                "survey": "survey"
            }
        )
    
    graph.add_edge("escalation", END)
    graph.add_edge("survey", END)
    
    # Compile
    checkpointer = SqliteSaver.from_conn_string(":memory:")
    return graph.compile(checkpointer=checkpointer)


# ============= USAGE =============

class SupportSession:
    """Manage a support conversation session."""
    
    def __init__(self, customer_id: str, customer_name: str):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.app = create_support_graph()
        self.config = {"configurable": {"thread_id": f"support-{customer_id}"}}
        self.initialized = False
    
    def send_message(self, message: str) -> str:
        """Send a message and get response."""
        
        if not self.initialized:
            state = {
                "customer_id": self.customer_id,
                "customer_name": self.customer_name,
                "messages": [HumanMessage(content=message)],
                "department": Department.GENERAL,
                "priority": Priority.MEDIUM,
                "issue_summary": "",
                "solution": None,
                "escalated": False,
                "satisfaction_score": None,
                "context": {}
            }
            self.initialized = True
        else:
            # Continue conversation
            current_state = self.app.get_state(self.config)
            state = {"messages": [HumanMessage(content=message)]}
        
        result = self.app.invoke(state, self.config)
        
        # Get last AI message
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        return ai_messages[-1].content if ai_messages else "Processing..."


# Example usage
if __name__ == "__main__":
    session = SupportSession("CUST001", "John Doe")
    
    # User sends message
    response = session.send_message("I was charged twice for my subscription!")
    print(f"Agent: {response}")
```

---

## 3. Research Assistant

### Implementation: Research Assistant

```python
"""
Research Assistant using LangGraph
==================================
A multi-step research agent that:
- Searches multiple sources
- Synthesizes information
- Generates reports
- Provides citations
"""

from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END, START
import operator

# ============= STATE =============

class ResearchState(TypedDict):
    topic: str
    search_queries: List[str]
    search_results: Annotated[list, operator.add]
    analysis: str | None
    outline: List[str]
    report: str | None
    citations: List[dict]
    quality_score: float

# ============= AGENTS =============

class QueryGenerator:
    """Generates diverse search queries for the topic."""
    
    PROMPT = """Generate 5 diverse search queries to research the topic: "{topic}"
    
    Include queries for:
    1. Overview/definition
    2. Recent developments
    3. Key players/examples
    4. Challenges/controversies
    5. Future trends
    
    Return as a JSON array of strings.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate(self, state: ResearchState) -> ResearchState:
        prompt = self.PROMPT.format(topic=state["topic"])
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        import json
        try:
            queries = json.loads(response.content)
        except:
            queries = [
                f"{state['topic']} overview",
                f"{state['topic']} recent news",
                f"{state['topic']} examples",
                f"{state['topic']} challenges",
                f"{state['topic']} future"
            ]
        
        return {"search_queries": queries}


class WebSearcher:
    """Performs web searches."""
    
    def __init__(self, search_tool=None):
        self.search_tool = search_tool or TavilySearchResults(max_results=3)
    
    def search(self, state: ResearchState) -> ResearchState:
        all_results = []
        
        for query in state["search_queries"]:
            try:
                results = self.search_tool.invoke({"query": query})
                for r in results:
                    all_results.append({
                        "query": query,
                        "title": r.get("title", ""),
                        "content": r.get("content", ""),
                        "url": r.get("url", "")
                    })
            except Exception as e:
                print(f"Search error for '{query}': {e}")
        
        return {"search_results": all_results}


class Analyzer:
    """Analyzes and synthesizes search results."""
    
    PROMPT = """Analyze these search results about "{topic}":

{results}

Provide:
1. Key themes and patterns
2. Important facts and statistics
3. Different perspectives
4. Knowledge gaps
5. Reliability assessment

Be thorough and objective.
"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def analyze(self, state: ResearchState) -> ResearchState:
        results_text = "\n\n".join([
            f"Source: {r['title']}\n{r['content']}\nURL: {r['url']}"
            for r in state["search_results"][:10]  # Limit to 10
        ])
        
        prompt = self.PROMPT.format(
            topic=state["topic"],
            results=results_text
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"analysis": response.content}


class OutlineCreator:
    """Creates a structured outline for the report."""
    
    PROMPT = """Based on this analysis of "{topic}":

{analysis}

Create a detailed outline for a comprehensive research report.
Include:
1. Executive Summary
2. Introduction
3. Main sections (3-5)
4. Conclusions
5. Recommendations

Return as a JSON array of section titles.
"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def create(self, state: ResearchState) -> ResearchState:
        prompt = self.PROMPT.format(
            topic=state["topic"],
            analysis=state["analysis"]
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        import json
        try:
            outline = json.loads(response.content)
        except:
            outline = [
                "Executive Summary",
                "Introduction",
                "Current State",
                "Challenges",
                "Opportunities",
                "Conclusions",
                "Recommendations"
            ]
        
        return {"outline": outline}


class ReportWriter:
    """Writes the final research report."""
    
    PROMPT = """Write a comprehensive research report about "{topic}".

Use this outline:
{outline}

Based on this analysis:
{analysis}

Requirements:
- Professional academic tone
- Well-structured sections
- Include relevant data and examples
- Add in-text citations where appropriate
- Markdown formatting
- 1500-2000 words
"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def write(self, state: ResearchState) -> ResearchState:
        outline_text = "\n".join([f"- {section}" for section in state["outline"]])
        
        prompt = self.PROMPT.format(
            topic=state["topic"],
            outline=outline_text,
            analysis=state["analysis"]
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Extract citations from search results
        citations = [
            {
                "title": r["title"],
                "url": r["url"]
            }
            for r in state["search_results"][:10]
        ]
        
        return {
            "report": response.content,
            "citations": citations
        }


class QualityChecker:
    """Evaluates report quality."""
    
    PROMPT = """Evaluate this research report:

{report}

Score (0-100) based on:
1. Comprehensiveness (20 points)
2. Accuracy (20 points)
3. Structure (20 points)
4. Clarity (20 points)
5. Citations (20 points)

Return JSON: {{"score": X, "feedback": "..."}}
"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def check(self, state: ResearchState) -> ResearchState:
        prompt = self.PROMPT.format(report=state["report"][:3000])
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        import json
        try:
            result = json.loads(response.content)
            score = result.get("score", 75) / 100
        except:
            score = 0.75
        
        return {"quality_score": score}


# ============= GRAPH =============

def create_research_graph(llm=None):
    """Create research assistant workflow."""
    
    if llm is None:
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
    
    # Initialize agents
    query_gen = QueryGenerator(llm)
    searcher = WebSearcher()
    analyzer = Analyzer(llm)
    outliner = OutlineCreator(llm)
    writer = ReportWriter(llm)
    checker = QualityChecker(llm)
    
    # Create graph
    graph = StateGraph(ResearchState)
    
    # Add nodes
    graph.add_node("generate_queries", query_gen.generate)
    graph.add_node("search", searcher.search)
    graph.add_node("analyze", analyzer.analyze)
    graph.add_node("outline", outliner.create)
    graph.add_node("write", writer.write)
    graph.add_node("quality_check", checker.check)
    
    # Add edges
    graph.add_edge(START, "generate_queries")
    graph.add_edge("generate_queries", "search")
    graph.add_edge("search", "analyze")
    graph.add_edge("analyze", "outline")
    graph.add_edge("outline", "write")
    graph.add_edge("write", "quality_check")
    graph.add_edge("quality_check", END)
    
    return graph.compile()


# ============= USAGE =============

def research_topic(topic: str) -> dict:
    """Research a topic and return the report."""
    
    app = create_research_graph()
    
    result = app.invoke({
        "topic": topic,
        "search_queries": [],
        "search_results": [],
        "analysis": None,
        "outline": [],
        "report": None,
        "citations": [],
        "quality_score": 0.0
    })
    
    return {
        "report": result["report"],
        "citations": result["citations"],
        "quality_score": result["quality_score"]
    }


if __name__ == "__main__":
    result = research_topic("Quantum Computing in 2024")
    print(result["report"])
    print(f"\nQuality Score: {result['quality_score']*100:.0f}%")
```

---

## 4. Content Generation Pipeline

### Implementation: Content Generation Pipeline

```python
"""
Content Generation Pipeline using LangGraph
============================================
Generates high-quality content through:
- Ideation
- Drafting
- Editing
- SEO optimization
"""

from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
import operator

# ============= STATE =============

class ContentState(TypedDict):
    topic: str
    content_type: str  # blog, article, social
    target_audience: str
    keywords: List[str]
    ideas: List[dict]
    selected_idea: dict | None
    outline: List[str]
    draft: str | None
    edited_draft: str | None
    seo_optimized: str | None
    final_content: str | None
    metadata: dict

# ============= AGENTS =============

class IdeationAgent:
    """Generates content ideas."""
    
    PROMPT = """Generate 5 unique content ideas for:
    Topic: {topic}
    Content Type: {content_type}
    Target Audience: {target_audience}
    
    For each idea provide:
    - Title
    - Hook/angle
    - Key points to cover
    - Estimated engagement potential (1-10)
    
    Return as JSON array.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate(self, state: ContentState) -> ContentState:
        prompt = self.PROMPT.format(
            topic=state["topic"],
            content_type=state["content_type"],
            target_audience=state["target_audience"]
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        import json
        try:
            ideas = json.loads(response.content)
        except:
            ideas = [{"title": state["topic"], "hook": "Main perspective", "points": [], "engagement": 5}]
        
        # Select best idea
        best_idea = max(ideas, key=lambda x: x.get("engagement", 0))
        
        return {
            "ideas": ideas,
            "selected_idea": best_idea
        }


class OutlineAgent:
    """Creates detailed content outline."""
    
    PROMPT = """Create a detailed outline for this content:
    
    Title: {title}
    Angle: {hook}
    Type: {content_type}
    Keywords to include: {keywords}
    
    Create a comprehensive outline with:
    - Compelling introduction hook
    - 3-5 main sections with subsections
    - Key points for each section
    - Conclusion with CTA
    
    Return as JSON array of section objects.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def create(self, state: ContentState) -> ContentState:
        idea = state["selected_idea"]
        
        prompt = self.PROMPT.format(
            title=idea.get("title", state["topic"]),
            hook=idea.get("hook", ""),
            content_type=state["content_type"],
            keywords=", ".join(state.get("keywords", []))
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        import json
        try:
            outline = json.loads(response.content)
            if isinstance(outline, list):
                outline = [item if isinstance(item, str) else item.get("title", str(item)) for item in outline]
        except:
            outline = ["Introduction", "Main Content", "Conclusion"]
        
        return {"outline": outline}


class DraftAgent:
    """Writes the initial draft."""
    
    PROMPT = """Write a {content_type} about "{title}".
    
    Follow this outline:
    {outline}
    
    Requirements:
    - Engaging and readable style
    - Target audience: {audience}
    - Include keywords naturally: {keywords}
    - Use subheadings for structure
    - {word_count} words approximately
    - Markdown formatting
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def write(self, state: ContentState) -> ContentState:
        word_counts = {
            "blog": "1000-1500",
            "article": "1500-2000",
            "social": "200-300"
        }
        
        outline_text = "\n".join([f"- {section}" for section in state["outline"]])
        
        prompt = self.PROMPT.format(
            content_type=state["content_type"],
            title=state["selected_idea"].get("title", state["topic"]),
            outline=outline_text,
            audience=state["target_audience"],
            keywords=", ".join(state.get("keywords", [])),
            word_count=word_counts.get(state["content_type"], "1000-1500")
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"draft": response.content}


class EditorAgent:
    """Edits and improves the draft."""
    
    PROMPT = """Edit this {content_type} for quality:

{draft}

Improve:
1. Clarity and readability
2. Grammar and spelling
3. Flow and transitions
4. Engagement and hooks
5. Factual accuracy

Keep the same overall structure. Return the improved version.
"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def edit(self, state: ContentState) -> ContentState:
        prompt = self.PROMPT.format(
            content_type=state["content_type"],
            draft=state["draft"]
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return {"edited_draft": response.content}


class SEOAgent:
    """Optimizes content for SEO."""
    
    PROMPT = """Optimize this content for SEO:

{content}

Keywords to target: {keywords}

Optimize:
1. Title and headings (include keywords naturally)
2. Meta description (generate one)
3. Internal linking suggestions
4. Image alt text suggestions
5. URL slug suggestion

Return the optimized content with a YAML front matter containing metadata.
"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def optimize(self, state: ContentState) -> ContentState:
        prompt = self.PROMPT.format(
            content=state["edited_draft"],
            keywords=", ".join(state.get("keywords", []))
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Extract metadata
        metadata = {
            "title": state["selected_idea"].get("title", state["topic"]),
            "keywords": state.get("keywords", []),
            "content_type": state["content_type"],
            "target_audience": state["target_audience"]
        }
        
        return {
            "seo_optimized": response.content,
            "final_content": response.content,
            "metadata": metadata
        }


# ============= GRAPH =============

def create_content_pipeline(llm=None):
    """Create content generation workflow."""
    
    if llm is None:
        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    # Initialize agents
    ideation = IdeationAgent(llm)
    outliner = OutlineAgent(llm)
    drafter = DraftAgent(llm)
    editor = EditorAgent(llm)
    seo = SEOAgent(llm)
    
    # Create graph
    graph = StateGraph(ContentState)
    
    # Add nodes
    graph.add_node("ideate", ideation.generate)
    graph.add_node("outline", outliner.create)
    graph.add_node("draft", drafter.write)
    graph.add_node("edit", editor.edit)
    graph.add_node("seo", seo.optimize)
    
    # Linear pipeline
    graph.add_edge(START, "ideate")
    graph.add_edge("ideate", "outline")
    graph.add_edge("outline", "draft")
    graph.add_edge("draft", "edit")
    graph.add_edge("edit", "seo")
    graph.add_edge("seo", END)
    
    return graph.compile()


# ============= USAGE =============

def generate_content(
    topic: str,
    content_type: str = "blog",
    target_audience: str = "general",
    keywords: List[str] = None
) -> dict:
    """Generate content for a topic."""
    
    app = create_content_pipeline()
    
    result = app.invoke({
        "topic": topic,
        "content_type": content_type,
        "target_audience": target_audience,
        "keywords": keywords or [],
        "ideas": [],
        "selected_idea": None,
        "outline": [],
        "draft": None,
        "edited_draft": None,
        "seo_optimized": None,
        "final_content": None,
        "metadata": {}
    })
    
    return {
        "content": result["final_content"],
        "metadata": result["metadata"],
        "all_ideas": result["ideas"]
    }


if __name__ == "__main__":
    result = generate_content(
        topic="Getting Started with LangGraph",
        content_type="blog",
        target_audience="developers",
        keywords=["langgraph", "langchain", "AI agents"]
    )
    
    print(result["content"])
```

---

## 5. Data Processing Workflow

### Implementation: Data Processing Workflow

```python
"""
Data Processing Workflow using LangGraph
========================================
ETL pipeline with AI-powered transformations:
- Data extraction
- Validation
- Transformation
- Loading
"""

from typing import TypedDict, Annotated, List, Any
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
import operator
import json

# ============= STATE =============

class DataState(TypedDict):
    source: str
    raw_data: Any
    schema: dict | None
    validated_data: Any
    validation_errors: List[str]
    transformed_data: Any
    transformation_log: Annotated[list, operator.add]
    destination: str
    load_status: str

# ============= PROCESSORS =============

class DataExtractor:
    """Extracts data from various sources."""
    
    def __init__(self, llm):
        self.llm = llm
    
    def extract(self, state: DataState) -> DataState:
        source = state["source"]
        
        # Simulate extraction based on source type
        if source.endswith(".json"):
            # JSON file
            sample_data = [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example"},  # Invalid email
                {"id": 3, "name": "", "email": "charlie@example.com"},  # Empty name
            ]
        elif source.endswith(".csv"):
            sample_data = [
                {"id": "1", "name": "Alice", "email": "alice@example.com"},
                {"id": "2", "name": "Bob", "email": "bob@example.com"},
            ]
        else:
            sample_data = []
        
        # Infer schema using LLM
        schema_prompt = f"""Analyze this data and infer the schema:
        {json.dumps(sample_data[:3], indent=2)}
        
        Return JSON schema with field names, types, and validation rules.
        """
        
        response = self.llm.invoke([HumanMessage(content=schema_prompt)])
        
        try:
            schema = json.loads(response.content)
        except:
            schema = {"fields": ["id", "name", "email"]}
        
        return {
            "raw_data": sample_data,
            "schema": schema,
            "transformation_log": ["Extracted data from source"]
        }


class DataValidator:
    """Validates data against schema."""
    
    def __init__(self, llm):
        self.llm = llm
    
    def validate(self, state: DataState) -> DataState:
        data = state["raw_data"]
        errors = []
        valid_records = []
        
        for i, record in enumerate(data):
            record_errors = []
            
            # Basic validation
            if not record.get("name"):
                record_errors.append(f"Record {i}: Empty name")
            
            email = record.get("email", "")
            if "@" not in email or "." not in email.split("@")[-1]:
                record_errors.append(f"Record {i}: Invalid email '{email}'")
            
            if record_errors:
                errors.extend(record_errors)
            else:
                valid_records.append(record)
        
        return {
            "validated_data": valid_records,
            "validation_errors": errors,
            "transformation_log": [f"Validated {len(valid_records)}/{len(data)} records"]
        }


class DataTransformer:
    """Transforms data with AI assistance."""
    
    PROMPT = """Transform this data according to these rules:
    1. Standardize email to lowercase
    2. Capitalize names properly
    3. Add a 'processed_at' timestamp field
    4. Generate a 'display_name' from name and email
    
    Data: {data}
    
    Return transformed data as JSON array.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def transform(self, state: DataState) -> DataState:
        data = state["validated_data"]
        
        if not data:
            return {
                "transformed_data": [],
                "transformation_log": ["No data to transform"]
            }
        
        # Use LLM for complex transformations
        prompt = self.PROMPT.format(data=json.dumps(data, indent=2))
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        try:
            transformed = json.loads(response.content)
        except:
            # Fallback to simple transformation
            from datetime import datetime
            transformed = []
            for record in data:
                new_record = record.copy()
                new_record["email"] = record.get("email", "").lower()
                new_record["name"] = record.get("name", "").title()
                new_record["processed_at"] = datetime.now().isoformat()
                new_record["display_name"] = f"{new_record['name']} <{new_record['email']}>"
                transformed.append(new_record)
        
        return {
            "transformed_data": transformed,
            "transformation_log": [f"Transformed {len(transformed)} records"]
        }


class DataLoader:
    """Loads data to destination."""
    
    def load(self, state: DataState) -> DataState:
        data = state["transformed_data"]
        destination = state["destination"]
        
        # Simulate loading
        if destination.startswith("db://"):
            status = f"Loaded {len(data)} records to database"
        elif destination.endswith(".json"):
            status = f"Saved {len(data)} records to JSON file"
        else:
            status = f"Loaded {len(data)} records to {destination}"
        
        return {
            "load_status": status,
            "transformation_log": [status]
        }


# ============= ROUTING =============

def check_validation(state: DataState) -> str:
    """Check if data passed validation."""
    if not state.get("validated_data"):
        return "fail"
    if len(state.get("validation_errors", [])) > len(state.get("validated_data", [])):
        return "fail"
    return "continue"


def handle_failure(state: DataState) -> DataState:
    """Handle validation failure."""
    return {
        "load_status": f"Failed: {len(state.get('validation_errors', []))} validation errors",
        "transformation_log": ["Pipeline failed due to validation errors"]
    }


# ============= GRAPH =============

def create_etl_pipeline(llm=None):
    """Create ETL pipeline."""
    
    if llm is None:
        llm = ChatOpenAI(model="gpt-4", temperature=0)
    
    extractor = DataExtractor(llm)
    validator = DataValidator(llm)
    transformer = DataTransformer(llm)
    loader = DataLoader()
    
    graph = StateGraph(DataState)
    
    graph.add_node("extract", extractor.extract)
    graph.add_node("validate", validator.validate)
    graph.add_node("transform", transformer.transform)
    graph.add_node("load", loader.load)
    graph.add_node("fail", handle_failure)
    
    graph.add_edge(START, "extract")
    graph.add_edge("extract", "validate")
    graph.add_conditional_edges(
        "validate",
        check_validation,
        {"continue": "transform", "fail": "fail"}
    )
    graph.add_edge("transform", "load")
    graph.add_edge("load", END)
    graph.add_edge("fail", END)
    
    return graph.compile()


# ============= USAGE =============

def process_data(source: str, destination: str) -> dict:
    """Run ETL pipeline."""
    
    app = create_etl_pipeline()
    
    result = app.invoke({
        "source": source,
        "destination": destination,
        "raw_data": None,
        "schema": None,
        "validated_data": None,
        "validation_errors": [],
        "transformed_data": None,
        "transformation_log": [],
        "load_status": ""
    })
    
    return {
        "status": result["load_status"],
        "records_processed": len(result.get("transformed_data", [])),
        "errors": result.get("validation_errors", []),
        "log": result["transformation_log"]
    }


if __name__ == "__main__":
    result = process_data("data.json", "db://production")
    print(f"Status: {result['status']}")
    print(f"Records: {result['records_processed']}")
    print(f"Errors: {result['errors']}")
```

---

## 6. Interactive Tutorial System

### Implementation: Interactive Tutorial System

```python
"""
Interactive Tutorial System using LangGraph
============================================
Adaptive learning system that:
- Assesses skill level
- Presents personalized content
- Tracks progress
- Provides feedback
"""

from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
import operator

# ============= STATE =============

class TutorialState(TypedDict):
    user_id: str
    topic: str
    skill_level: str  # beginner, intermediate, advanced
    messages: Annotated[list, operator.add]
    current_lesson: int
    lessons: List[dict]
    quiz_results: List[dict]
    progress: float
    completed: bool

# ============= COMPONENTS =============

class SkillAssessor:
    """Assesses user's current skill level."""
    
    QUESTIONS = {
        "python": [
            "What is a variable in Python?",
            "Explain list comprehensions.",
            "What are decorators?"
        ]
    }
    
    def __init__(self, llm):
        self.llm = llm
    
    def assess(self, state: TutorialState) -> TutorialState:
        # In real implementation, would analyze user responses
        # For now, simulate assessment
        
        assessment_prompt = f"""
        Based on the user's topic interest: {state['topic']}
        
        Generate 3 assessment questions for different levels:
        1. Beginner level
        2. Intermediate level  
        3. Advanced level
        
        Format as JSON array with 'question' and 'level' fields.
        """
        
        response = self.llm.invoke([HumanMessage(content=assessment_prompt)])
        
        # For demo, default to beginner
        return {
            "skill_level": "beginner",
            "messages": [AIMessage(content=f"Welcome! I've assessed your level as beginner for {state['topic']}. Let's start learning!")]
        }


class CurriculumGenerator:
    """Generates personalized curriculum."""
    
    PROMPT = """Create a learning curriculum for:
    Topic: {topic}
    Skill Level: {skill_level}
    
    Generate 5 lessons with:
    - Lesson title
    - Learning objectives (3 each)
    - Key concepts to cover
    - Estimated duration
    
    Return as JSON array.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate(self, state: TutorialState) -> TutorialState:
        prompt = self.PROMPT.format(
            topic=state["topic"],
            skill_level=state["skill_level"]
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        import json
        try:
            lessons = json.loads(response.content)
        except:
            lessons = [
                {"title": f"{state['topic']} Basics", "objectives": ["Understand fundamentals"], "duration": "30 min"},
                {"title": f"{state['topic']} Practice", "objectives": ["Apply concepts"], "duration": "45 min"},
                {"title": f"{state['topic']} Advanced", "objectives": ["Master techniques"], "duration": "60 min"},
            ]
        
        return {
            "lessons": lessons,
            "current_lesson": 0,
            "messages": [AIMessage(content=f"I've created a personalized curriculum with {len(lessons)} lessons!")]
        }


class LessonPresenter:
    """Presents lesson content."""
    
    PROMPT = """Create an engaging lesson about:
    Topic: {topic}
    Lesson Title: {lesson_title}
    Objectives: {objectives}
    Skill Level: {skill_level}
    
    Include:
    1. Introduction with hook
    2. Core concepts explained simply
    3. Examples and analogies
    4. Practice exercises
    5. Summary
    
    Format with Markdown, be engaging and educational.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def present(self, state: TutorialState) -> TutorialState:
        current = state["current_lesson"]
        lesson = state["lessons"][current]
        
        prompt = self.PROMPT.format(
            topic=state["topic"],
            lesson_title=lesson.get("title", f"Lesson {current + 1}"),
            objectives=lesson.get("objectives", []),
            skill_level=state["skill_level"]
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "messages": [AIMessage(content=response.content)]
        }


class QuizGenerator:
    """Generates quizzes for lessons."""
    
    PROMPT = """Create a quiz for:
    Topic: {topic}
    Lesson: {lesson_title}
    Skill Level: {skill_level}
    
    Generate 3 multiple choice questions.
    Return as JSON with 'question', 'options' (array), and 'correct_index'.
    """
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate(self, state: TutorialState) -> TutorialState:
        current = state["current_lesson"]
        lesson = state["lessons"][current]
        
        prompt = self.PROMPT.format(
            topic=state["topic"],
            lesson_title=lesson.get("title", ""),
            skill_level=state["skill_level"]
        )
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Format quiz for display
        quiz_message = f"""
        📝 **Quiz Time!**
        
        Let's check your understanding of {lesson.get('title', 'this lesson')}.
        
        {response.content}
        
        Reply with your answers (e.g., "1-A, 2-B, 3-C")
        """
        
        return {
            "messages": [AIMessage(content=quiz_message)]
        }


class ProgressTracker:
    """Tracks and updates progress."""
    
    def update(self, state: TutorialState) -> TutorialState:
        current = state["current_lesson"]
        total = len(state["lessons"])
        
        new_lesson = current + 1
        progress = (new_lesson / total) * 100
        completed = new_lesson >= total
        
        if completed:
            message = f"""
            🎉 **Congratulations!**
            
            You've completed all {total} lessons on {state['topic']}!
            
            Your progress: {progress:.0f}%
            
            Would you like to:
            1. Review any lessons
            2. Take a comprehensive test
            3. Move to advanced topics
            """
        else:
            message = f"""
            ✅ **Lesson Complete!**
            
            Progress: {progress:.0f}% ({new_lesson}/{total} lessons)
            
            Ready for the next lesson?
            """
        
        return {
            "current_lesson": new_lesson,
            "progress": progress,
            "completed": completed,
            "messages": [AIMessage(content=message)]
        }


# ============= ROUTING =============

def should_continue(state: TutorialState) -> str:
    """Check if tutorial should continue."""
    if state.get("completed"):
        return "end"
    return "next_lesson"


# ============= GRAPH =============

def create_tutorial_system(llm=None):
    """Create tutorial system workflow."""
    
    if llm is None:
        llm = ChatOpenAI(model="gpt-4", temperature=0.7)
    
    assessor = SkillAssessor(llm)
    curriculum = CurriculumGenerator(llm)
    presenter = LessonPresenter(llm)
    quiz = QuizGenerator(llm)
    tracker = ProgressTracker()
    
    graph = StateGraph(TutorialState)
    
    graph.add_node("assess", assessor.assess)
    graph.add_node("curriculum", curriculum.generate)
    graph.add_node("lesson", presenter.present)
    graph.add_node("quiz", quiz.generate)
    graph.add_node("progress", tracker.update)
    
    # Initial flow
    graph.add_edge(START, "assess")
    graph.add_edge("assess", "curriculum")
    graph.add_edge("curriculum", "lesson")
    graph.add_edge("lesson", "quiz")
    graph.add_edge("quiz", "progress")
    
    # Loop or end
    graph.add_conditional_edges(
        "progress",
        should_continue,
        {"next_lesson": "lesson", "end": END}
    )
    
    # Add memory for session persistence
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# ============= USAGE =============

class TutorialSession:
    """Manage a tutorial session."""
    
    def __init__(self, user_id: str, topic: str):
        self.user_id = user_id
        self.topic = topic
        self.app = create_tutorial_system()
        self.config = {"configurable": {"thread_id": f"tutorial-{user_id}-{topic}"}}
        self.started = False
    
    def start(self) -> str:
        """Start the tutorial."""
        state = {
            "user_id": self.user_id,
            "topic": self.topic,
            "skill_level": "beginner",
            "messages": [],
            "current_lesson": 0,
            "lessons": [],
            "quiz_results": [],
            "progress": 0.0,
            "completed": False
        }
        
        result = self.app.invoke(state, self.config)
        self.started = True
        
        # Collect all messages
        all_messages = [m.content for m in result["messages"] if isinstance(m, AIMessage)]
        return "\n\n---\n\n".join(all_messages)
    
    def next_lesson(self) -> str:
        """Move to next lesson."""
        if not self.started:
            return self.start()
        
        # Continue from checkpoint
        result = self.app.invoke(None, self.config)
        
        all_messages = [m.content for m in result["messages"] if isinstance(m, AIMessage)]
        return "\n\n---\n\n".join(all_messages[-3:])  # Last 3 messages
    
    def get_progress(self) -> dict:
        """Get current progress."""
        state = self.app.get_state(self.config)
        return {
            "progress": state.values.get("progress", 0),
            "current_lesson": state.values.get("current_lesson", 0),
            "total_lessons": len(state.values.get("lessons", [])),
            "completed": state.values.get("completed", False)
        }


if __name__ == "__main__":
    session = TutorialSession("user123", "Python Programming")
    
    # Start tutorial
    content = session.start()
    print(content)
    
    # Check progress
    progress = session.get_progress()
    print(f"\nProgress: {progress}")
```

---

> **📌 Previous:** See `LANGGRAPH_PATTERNS_ADVANCED.md` for architecture patterns
> **📌 Main:** See `LANGCHAIN_LANGGRAPH_DOCUMENTATION.md` for fundamentals
>
> **Part 3 of 3 | LangChain/LangGraph Documentation Series**

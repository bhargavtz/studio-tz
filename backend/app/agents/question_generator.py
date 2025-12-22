"""
NCD INAI - Question Generator Agent

Generates domain-specific questions for gathering requirements.
"""

from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings
from app.models.session import DomainClassification


QUESTION_GENERATOR_PROMPT = """You are an expert business consultant and web designer.
Your task is to generate smart, domain-specific questions to understand a client's needs.

You are helping someone build a {domain} website in the {industry} industry.

Generate 8-12 thoughtful questions that:
1. Are specific to this type of business (NOT generic questions)
2. Are written in simple, non-technical language
3. Help understand their unique value proposition
4. Gather information needed to design their website
5. Sound like a real consultant would ask

For a {domain} business, consider asking about:
- Their specific services/products
- Target audience
- Competitive advantages
- Visual/brand preferences
- Key features they need
- Special requirements for their industry

DO NOT ask:
- Generic questions like "what's your name"
- Technical questions about hosting or domains
- Questions that would be obvious from the domain

Each question should have:
- id: A unique identifier (q1, q2, etc.)
- question: The question text
- type: Input type (text, textarea, select, multiselect, yesno)
- options: Array of options (for select/multiselect types)
- required: Whether the question is required
- placeholder: Example/placeholder text

Keywords relevant to this business: {keywords}

Respond with a JSON object:
{{
    "questions": [
        {{
            "id": "q1",
            "question": "...",
            "type": "text|textarea|select|multiselect|yesno",
            "options": [],
            "required": true,
            "placeholder": "..."
        }}
    ]
}}

Generate questions that will help build an amazing {domain} website.
Respond ONLY with valid JSON."""


class QuestionGeneratorAgent:
    """Agent that generates domain-specific questions."""
    
    def __init__(self):
        self._llm = None
        self._chain = None
    
    def _get_llm(self):
        if self._llm is None:
            self._llm = ChatGroq(
                api_key=settings.groq_api_key,
                model_name=settings.question_model,  # Use Llama for questions
                temperature=0.7
            )
        return self._llm
    
    def _get_chain(self):
        if self._chain is None:
            prompt = ChatPromptTemplate.from_template(QUESTION_GENERATOR_PROMPT)
            parser = JsonOutputParser()
            self._chain = prompt | self._get_llm() | parser
        return self._chain
    
    async def generate(self, domain: DomainClassification) -> List[Dict[str, Any]]:
        """Generate domain-specific questions."""
        try:
            result = await self._get_chain().ainvoke({
                "domain": domain.domain.replace("_", " "),
                "industry": domain.industry,
                "keywords": ", ".join(domain.keywords)
            })
            return result.get("questions", [])
        except Exception as e:
            print(f"Question generation error: {e}")
            # Fallback questions
            return self._get_fallback_questions(domain.domain)
    
    def _get_fallback_questions(self, domain: str) -> List[Dict[str, Any]]:
        """Get fallback questions if AI fails."""
        return [
            {
                "id": "q1",
                "question": "What is your business name?",
                "type": "text",
                "options": [],
                "required": True,
                "placeholder": "Enter your business name"
            },
            {
                "id": "q2", 
                "question": "Describe your main services or products.",
                "type": "textarea",
                "options": [],
                "required": True,
                "placeholder": "Tell us what you offer..."
            },
            {
                "id": "q3",
                "question": "Who is your target audience?",
                "type": "text",
                "options": [],
                "required": True,
                "placeholder": "e.g., Young professionals, families, businesses"
            },
            {
                "id": "q4",
                "question": "What makes you different from competitors?",
                "type": "textarea",
                "options": [],
                "required": False,
                "placeholder": "Your unique selling points..."
            },
            {
                "id": "q5",
                "question": "What's the preferred color scheme or style?",
                "type": "select",
                "options": ["Modern & Minimal", "Bold & Vibrant", "Elegant & Professional", "Warm & Friendly", "Dark & Sophisticated"],
                "required": True,
                "placeholder": ""
            },
            {
                "id": "q6",
                "question": "Do you need a contact form?",
                "type": "yesno",
                "options": [],
                "required": True,
                "placeholder": ""
            },
            {
                "id": "q7",
                "question": "What pages do you need?",
                "type": "multiselect",
                "options": ["Home", "About", "Services", "Portfolio", "Contact", "Blog", "Pricing"],
                "required": True,
                "placeholder": ""
            },
            {
                "id": "q8",
                "question": "Any additional features or requirements?",
                "type": "textarea",
                "options": [],
                "required": False,
                "placeholder": "Special requests, integrations, etc."
            }
        ]


# Singleton instance
question_generator = QuestionGeneratorAgent()

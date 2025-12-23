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


QUESTION_GENERATOR_PROMPT = """You are a WORLD-CLASS BUSINESS CONSULTANT & UX STRATEGIST.
Your task is to conduct a high-level deep-dive interview to perfectly align a website's design with the client's strategic vision.

You are crafting specific, high-impact questions for a {domain} business in the {industry} sector.

Your Goal: Extract the "Soul" of the brand to enable an award-winning digital presence.

GUIDELINES FOR QUESTIONS:
1.  **Be Specific & Strategic**: Do NOT ask "What services do you offer?". Instead ask "Which of your services generates the most revenue, and which do you want to highlight for growth?"
2.  **Focus on Emotion & Vibe**: tailored questions about the *feeling* of the site. (e.g., "Should users feel excited and energized, or calm and reassured?")
3.  **Understand the User Journey**: Ask about what the primary conversion goal is (leads, sales, calls, brand awareness).
4.  **Visual DNA**: Ask about specific visual influencers or competitors they admire or despise.
5.  **Language**: Use professional, engaging, and confident language. No "intern-speak".

Generate 8-10 questions that cover:
- Core Value Proposition & Competitive Edge
- Target Audience Persona (Who are we trying to impress?)
- Primary User Action/Conversion Goal
- Aesthetic Preferences (Luxury, Minimal, Bold, Trustworthy, etc.)
- Specific Features needed for this specific Domain.

DO NOT ask:
- "What is your business name?" (We know this)
- Generic "What features do you want?" (You are the expert, suggest them later)
- Technical questions the client wouldn't know.

Format as a JSON object:
{{
    "questions": [
        {{
            "id": "q1",
            "question": "...",
            "type": "text|textarea|select|multiselect|yesno",
            "options": ["Option 1", "Option 2"],
            "required": true,
            "placeholder": "e.g., ..."
        }}
    ]
}}

Ensure the questions feel like a Premium Consultation session.
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

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


QUESTION_GENERATOR_PROMPT = """You are a FRIENDLY BUSINESS HELPER.
Your task is to ask SIMPLE, EASY questions to understand what kind of website the user wants to build.

You are helping someone create a {domain} website in the {industry} sector.

**CRITICAL RULES:**
1. **START SIMPLE**: First questions MUST be very basic (website name, what they do)
2. **NO TECHNICAL JARGON**: Never ask about hosting, deployment, technical specs, frameworks
3. **PROGRESSIVE DIFFICULTY**: Start with easy questions, gradually get more detailed
4. **KEEP IT SHORT**: Maximum 6-8 questions total
5. **USE SIMPLE LANGUAGE**: Write like you're talking to a friend, not a business consultant

**QUESTION STRUCTURE:**
Create questions in TWO levels:

**BASIC LEVEL (First 3-4 questions - REQUIRED):**
- Website name (ALWAYS first question)
- Business tagline or short description
- What does the business do (in simple words)
- Basic business description

**INTERMEDIATE LEVEL (Next 3-4 questions - REQUIRED):**
- Target audience (who will visit the site)
- Main pages needed (Home, About, Services, Contact, etc.)
- Key services or products to highlight
- Preferred style/mood (Modern, Professional, Colorful, Minimal, etc.) - keep options simple

**ABSOLUTELY FORBIDDEN TO ASK:**
- Hosting details or where to deploy
- Technical specifications
- Advanced color theory or design systems
- Complex styling preferences
- Framework choices
- SEO strategies
- Analytics or tracking
- Any question a non-technical person wouldn't understand

**FORMAT:**
Each question MUST include a "level" field.

{{
    "questions": [
        {{
            "id": "q1",
            "question": "What is the name of your website or business?",
            "type": "text",
            "level": "BASIC",
            "options": [],
            "required": true,
            "placeholder": "e.g., My Awesome Store"
        }},
        {{
            "id": "q2",
            "question": "...",
            "type": "text|textarea|select|multiselect",
            "level": "BASIC|INTERMEDIATE",
            "options": ["Option 1", "Option 2"],
            "required": true,
            "placeholder": "..."
        }}
    ]
}}

**REMEMBER:**
- Question 1 MUST ALWAYS be "What is the name of your website or business?"
- Total 6-8 questions maximum
- First 3-4 are BASIC level
- Next 3-4 are INTERMEDIATE level
- NO advanced/technical questions
- Use friendly, simple language

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
                "question": "What is the name of your website or business?",
                "type": "text",
                "level": "BASIC",
                "options": [],
                "required": True,
                "placeholder": "e.g., My Awesome Business"
            },
            {
                "id": "q2",
                "question": "Write a short tagline or description for your business",
                "type": "text",
                "level": "BASIC",
                "options": [],
                "required": True,
                "placeholder": "e.g., Fresh coffee delivered to your door"
            },
            {
                "id": "q3", 
                "question": "What does your business do? (in simple words)",
                "type": "textarea",
                "level": "BASIC",
                "options": [],
                "required": True,
                "placeholder": "Tell us briefly what you offer..."
            },
            {
                "id": "q4",
                "question": "Who are your main customers?",
                "type": "text",
                "level": "INTERMEDIATE",
                "options": [],
                "required": True,
                "placeholder": "e.g., Young professionals, families, small businesses"
            },
            {
                "id": "q5",
                "question": "Which pages do you need on your website?",
                "type": "multiselect",
                "level": "INTERMEDIATE",
                "options": ["Home", "About", "Services", "Products", "Contact", "Blog"],
                "required": True,
                "placeholder": ""
            },
            {
                "id": "q6",
                "question": "What style do you prefer for your website?",
                "type": "select",
                "level": "INTERMEDIATE",
                "options": ["Modern & Clean", "Colorful & Fun", "Professional & Elegant", "Simple & Minimal"],
                "required": True,
                "placeholder": ""
            }
        ]


# Singleton instance
question_generator = QuestionGeneratorAgent()

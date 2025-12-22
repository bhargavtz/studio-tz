"""
NCD INAI - Blueprint Architect Agent

Creates structured website blueprints from user answers.
"""

from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings
from app.models.session import DomainClassification


BLUEPRINT_ARCHITECT_PROMPT = """You are an expert website architect and UX designer.
Your task is to create a detailed website blueprint based on the client's requirements.

Business Details:
- Domain: {domain}
- Industry: {industry}
- Original Intent: {intent}

Client's Answers:
{answers}

Create a comprehensive website blueprint that includes:
1. All necessary pages for this type of business
2. Well-structured sections for each page
3. Appropriate components within each section
4. A cohesive theme and style based on their preferences

Section types to use:
- hero: Main banner with headline and CTA
- about: About the business
- services: Services or products offered
- features: Key features/benefits
- gallery: Image gallery/portfolio
- testimonials: Customer reviews
- team: Team members
- pricing: Pricing tables
- contact: Contact form and info
- cta: Call to action sections
- footer: Footer with links

Component types to use:
- heading: Text heading (h1, h2, etc.)
- paragraph: Text content
- button: CTA button
- image: Image element
- card: Content card
- form: Contact/signup form
- list: Bulleted/numbered list
- icon: Icon element
- map: Location map

Create a blueprint as a JSON object with this structure:
{{
    "name": "Business Name Website",
    "description": "Brief description of the website",
    "domain": "{domain}",
    "pages": [
        {{
            "id": "home",
            "title": "Home",
            "slug": "/",
            "sections": [
                {{
                    "id": "hero",
                    "type": "hero",
                    "title": "Section title",
                    "components": [
                        {{
                            "id": "hero-heading",
                            "type": "heading",
                            "content": "Actual headline text",
                            "properties": {{"level": "h1"}}
                        }}
                    ],
                    "properties": {{}}
                }}
            ],
            "meta": {{"title": "...", "description": "..."}}
        }}
    ],
    "theme": {{
        "primaryColor": "#hex",
        "secondaryColor": "#hex",
        "backgroundColor": "#hex",
        "textColor": "#hex",
        "accentColor": "#hex",
        "fontFamily": "Font name",
        "style": "modern|classic|minimal|bold"
    }},
    "global_styles": {{
        "borderRadius": "8px",
        "spacing": "comfortable",
        "animation": "subtle"
    }}
}}

Make sure:
- Content reflects the actual business details from their answers
- Include real placeholder text based on their business
- Theme colors match their stated preferences
- Structure is logical for their industry

Respond ONLY with valid JSON."""


class BlueprintArchitectAgent:
    """Agent that creates website blueprints from requirements."""
    
    def __init__(self):
        self._llm = None
        self._chain = None
    
    def _get_llm(self):
        if self._llm is None:
            self._llm = ChatGroq(
                api_key=settings.groq_api_key,
                model_name=settings.llm_model,
                temperature=0.7
            )
        return self._llm
    
    def _get_chain(self):
        if self._chain is None:
            prompt = ChatPromptTemplate.from_template(BLUEPRINT_ARCHITECT_PROMPT)
            parser = JsonOutputParser()
            self._chain = prompt | self._get_llm() | parser
        return self._chain
    
    async def create_blueprint(
        self,
        domain: DomainClassification,
        intent: str,
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a website blueprint from requirements."""
        # Format answers nicely
        answers_text = self._format_answers(answers)
        
        try:
            result = await self._get_chain().ainvoke({
                "domain": domain.domain.replace("_", " "),
                "industry": domain.industry,
                "intent": intent,
                "answers": answers_text
            })
            return result
        except Exception as e:
            print(f"Blueprint generation error: {e}")
            return self._get_fallback_blueprint(domain, answers)
    
    def _format_answers(self, answers: Dict[str, Any]) -> str:
        """Format answers for the prompt."""
        lines = []
        for key, value in answers.items():
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _get_fallback_blueprint(
        self,
        domain: DomainClassification,
        answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get a fallback blueprint if AI fails."""
        business_name = answers.get("q1", "My Business")
        
        return {
            "name": f"{business_name} Website",
            "description": f"A professional {domain.domain.replace('_', ' ')} website",
            "domain": domain.domain,
            "pages": [
                {
                    "id": "home",
                    "title": "Home",
                    "slug": "/",
                    "sections": [
                        {
                            "id": "hero",
                            "type": "hero",
                            "title": "Welcome",
                            "components": [
                                {
                                    "id": "hero-h1",
                                    "type": "heading",
                                    "content": f"Welcome to {business_name}",
                                    "properties": {"level": "h1"}
                                },
                                {
                                    "id": "hero-p",
                                    "type": "paragraph",
                                    "content": "Your trusted partner for quality service.",
                                    "properties": {}
                                },
                                {
                                    "id": "hero-btn",
                                    "type": "button",
                                    "content": "Get Started",
                                    "properties": {"variant": "primary"}
                                }
                            ],
                            "properties": {}
                        },
                        {
                            "id": "about",
                            "type": "about",
                            "title": "About Us",
                            "components": [
                                {
                                    "id": "about-h2",
                                    "type": "heading",
                                    "content": "About Us",
                                    "properties": {"level": "h2"}
                                },
                                {
                                    "id": "about-p",
                                    "type": "paragraph",
                                    "content": answers.get("q2", "We provide excellent services."),
                                    "properties": {}
                                }
                            ],
                            "properties": {}
                        },
                        {
                            "id": "contact",
                            "type": "contact",
                            "title": "Contact Us",
                            "components": [
                                {
                                    "id": "contact-h2",
                                    "type": "heading",
                                    "content": "Get In Touch",
                                    "properties": {"level": "h2"}
                                },
                                {
                                    "id": "contact-form",
                                    "type": "form",
                                    "content": "",
                                    "properties": {"fields": ["name", "email", "message"]}
                                }
                            ],
                            "properties": {}
                        }
                    ],
                    "meta": {
                        "title": f"{business_name} - Home",
                        "description": f"Welcome to {business_name}"
                    }
                }
            ],
            "theme": {
                "primaryColor": "#3B82F6",
                "secondaryColor": "#1E40AF",
                "backgroundColor": "#FFFFFF",
                "textColor": "#1F2937",
                "accentColor": "#10B981",
                "fontFamily": "Inter",
                "style": "modern"
            },
            "global_styles": {
                "borderRadius": "8px",
                "spacing": "comfortable",
                "animation": "subtle"
            }
        }


# Singleton instance
blueprint_architect = BlueprintArchitectAgent()

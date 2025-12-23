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


BLUEPRINT_ARCHITECT_PROMPT = """You are a WORLD-RENOWNED WEBSITE ARCHITECT & UX VISIONARY.
Your task is to correct and elevate the client's vision into a MASTERPIECE BLUEPRINT.

You are designing a Premium, Award-Winning Website for:
- Domain: {domain}
- Industry: {industry}
- Client Intent: {intent}

Client Answers:
{answers}

YOUR MANDATE:
1.  **Orchestrate the User Journey**: Don't just list pages. Create a flow that guides users from "Interest" to "Action".
2.  **Strategic Sections**:
    - Reject generic "About" or "Services" labels if they are boring. Rename them excitingly (e.g., "Our Legacy", "Craftsmanship", "Why Choose Us").
    - Include "Social Proof" (Testimonials, Logos) early in the journey.
    - ESSENTIAL: Every page MUST have a clear Call-to-Action (CTA).
3.  **Visual Language**:
    - Select a theme that fits the *industry* but stands out. (e.g., A law firm should be 'Trustworthy' but 'Modern', not 'Boring').
    - Suggest deep, rich color palettes or sophisticated gradients.
4.  **Content Depth**:
    - For each section, define the key components precisely.
    - Use "Cards", "Grids", "Parallax Headers", and "Sticky Navigations" where they add value.

STRUCTURE REQUIREMENTS:
- **Pages**: Home, About, [Industry Specific Page], [Industry Specific Page], Contact.
- **Home Page**: Must be a "Showstopper". Hero -> Value Props -> Feature Highlight -> Social Proof -> CTA -> Footer.

Create the Blueprint JSON:
{{
    "name": "Business Name",
    "description": "A high-conversion, premium digital experience.",
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
                    "title": "Hero Section",
                    "components": [
                        {{
                            "id": "hero-heading",
                            "type": "heading",
                            "content": "Compelling Headline Here",
                            "properties": {{"level": "h1", "highlight": true}}
                        }}
                    ],
                    "properties": {{"layout": "full-screen", "alignment": "center"}}
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
        "fontFamily": "Font Name",
        "style": "glassmorphism|minimalist_luxury|bold_brutalist|soft_modern"
    }},
    "global_styles": {{
        "borderRadius": "12px",
        "spacing": "relaxed",
        "animation": "smooth-reveal"
    }}
}}

Respond ONLY with valid JSON. Do not include markdown blocks."""


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


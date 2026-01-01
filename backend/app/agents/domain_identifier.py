"""
NCD INAI - Domain Identifier Agent

Identifies the business domain from user's intent description.
"""

import logging
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings
from app.models.session import DomainClassification

logger = logging.getLogger(__name__)


DOMAIN_IDENTIFIER_PROMPT = """You are an expert business analyst. 
Your task is to classify the type of website a user wants to build based on their description.

Analyze the user's intent and provide a structured classification.

Common domains include:
- restaurant: Restaurants, cafes, food establishments
- flower_shop: Florists, floral designers
- portfolio: Personal portfolios, creative professionals
- agency: Marketing, design, consulting agencies
- ecommerce: Online stores, product sales
- saas: Software as a service products
- blog: Personal or professional blogs
- nonprofit: Charities, NGOs
- medical: Healthcare, clinics, doctors
- legal: Law firms, attorneys
- realestate: Real estate agencies, property listings
- education: Schools, courses, tutoring
- fitness: Gyms, personal trainers
- beauty: Salons, spas, beauty services
- photography: Photographers, studios
- construction: Contractors, builders
- automotive: Car dealers, repair shops
- travel: Travel agencies, tour operators
- event: Event planners, wedding services
- tech_startup: Technology startups

If the domain doesn't match any common type, create an appropriate domain name.

User's Intent: {intent}

Respond with a JSON object containing:
- domain: The primary domain identifier (lowercase, underscore-separated)
- industry: The broader industry category
- business_type: Specific type of business (local_business, online_service, professional_service, etc.)
- keywords: List of 3-5 relevant keywords
- confidence: Your confidence score (0.0 to 1.0)

Respond ONLY with valid JSON, no other text."""


class DomainIdentifierAgent:
    """Agent that identifies the business domain from user intent."""
    
    def __init__(self):
        self._llm = None
        self._chain = None
    
    def _get_llm(self):
        if self._llm is None:
            self._llm = ChatGroq(
                api_key=settings.groq_api_key,
                model_name=settings.llm_model,
                temperature=0.3
            )
        return self._llm
    
    def _get_chain(self):
        if self._chain is None:
            parser = JsonOutputParser()
            prompt = ChatPromptTemplate.from_template(DOMAIN_IDENTIFIER_PROMPT)
            self._chain = prompt | self._get_llm() | parser
        return self._chain
    
    async def identify(self, intent: str) -> DomainClassification:
        """Identify the domain from user's intent."""
        try:
            result = await self._get_chain().ainvoke({"intent": intent})
            return DomainClassification(**result)
        except Exception as e:
            logger.warning(f"Domain identification error: {e}")
            # Fallback classification
            return DomainClassification(
                domain="general_business",
                industry="general",
                business_type="small_business",
                keywords=["website", "business", "online presence"],
                confidence=0.5
            )


# Singleton instance
domain_identifier = DomainIdentifierAgent()

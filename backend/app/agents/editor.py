"""
NCD INAI - Editor Agent (Planner Only)

LLM decides WHAT to edit, backend executes HOW.
"""

import logging
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings

logger = logging.getLogger(__name__)


EDITOR_PLANNER_PROMPT = """You are an expert web design consultant.
Your task is to understand the user's edit request and return a STRUCTURED EDIT PLAN.

You do NOT modify code directly. You only decide WHAT should change.

Current Element Info:
- NCD ID: {ncd_id}
- File: {file_path}
- Type: {element_type}
- Current Value: {current_value}

User's Request:
"{instruction}"

Analyze the request and return ONE of these edit actions:

1. UPDATE_TEXT - Change text content
2. UPDATE_STYLE - Modify CSS property
3. UPDATE_ATTRIBUTE - Change HTML attribute
4. ADD_CLASS - Add CSS class
5. REMOVE_CLASS - Remove CSS class

Response format (JSON ONLY):
{{
    "action": "UPDATE_TEXT|UPDATE_STYLE|UPDATE_ATTRIBUTE|ADD_CLASS|REMOVE_CLASS",
    "target_ncd_id": "{ncd_id}",
    "target_file": "{file_path}",
    "parameters": {{
        // For UPDATE_TEXT:
        "new_text": "..."
        
        // For UPDATE_STYLE:
        "property": "color",
        "value": "#ff0000"
        
        // For UPDATE_ATTRIBUTE:
        "attribute": "href",
        "value": "https://..."
        
        // For ADD_CLASS / REMOVE_CLASS:
        "class_name": "highlight"
    }},
    "reasoning": "Brief explanation of why this edit makes sense"
}}

Rules:
- Return ONLY valid JSON
- Choose the most appropriate action
- Be specific with values
- If request is unclear, use "UPDATE_TEXT" as default

Respond with JSON only."""


class EditorPlannerAgent:
    """Agent that plans edits (does not execute them)."""
    
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
            prompt = ChatPromptTemplate.from_template(EDITOR_PLANNER_PROMPT)
            parser = JsonOutputParser()
            self._chain = prompt | self._get_llm() | parser
        return self._chain
    
    async def plan_edit(
        self,
        ncd_id: str,
        file_path: str,
        element_type: str,
        current_value: str,
        instruction: str
    ) -> Dict[str, Any]:
        """Plan an edit based on user instruction."""
        try:
            result = await self._get_chain().ainvoke({
                "ncd_id": ncd_id,
                "file_path": file_path,
                "element_type": element_type,
                "current_value": current_value,
                "instruction": instruction
            })
            return result
        except Exception as e:
            logger.warning(f"Edit planning error: {e}")
            # Fallback: simple text update
            return {
                "action": "UPDATE_TEXT",
                "target_ncd_id": ncd_id,
                "target_file": file_path,
                "parameters": {
                    "new_text": instruction  # Use instruction as new text
                },
                "reasoning": f"Fallback due to error: {str(e)}"
            }


# Singleton instance
editor_planner = EditorPlannerAgent()

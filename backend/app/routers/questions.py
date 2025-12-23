"""
NCD INAI - Questions Router
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.session_manager import session_manager
from app.models.session import SessionStatus
from app.agents.question_generator import question_generator

router = APIRouter()




class QuestionsResponse(BaseModel):
    session_id: str
    questions: List[Dict[str, Any]]
    total_questions: int


class AnswersRequest(BaseModel):
    answers: Dict[str, Any]
    
    @classmethod
    def validate_answers(cls, answers: Dict[str, Any], questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate answers match question types and requirements."""
        validated = {}
        
        for question in questions:
            q_id = question['id']
            q_type = question['type']
            required = question.get('required', False)
            
            answer = answers.get(q_id)
            
            # Skip validation if answer is None/empty (even if required)
            # We'll be lenient and let AI work with partial data
            if answer is None or answer == '' or (isinstance(answer, list) and len(answer) == 0):
                if required:
                    # Log warning but don't block
                    print(f"Warning: Required question {q_id} was not answered")
                continue
            
            # Type validation and sanitization
            if q_type == 'text' or q_type == 'textarea':
                if not isinstance(answer, str):
                    raise ValueError(f"Question {q_id} must be a string")
                # Sanitize: limit length
                validated[q_id] = str(answer)[:5000]
                
            elif q_type == 'select':
                if not isinstance(answer, str):
                    raise ValueError(f"Question {q_id} must be a string")
                options = question.get('options', [])
                if options and answer not in options:
                    # Be lenient - accept the value anyway
                    print(f"Warning: Question {q_id} has unexpected option: {answer}")
                validated[q_id] = answer
                
            elif q_type == 'multiselect':
                if not isinstance(answer, list):
                    raise ValueError(f"Question {q_id} must be a list")
                options = question.get('options', [])
                if options:
                    for item in answer:
                        if item not in options:
                            print(f"Warning: Question {q_id} has unexpected option: {item}")
                validated[q_id] = answer
                
            elif q_type == 'yesno':
                if not isinstance(answer, bool):
                    raise ValueError(f"Question {q_id} must be a boolean")
                validated[q_id] = answer
            else:
                # Unknown type, accept as-is but sanitize strings
                if isinstance(answer, str):
                    validated[q_id] = str(answer)[:5000]
                else:
                    validated[q_id] = answer
        
        return validated


class AnswersResponse(BaseModel):
    session_id: str
    status: str
    answers_count: int
    message: str


@router.get("/questions/{session_id}", response_model=QuestionsResponse)
async def get_questions(session_id: str):
    """Get or generate domain-specific questions."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.domain:
        raise HTTPException(
            status_code=400, 
            detail="Domain not identified yet. Process intent first."
        )
    
    # Check if questions already generated
    if session.questions:
        return QuestionsResponse(
            session_id=session.id,
            questions=session.questions,
            total_questions=len(session.questions)
        )
    
    # Generate questions
    questions = await question_generator.generate(session.domain)
    session.questions = questions
    session.status = SessionStatus.QUESTIONS_GENERATED
    
    # Save questions
    session_manager.save_json_file(
        session_id,
        "domain_questions.json",
        {"domain": session.domain.domain, "questions": questions}
    )
    
    session_manager.update_session(session)
    
    return QuestionsResponse(
        session_id=session.id,
        questions=questions,
        total_questions=len(questions)
    )


@router.post("/answers/{session_id}", response_model=AnswersResponse)
async def submit_answers(session_id: str, request: AnswersRequest):
    """Submit answers to the questions."""
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session.questions:
        raise HTTPException(
            status_code=400,
            detail="Questions not generated yet."
        )
    
    # Validate answers against questions
    try:
        validated_answers = AnswersRequest.validate_answers(
            request.answers,
            session.questions
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid answers: {str(e)}"
        )
    
    # Store validated answers
    session.answers = validated_answers
    session.status = SessionStatus.ANSWERS_COLLECTED
    
    # Save answers
    session_manager.save_json_file(
        session_id,
        "answers.json",
        validated_answers
    )
    
    session_manager.update_session(session)
    
    return AnswersResponse(
        session_id=session.id,
        status=session.status.value,
        answers_count=len(validated_answers),
        message="Answers saved. Ready to generate blueprint."
    )

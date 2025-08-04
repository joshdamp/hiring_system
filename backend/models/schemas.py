from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# User models
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=18, le=100)
    experience: int = Field(..., ge=0, le=50)
    consent: bool = Field(..., description="Data processing consent")

class UserResponse(BaseModel):
    userId: str
    name: str
    age: int
    experience: int
    consent: bool
    timestamp: str

# Question models
class FixedQuestion(BaseModel):
    QuestionID: str
    Prompt: str
    Option1: str
    Option2: str
    Option3: str
    Option4: str

class FollowUpQuestion(BaseModel):
    QuestionID: str
    QuestionText: str

# Response models
class QuestionResponse(BaseModel):
    questionId: str
    response: Any  # Can be int (1-4) for fixed questions or str for follow-up
    timestamp: str

class InitialResponsesRequest(BaseModel):
    userId: str
    responses: List[QuestionResponse]

class FollowUpResponsesRequest(BaseModel):
    userId: str
    responses: List[QuestionResponse]

class FollowUpQuestionsRequest(BaseModel):
    userId: str

# Assessment results
class TraitScore(BaseModel):
    name: str
    ranking: int
    score: float

class FinalResults(BaseModel):
    userId: str
    name: str
    traits: List[TraitScore]
    timestamp: str
    assessmentAccuracy: float

# Matching models
class MatchingRequest(BaseModel):
    userTraits: List[TraitScore]
    idealTraits: List[TraitScore]

# API Response models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

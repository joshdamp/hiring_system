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
class LikertQuestion(BaseModel):
    QuestionID: str
    LeftStatement: str  # Left side statement (e.g., "I enjoy imagining the future")
    RightStatement: str  # Right side statement (e.g., "I prefer dealing with today")
    Theme: str  # Strategic, Executing, Influencing, Relationship Building

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
class LikertResponse(BaseModel):
    questionId: str
    response: int = Field(..., ge=1, le=5, description="1=Strongly Left, 2=Somewhat Left, 3=Neutral, 4=Somewhat Right, 5=Strongly Right")
    timestamp: str

class QuestionResponse(BaseModel):
    questionId: str
    response: Optional[Any] = None  # For regular responses (Chapter 3, text answers)
    firstChoice: Optional[str] = None  # For dual-choice responses (Chapter 2)
    secondChoice: Optional[str] = None  # For dual-choice responses (Chapter 2)
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

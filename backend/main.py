from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from models.schemas import *
from services.sheets_service import SheetsService
from services.huggingface_ai_service import HuggingFaceAIService
from services.assessment_service import AssessmentService

# Initialize FastAPI app
app = FastAPI(
    title="Automated Hiring System API",
    description="AI-powered psychometric assessment for hiring",
    version="1.0.0"
)

# CORS middleware  
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://hiring-system.onrender.com",  # Your actual frontend URL
        "https://hiring-system-frontend.onrender.com",
        "https://*.vercel.app",
        "https://*.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With"],
)

# Initialize services
sheets_service = SheetsService()
ai_service = HuggingFaceAIService()  # FREE AI Service!
assessment_service = AssessmentService(sheets_service, ai_service)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Automated Hiring System API", 
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "users": "/api/users", 
            "questions": "/api/questions/fixed",
            "docs": "/docs"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/users", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """Create a new user and store in Google Sheets"""
    try:
        print(f"Creating user with data: {user_data.dict()}")
        user_response = await assessment_service.create_user(user_data)
        print(f"User created successfully: {user_response.userId}")
        return user_response
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Also add endpoint without /api prefix for frontend compatibility
@app.post("/users", response_model=UserResponse)
async def create_user_alt(user_data: UserCreate):
    """Create a new user and store in Google Sheets (alternative endpoint)"""
    return await create_user(user_data)

@app.get("/api/questions/fixed")
async def get_fixed_questions():
    """Get all fixed psychometric questions"""
    try:
        questions = await assessment_service.get_fixed_questions()
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Also add endpoint without /api prefix for frontend compatibility
@app.get("/questions/fixed")
async def get_fixed_questions_alt():
    """Get all fixed psychometric questions (alternative endpoint)"""
    return await get_fixed_questions()

@app.post("/questions/follow-up/{round}")
async def get_follow_up_questions_alt(round: int, user_data: UserCreate):
    """Get follow-up questions (alternative endpoint)"""
    return await get_follow_up_questions(round, user_data)

@app.post("/responses/initial")
async def submit_initial_responses_alt(request: InitialResponsesRequest):
    """Submit initial responses (alternative endpoint)"""
    return await submit_initial_responses(request)

@app.post("/api/questions/follow-up/{round}")
async def get_follow_up_questions(round: int, request: FollowUpQuestionsRequest):
    """Generate personalized follow-up questions based on previous responses"""
    try:
        if round not in [1, 2]:
            raise HTTPException(status_code=400, detail="Round must be 1 or 2")
        
        questions = await assessment_service.generate_follow_up_questions(
            request.userId, round
        )
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/responses/initial")
async def submit_initial_responses(request: InitialResponsesRequest):
    """Submit initial assessment responses"""
    try:
        result = await assessment_service.submit_initial_responses(
            request.userId, request.responses
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/responses/follow-up/{round}")
async def submit_follow_up_responses(round: int, request: FollowUpResponsesRequest):
    """Submit follow-up responses"""
    try:
        if round not in [1, 2]:
            raise HTTPException(status_code=400, detail="Round must be 1 or 2")
        
        result = await assessment_service.submit_follow_up_responses(
            request.userId, request.responses, round
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary/initial/{user_id}")
async def get_initial_summary(user_id: str):
    """Get initial personality summary"""
    try:
        summary = await assessment_service.generate_initial_summary(user_id)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary/follow-up/{user_id}/{round}")
async def get_follow_up_summary(user_id: str, round: int):
    """Get follow-up summary after each round"""
    try:
        if round not in [1, 2]:
            raise HTTPException(status_code=400, detail="Round must be 1 or 2")
        
        summary = await assessment_service.generate_follow_up_summary(user_id, round)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary/final/{user_id}")
async def get_final_summary(user_id: str):
    """Get final comprehensive personality summary"""
    try:
        summary = await assessment_service.generate_final_summary(user_id)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/results/{user_id}")
async def get_final_results(user_id: str):
    """Get final trait rankings and complete results"""
    try:
        results = await assessment_service.get_final_results(user_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/matching/calculate")
async def calculate_match_score(request: MatchingRequest):
    """Calculate match score between user profile and ideal candidate"""
    try:
        match_score = await assessment_service.calculate_match_score(
            request.userTraits, request.idealTraits
        )
        return {"matchScore": match_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-sheets")
async def test_sheets_connection():
    """Test Google Sheets connection"""
    try:
        # Test if sheets service is working
        test_data = {
            "userId": "test-user-123",
            "name": "Test User",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "experience": "3-5 years",
            "position": "Software Engineer",
            "timestamp": datetime.now().isoformat()
        }
        
        result = await sheets_service.save_user_info(test_data)
        
        return {
            "status": "success" if result else "mock",
            "message": "Google Sheets connection tested",
            "sheets_connected": sheets_service.spreadsheet is not None,
            "test_data_saved": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "sheets_connected": False
        }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )

from typing import List, Dict, Any
import math
from datetime import datetime
from .sheets_service import SheetsService
from .nvidia_ai_service import NvidiaAIService
from models.schemas import UserCreate, UserResponse, TraitScore, FinalResults

class AssessmentService:
    def __init__(self, sheets_service: SheetsService, ai_service: NvidiaAIService):
        self.sheets_service = sheets_service
        self.ai_service = ai_service  # NVIDIA AI Service!
        
        # Store trait rankings during assessment
        self.user_trait_rankings = {}
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user and return user response"""
        try:
            # Generate unique user ID
            user_id = f"U{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare user data for saving (only fields that exist in Google Sheets)
            user_dict = {
                'userId': user_id,
                'name': user_data.name,
                'age': user_data.age,
                'experience': user_data.experience,
                'consent': user_data.consent,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save user info to Google Sheets
            await self.sheets_service.save_user_info(user_dict)
            
            # Return user response
            return UserResponse(
                userId=user_id,
                name=user_data.name,
                age=user_data.age,
                experience=user_data.experience,
                consent=user_data.consent,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            raise Exception(f"Failed to create user: {str(e)}")
    
    async def get_fixed_questions(self) -> List[Dict[str, Any]]:
        """Get all fixed psychometric questions"""
        try:
            questions = await self.sheets_service.get_fixed_questions()
            return questions
        except Exception as e:
            raise Exception(f"Failed to get fixed questions: {str(e)}")
    
    async def submit_initial_responses(self, user_id: str, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit initial assessment responses and analyze them"""
        try:
            # Convert Pydantic models to dictionaries if needed
            if responses and hasattr(responses[0], 'model_dump'):
                response_dicts = [resp.model_dump() for resp in responses]
            else:
                response_dicts = responses
            
            # Save responses to Google Sheets
            await self.sheets_service.save_initial_responses(user_id, response_dicts)
            
            # Get questions for analysis
            questions = await self.sheets_service.get_fixed_questions()
            
            # Analyze responses with LLM to get trait rankings
            trait_rankings = await self.ai_service.analyze_initial_responses(response_dicts, questions)
            
            # Store trait rankings for this user
            self.user_trait_rankings[user_id] = trait_rankings
            
            return {
                "success": True,
                "message": "Initial responses submitted successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to submit initial responses: {str(e)}")
    
    async def generate_follow_up_questions(self, user_id: str, round_num: int) -> List[Dict[str, Any]]:
        """Generate personalized follow-up questions"""
        try:
            print(f"DEBUG: Assessment service generating follow-up questions for {user_id}, round {round_num}")
            
            # Get previous responses
            if round_num == 1:
                previous_responses = await self.sheets_service.get_user_responses(user_id, "initial")
            else:
                previous_responses = await self.sheets_service.get_user_responses(user_id, "follow_up_1")
            
            # Get current trait rankings
            trait_rankings = self.user_trait_rankings.get(user_id, {})
            print(f"DEBUG: Retrieved trait rankings for {user_id}: {len(trait_rankings)} traits")
            print(f"DEBUG: Previous responses count: {len(previous_responses)}")
            
            # If no trait rankings in memory, try to regenerate from initial responses
            if not trait_rankings and round_num == 1:
                print(f"DEBUG: No trait rankings in memory, regenerating from initial responses")
                initial_responses = await self.sheets_service.get_user_responses(user_id, "User_Responses")
                if initial_responses:
                    trait_rankings = await self.ai_service.analyze_trait_rankings(initial_responses)
                    self.user_trait_rankings[user_id] = trait_rankings
                    print(f"DEBUG: Regenerated {len(trait_rankings)} trait rankings")
            
            # Generate questions using LLM
            questions = await self.ai_service.generate_follow_up_questions(
                user_id, trait_rankings, previous_responses, round_num
            )
            
            print(f"DEBUG: Generated {len(questions)} questions")
            
            # Save questions to Google Sheets
            await self.sheets_service.save_follow_up_questions(user_id, questions, round_num)
            
            return questions
            
        except Exception as e:
            print(f"ERROR: Failed to generate follow-up questions: {str(e)}")
            raise Exception(f"Failed to generate follow-up questions: {str(e)}")
    
    async def submit_follow_up_responses(self, user_id: str, responses: List[Dict[str, Any]], round_num: int) -> Dict[str, Any]:
        """Submit follow-up responses and update trait rankings"""
        try:
            # Convert Pydantic models to dictionaries if needed
            if responses and hasattr(responses[0], 'model_dump'):
                response_dicts = [resp.model_dump() for resp in responses]
            elif responses and hasattr(responses[0], 'dict'):
                response_dicts = [resp.dict() for resp in responses]
            else:
                response_dicts = responses
            
            # Save responses to Google Sheets
            await self.sheets_service.save_follow_up_responses(user_id, response_dicts, round_num)
            
            # Update trait rankings based on new responses
            current_rankings = self.user_trait_rankings.get(user_id, {})
            updated_rankings = await self.ai_service.update_trait_rankings(
                current_rankings, response_dicts, round_num
            )
            
            # Store updated rankings
            self.user_trait_rankings[user_id] = updated_rankings
            
            return {
                "success": True,
                "message": f"Follow-up responses for round {round_num} submitted successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to submit follow-up responses: {str(e)}")
    
    async def generate_initial_summary(self, user_id: str) -> str:
        """Generate initial personality summary"""
        try:
            # Get user responses
            initial_responses = await self.sheets_service.get_user_responses(user_id, "initial")
            
            # Get trait rankings
            trait_rankings = self.user_trait_rankings.get(user_id, {})
            
            # Generate summary using LLM
            summary = await self.ai_service.generate_summary(
                user_id, initial_responses, trait_rankings, "initial"
            )
            
            return summary
            
        except Exception as e:
            raise Exception(f"Failed to generate initial summary: {str(e)}")
    
    async def generate_follow_up_summary(self, user_id: str, round_num: int) -> str:
        """Generate follow-up summary after each round"""
        try:
            # Get all user responses up to this point
            all_responses = []
            initial_responses = await self.sheets_service.get_user_responses(user_id, "initial")
            follow_up_1_responses = await self.sheets_service.get_user_responses(user_id, "follow_up_1")
            all_responses.extend(initial_responses)
            all_responses.extend(follow_up_1_responses)
            
            if round_num == 2:
                follow_up_2_responses = await self.sheets_service.get_user_responses(user_id, "follow_up_2")
                all_responses.extend(follow_up_2_responses)
            
            # Get current trait rankings
            trait_rankings = self.user_trait_rankings.get(user_id, {})
            
            # Generate summary using LLM
            summary = await self.ai_service.generate_summary(
                user_id, all_responses, trait_rankings, "follow_up"
            )
            
            return summary
            
        except Exception as e:
            raise Exception(f"Failed to generate follow-up summary: {str(e)}")
    
    async def generate_final_summary(self, user_id: str) -> str:
        """Generate final comprehensive personality summary"""
        try:
            # Get all user responses
            all_responses = []
            initial_responses = await self.sheets_service.get_user_responses(user_id, "initial")
            follow_up_1_responses = await self.sheets_service.get_user_responses(user_id, "follow_up_1")
            follow_up_2_responses = await self.sheets_service.get_user_responses(user_id, "follow_up_2")
            all_responses.extend(initial_responses)
            all_responses.extend(follow_up_1_responses)
            all_responses.extend(follow_up_2_responses)
            
            # Get final trait rankings
            trait_rankings = self.user_trait_rankings.get(user_id, {})
            
            # Generate final summary using LLM
            summary = await self.ai_service.generate_summary(
                user_id, all_responses, trait_rankings, "final"
            )
            
            return summary
            
        except Exception as e:
            raise Exception(f"Failed to generate final summary: {str(e)}")
    
    async def get_final_results(self, user_id: str) -> FinalResults:
        """Get final trait rankings and complete results"""
        try:
            # Get trait rankings
            trait_rankings = self.user_trait_rankings.get(user_id, {})
            
            if not trait_rankings:
                raise Exception("No trait rankings found for user")
            
            # Convert to TraitScore objects
            traits = []
            for trait_name, ranking in trait_rankings.items():
                # Calculate score from ranking (higher rank = lower score)
                score = (35 - ranking) / 34 * 100  # Convert to 0-100 scale
                traits.append(TraitScore(
                    name=trait_name,
                    ranking=ranking,
                    score=score
                ))
            
            # Sort by ranking
            traits.sort(key=lambda x: x.ranking)
            
            # Save to Google Sheets with trait rankings
            user_name = await self.sheets_service.get_user_name(user_id)
            await self.sheets_service.save_final_results(user_id, user_name, trait_rankings)
            
            return FinalResults(
                userId=user_id,
                name=user_name,
                traits=traits,
                timestamp=datetime.now().isoformat(),
                assessmentAccuracy=96.0  # Mock accuracy score
            )
            
        except Exception as e:
            raise Exception(f"Failed to get final results: {str(e)}")
    
    async def calculate_match_score(self, user_traits: List[TraitScore], ideal_traits: List[TraitScore]) -> float:
        """Calculate match score using the piecewise weight function"""
        try:
            def weight_function(distance: float) -> float:
                """Piecewise weight function as specified"""
                if 0 <= distance <= 7:
                    return 1 - 0.035714 * distance
                elif 8 <= distance <= 11:
                    return 0.75 * math.exp(-1.106 * (distance - 7))
                else:
                    return 0
            
            # Create dictionaries for easy lookup
            user_dict = {trait.name: trait.ranking for trait in user_traits}
            ideal_dict = {trait.name: trait.ranking for trait in ideal_traits}
            
            total_weight = 0
            total_traits = 0
            
            # Calculate weights for each trait
            for trait_name in user_dict.keys():
                if trait_name in ideal_dict:
                    distance = abs(user_dict[trait_name] - ideal_dict[trait_name])
                    weight = weight_function(distance)
                    total_weight += weight
                    total_traits += 1
            
            # Calculate match percentage
            if total_traits > 0:
                match_score = (total_weight / total_traits) * 100
                return round(match_score, 2)
            else:
                return 0.0
                
        except Exception as e:
            raise Exception(f"Failed to calculate match score: {str(e)}")

import requests
import json
from typing import List, Dict, Any
import asyncio
import aiohttp
from datetime import datetime
import random
import os
from dotenv import load_dotenv
from .ai_prompts_service import (
    get_system_prompt, 
    get_chapter_2_generation_prompt,
    get_chapter_3_generation_prompt,
    CLIFTON_STRENGTHS,
    get_all_strengths,
    validate_strength_profile,
    PRIMING_1_IDENTITY,
    PRIMING_2_METHODOLOGY,
    PRIMING_3_OVERVIEW
)

# Load environment variables from root directory
load_dotenv('../.env')

class GroqAIService:
    """
    Enhanced FREE AI service using Groq API with CliftonStrengths priming
    Requires free API key from https://console.groq.com/
    Much faster and more reliable than HuggingFace
    """
    
    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            print("Warning: GROQ_API_KEY not found. Get free API key from https://console.groq.com/")
        
        # Groq API configuration
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"  # Most reliable supported model
        
        # Use the complete 34 CliftonStrengths from ai_prompts_service
        self.clifton_strengths = CLIFTON_STRENGTHS
        self.all_traits = get_all_strengths()
        
        # System prompt with CliftonStrengths priming
        self.system_prompt = get_system_prompt()
        
    def _make_api_call(self, messages: List[Dict[str, str]], max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Make a call to Groq API
        """
        if not self.api_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                print(f"Groq API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return None
    
    async def analyze_initial_responses(self, responses: List[Dict[str, Any]], 
                                     questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analyze initial responses using AI to create trait rankings
        """
        try:
            if not self.api_key:
                return self._generate_fallback_rankings()
            
            # Create a comprehensive analysis prompt
            response_text = ""
            for i, response in enumerate(responses):
                question_id = response.get('questionId', '')
                answer = response.get('response', '')
                
                # Find the corresponding question
                question = None
                for q in questions:
                    if q.get('QuestionID') == question_id or q.get('Prompt') == question_id:
                        question = q
                        break
                
                if question:
                    response_text += f"Question {i+1}: {question.get('Prompt', '')}\n"
                    response_text += f"Answer: {answer}\n\n"
            
            # AI analysis prompt
            messages = [
                {
                    "role": "system",
                    "content": """You are a strengths assessment expert. Analyze responses and rank the 34 core strengths from 1 (strongest) to 34 (weakest). 

IMPORTANT: Return ONLY a valid JSON object with ALL 34 traits ranked. No other text.

The 34 traits are: Achiever, Activator, Adaptability, Analytical, Arranger, Belief, Command, Communication, Competition, Connectedness, Consistency, Context, Deliberative, Developer, Discipline, Empathy, Focus, Futuristic, Harmony, Ideation, Includer, Individualization, Input, Intellection, Learner, Maximizer, Positivity, Relator, Responsibility, Restorative, Self-Assurance, Significance, Strategic, Woo.

Format: {"Achiever": 1, "Activator": 2, ...}"""
                },
                {
                    "role": "user", 
                    "content": f"Analyze these responses and return a JSON ranking of all 34 traits:\n\n{response_text}\n\nReturn only the JSON object."
                }
            ]
            
            ai_response = self._make_api_call(messages, max_tokens=1000, temperature=0.3)
            
            print(f"AI Response for trait analysis: {ai_response[:1000]}...")  # Debug log - show more
            
            if ai_response:
                try:
                    # Extract JSON from the response
                    import re
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        json_text = json_match.group()
                        print(f"DEBUG: Extracted JSON: {json_text[:500]}...")  # Debug the JSON
                        trait_rankings = json.loads(json_text)
                        print(f"Parsed trait rankings: {len(trait_rankings)} traits found")  # Debug log
                        
                        # Validate that we have rankings for all traits and they're not all sequential
                        if len(trait_rankings) >= 30:  # At least most traits
                            # Check if rankings are actually varied (not just 1,2,3,4...)
                            values = list(trait_rankings.values())
                            unique_values = len(set(values))
                            print(f"DEBUG: Found {unique_values} unique ranking values out of {len(values)} total")
                            
                            # Check if it's sequential (1,2,3,4... pattern)
                            sorted_values = sorted(values)
                            is_sequential = sorted_values == list(range(1, len(sorted_values) + 1))
                            print(f"DEBUG: Is sequential pattern: {is_sequential}")
                            
                            if not is_sequential and unique_values > 10:  # At least 10 different ranking values
                                print(f"DEBUG: AI rankings look valid, using them")
                                return trait_rankings
                            else:
                                print(f"DEBUG: AI rankings look sequential/invalid, using fallback")
                
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")  # Debug log
                    print(f"DEBUG: Failed to parse: {json_text[:200] if 'json_text' in locals() else 'No JSON text'}")
                    pass
            
            # Fallback if AI analysis fails
            print(f"DEBUG: Using fallback rankings due to AI analysis failure")
            return self._generate_fallback_rankings()
            
        except Exception as e:
            print(f"Error in analyze_initial_responses: {e}")
            return self._generate_fallback_rankings()
    
    def _generate_fallback_rankings(self) -> Dict[str, int]:
        """Generate realistic fallback rankings"""
        traits = list(self.all_traits)
        random.shuffle(traits)
        return {trait: i + 1 for i, trait in enumerate(traits)}
    
    async def generate_follow_up_questions(self, user_id: str, round_num: int,
                                         previous_responses: List[Dict[str, Any]],
                                         trait_rankings: Dict[str, int]) -> List[Dict[str, Any]]:
        """
        Generate follow-up questions using AI
        """
        try:
            print(f"DEBUG: Generating follow-up questions for user {user_id}, round {round_num}")
            print(f"DEBUG: API key available: {bool(self.api_key)}")
            print(f"DEBUG: Previous responses count: {len(previous_responses)}")
            print(f"DEBUG: Trait rankings: {trait_rankings}")
            
            if not self.api_key:
                print("DEBUG: No API key - using fallback questions")
                return self._generate_fallback_questions(user_id, round_num)
            
            if round_num == 1:
                return await self._generate_chapter_2_questions(user_id, trait_rankings)
            else:
                return await self._generate_chapter_3_questions(user_id, trait_rankings)
            
        except Exception as e:
            print(f"Error generating follow-up questions: {e}")
            return self._generate_fallback_questions(user_id, round_num)
    
    async def _generate_chapter_2_questions(self, user_id: str, trait_rankings: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate Chapter 2 situational questions"""
        try:
            print(f"DEBUG: Generating Chapter 2 questions for user {user_id}")
            # Get top traits
            top_traits = sorted(trait_rankings.items(), key=lambda x: x[1])[:8]
            top_trait_names = [trait[0] for trait in top_traits]
            print(f"DEBUG: Top traits for Chapter 2: {top_trait_names}")
            
            prompt = get_chapter_2_generation_prompt(top_trait_names)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            print(f"DEBUG: Making API call for Chapter 2...")
            ai_response = self._make_api_call(messages, max_tokens=2000, temperature=0.8)
            print(f"DEBUG: API response length: {len(ai_response) if ai_response else 0}")
            
            if ai_response:
                try:
                    # Parse the AI response to extract questions
                    import re
                    json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
                    if json_match:
                        questions = json.loads(json_match.group())
                        print(f"DEBUG: Successfully parsed {len(questions)} questions from AI")
                        if len(questions) >= 8:
                            return questions[:12]  # Take first 12
                except json.JSONDecodeError as je:
                    print(f"DEBUG: JSON decode error: {je}")
            
            print("DEBUG: AI generation failed, using fallback questions")
            return self._generate_fallback_questions(user_id, 1)
            
        except Exception as e:
            print(f"Error generating Chapter 2 questions: {e}")
            return self._generate_fallback_questions(user_id, 1)
    
    async def _generate_chapter_3_questions(self, user_id: str, trait_rankings: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate Chapter 3 open-ended questions"""
        try:
            print(f"DEBUG: Generating Chapter 3 questions for user {user_id}")
            # Get top traits
            top_traits = sorted(trait_rankings.items(), key=lambda x: x[1])[:5]
            top_trait_names = [trait[0] for trait in top_traits]
            print(f"DEBUG: Top traits for Chapter 3: {top_trait_names}")
            
            # For Chapter 3, we need chapter 2 results, but we can use trait rankings as proxy
            chapter_1_results = f"Top traits from initial assessment: {', '.join(top_trait_names)}"
            chapter_2_results = f"User trait rankings: {trait_rankings}"
            
            prompt = get_chapter_3_generation_prompt(chapter_1_results, chapter_2_results)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            print(f"DEBUG: Making API call for Chapter 3...")
            ai_response = self._make_api_call(messages, max_tokens=1500, temperature=0.8)
            print(f"DEBUG: API response length: {len(ai_response) if ai_response else 0}")
            
            if ai_response:
                try:
                    # Parse the AI response to extract questions
                    import re
                    json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
                    if json_match:
                        questions = json.loads(json_match.group())
                        print(f"DEBUG: Successfully parsed {len(questions)} questions from AI")
                        if len(questions) >= 4:
                            return questions[:7]  # Take first 7
                except json.JSONDecodeError as je:
                    print(f"DEBUG: JSON decode error in Chapter 3: {je}")
            
            print("DEBUG: Chapter 3 AI generation failed, using fallback questions")
            return self._generate_fallback_questions(user_id, 2)
            
            return self._generate_fallback_questions(user_id, 2)
            
        except Exception as e:
            print(f"Error generating Chapter 3 questions: {e}")
            return self._generate_fallback_questions(user_id, 2)
    
    def _generate_fallback_questions(self, user_id: str, round_num: int) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI fails"""
        if round_num == 1:
            # Chapter 2 fallback questions
            return [
                {
                    "QuestionID": f"C2_FB_1",
                    "Prompt": "When facing a challenging deadline, what's your first instinct?",
                    "Type": "multiple_choice",
                    "Option1": "Break it down into smaller tasks",
                    "Option2": "Rally the team for support", 
                    "Option3": "Focus intensely and push through",
                    "Option4": "Ask for guidance or extension"
                },
                {
                    "QuestionID": f"C2_FB_2",
                    "Prompt": "In a team meeting when there's disagreement, you typically:",
                    "Type": "multiple_choice",
                    "Option1": "Listen to all perspectives first",
                    "Option2": "Present your solution clearly", 
                    "Option3": "Find common ground between views",
                    "Option4": "Suggest taking time to think it over"
                },
                {
                    "QuestionID": f"C2_FB_3",
                    "Prompt": "When starting a new project, your natural approach is to:",
                    "Type": "multiple_choice",
                    "Option1": "Research and gather information",
                    "Option2": "Jump in and start experimenting", 
                    "Option3": "Plan out each step carefully",
                    "Option4": "Connect with others who've done similar work"
                }
            ]
        else:
            # Chapter 3 fallback questions
            return [
                {
                    "QuestionID": f"C3_FB_1",
                    "Prompt": "Describe a time when you had to adapt quickly to unexpected changes. How did you handle it and what did you learn?",
                    "Type": "open_ended"
                },
                {
                    "QuestionID": f"C3_FB_2", 
                    "Prompt": "Tell me about a project where you took initiative. What motivated you and what was the outcome?",
                    "Type": "open_ended"
                },
                {
                    "QuestionID": f"C3_FB_3",
                    "Prompt": "How do you typically approach building relationships with new team members or colleagues?",
                    "Type": "open_ended"
                },
                {
                    "QuestionID": f"C3_FB_4",
                    "Prompt": "What energizes you most at work and how do you seek out these opportunities?",
                    "Type": "open_ended"
                },
                {
                    "QuestionID": f"C3_FB_5",
                    "Prompt": "Describe your approach to solving complex problems. Walk me through your process.",
                    "Type": "open_ended"
                }
            ]
    
    async def generate_summary(self, user_id: str, all_responses: List[Dict[str, Any]], 
                             trait_rankings: Dict[str, int], summary_type: str = "initial") -> str:
        """Generate AI-powered personality summary"""
        try:
            if not self.api_key:
                return self._generate_fallback_summary(summary_type)
            
            # Ensure trait_rankings is a dictionary
            if not isinstance(trait_rankings, dict):
                print(f"Warning: trait_rankings is not a dict, got {type(trait_rankings)}")
                return self._generate_fallback_summary(summary_type)
            
            # Get top 5 traits
            if trait_rankings:
                top_traits = sorted(trait_rankings.items(), key=lambda x: x[1], reverse=True)[:5]
                top_trait_names = [trait[0] for trait in top_traits]
            else:
                top_trait_names = ["Analytical", "Strategic", "Communication", "Adaptability", "Innovation"]
            
            # Create comprehensive context
            context = f"Top 5 Strengths: {', '.join(top_trait_names)}\n"
            context += f"Total responses analyzed: {len(all_responses)}\n"
            
            if summary_type == "final":
                prompt = f"""Create a final personality assessment summary based on:

{context}

Write a concise 3-4 sentence summary that:
1. Starts with "You are a..."
2. Describes their key strengths and traits
3. Mentions how they work and lead

Format: "You are a [description]. You showed... Your strengths include... This makes you..."

Keep it personal, concise, and professionally valuable."""
            else:
                prompt = f"""Create an initial personality summary based on:

{context}

Write a brief 3-4 sentence summary that:
1. Starts with "You are a..."
2. Introduces their emerging strengths
3. Sets up anticipation for deeper analysis

Format: "You are a [description]. You showed... Your responses indicate... We'll explore..."

Keep it engaging, encouraging, and concise."""
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            ai_response = self._make_api_call(messages, max_tokens=800, temperature=0.7)
            
            if ai_response and len(ai_response.strip()) > 100:
                return ai_response.strip()
            
            return self._generate_fallback_summary(summary_type)
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return self._generate_fallback_summary(summary_type)
    
    def _generate_fallback_summary(self, summary_type: str) -> str:
        """Generate fallback summary when AI fails"""
        if summary_type == "final":
            return """You are a strategic thinker with strong relationship-building abilities. You showed natural talent in both analytical problem-solving and team collaboration. Your strengths work together to create a powerful foundation for leadership roles. This combination positions you excellently for roles requiring both strategic insight and interpersonal excellence."""
        else:
            return """You are a well-rounded professional with emerging patterns across multiple strength domains. You showed strong indicators in both analytical thinking and interpersonal awareness. Your responses indicate someone who brings depth and collaboration to their work. We'll explore these emerging strengths more deeply in the following sections."""

    async def update_trait_rankings(self, current_rankings: Dict[str, int],
                                  new_responses: List[Dict[str, Any]],
                                  round_num: int) -> Dict[str, int]:
        """Update trait rankings based on new follow-up responses"""
        try:
            if round_num == 1:
                # Chapter 2: Process dual-choice responses (round 1)
                analysis_prompt = self._create_dual_choice_analysis_prompt(new_responses, current_rankings)
            else:
                # Chapter 3: Process text responses (round 2)
                analysis_prompt = self._create_text_response_analysis_prompt(new_responses, current_rankings)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = self._make_api_call(messages, max_tokens=800, temperature=0.3)
            
            # Parse the response to extract updated rankings
            updated_rankings = self._parse_ranking_response(response, current_rankings)
            return updated_rankings
            
        except Exception as e:
            print(f"Error updating trait rankings: {e}")
            return current_rankings
    
    def _create_dual_choice_analysis_prompt(self, responses: List[Dict[str, Any]], 
                                          current_rankings: Dict[str, int]) -> str:
        """Create prompt for analyzing dual-choice responses from Chapter 2"""
        response_text = ""
        for resp in responses:
            first_choice = resp.get('firstChoice', '')
            second_choice = resp.get('secondChoice', '')
            response_text += f"First choice (emotional truth): {first_choice}\n"
            response_text += f"Second choice (practical/expected): {second_choice}\n\n"
        
        return f"""
        Analyze these dual-choice responses from Chapter 2 (situational assessment) and update the CliftonStrengths rankings.
        
        Current rankings: {current_rankings}
        
        Dual-choice responses:
        {response_text}
        
        The first choice represents emotional truth (immediate reaction), the second choice represents practical/expected response.
        Weight the first choice more heavily as it reveals authentic strengths patterns.
        
        Return updated rankings as a JSON object with strength names as keys and ranking scores (1-100) as values.
        Focus on the top 10-15 strengths that show the strongest evidence.
        """
    
    def _create_text_response_analysis_prompt(self, responses: List[Dict[str, Any]], 
                                            current_rankings: Dict[str, int]) -> str:
        """Create prompt for analyzing text responses from Chapter 3"""
        response_text = ""
        for resp in responses:
            response_content = resp.get('response', '')
            response_text += f"Response: {response_content}\n\n"
        
        return f"""
        Analyze these detailed text responses from Chapter 3 (depth assessment) and update the CliftonStrengths rankings.
        
        Current rankings: {current_rankings}
        
        Text responses:
        {response_text}
        
        These responses provide deeper insight into how the person demonstrates their strengths through stories and examples.
        Look for concrete evidence of strengths in action.
        
        Return updated rankings as a JSON object with strength names as keys and ranking scores (1-100) as values.
        Focus on the top 10-15 strengths that show the strongest evidence.
        """
    
    def _parse_ranking_response(self, response: str, fallback_rankings: Dict[str, int]) -> Dict[str, int]:
        """Parse AI response to extract trait rankings"""
        try:
            # Try to find JSON in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                rankings = json.loads(json_str)
                
                # Validate rankings
                if isinstance(rankings, dict) and all(isinstance(v, (int, float)) for v in rankings.values()):
                    return {k: int(v) for k, v in rankings.items()}
            
            return fallback_rankings
            
        except Exception as e:
            print(f"Error parsing rankings: {e}")
            return fallback_rankings

# Create an instance for compatibility
groq_service = GroqAIService()

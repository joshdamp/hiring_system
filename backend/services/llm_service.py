import os
from typing import List, Dict, Any
import json
from datetime import datetime
from .ai_prompts_service import (
    get_system_prompt, 
    get_chapter_2_generation_prompt,
    get_chapter_3_generation_prompt,
    CLIFTON_STRENGTHS,
    get_all_strengths,
    validate_strength_profile
)
from .groq_ai_service import GroqAIService

class LLMService:
    def __init__(self):
        """Initialize with Groq AI service and CliftonStrengths priming"""
        self.ai_service = GroqAIService()
        
        # Use the complete 34 CliftonStrengths from ai_prompts_service
        self.traits = get_all_strengths()
        self.clifton_domains = CLIFTON_STRENGTHS
        
        # System prompt with priming
        self.system_prompt = get_system_prompt()
    
    def _initialize_client(self):
        """No longer needed - using Groq free service"""
        pass
    
    async def analyze_initial_responses(self, responses: List[Dict[str, Any]], 
                                     questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze Chapter 1 responses and create baseline trait rankings using CliftonStrengths priming"""
        try:
            # Use Hugging Face AI service for analysis
            trait_rankings = await self.ai_service.analyze_initial_responses(responses, questions)
            
            # Validate the rankings contain all 34 unique strengths
            if trait_rankings:
                strength_list = sorted(trait_rankings.keys(), key=lambda x: trait_rankings[x])
                is_valid, message = validate_strength_profile(strength_list)
                
                if not is_valid:
                    print(f"Warning: Invalid strength profile generated - {message}")
                    return self._generate_mock_trait_rankings()
            
            return trait_rankings or self._generate_mock_trait_rankings()
            
        except Exception as e:
            print(f"Error in analyze_initial_responses: {e}")
            return self._generate_mock_trait_rankings()
    
    async def generate_follow_up_questions(self, user_id: str, round_num: int,
                                         previous_responses: List[Dict[str, Any]],
                                         trait_rankings: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate Chapter 2 or Chapter 3 questions based on previous responses and CliftonStrengths methodology"""
        try:
            # Use Hugging Face AI service for question generation
            questions = await self.ai_service.generate_follow_up_questions(
                user_id, round_num, previous_responses, trait_rankings
            )
            
            if not questions:
                return self._generate_mock_follow_up_questions(round_num)
            
            return questions
            
        except Exception as e:
            print(f"Error in generate_follow_up_questions: {e}")
            return self._generate_mock_follow_up_questions(round_num)
    
    async def generate_summary(self, user_responses: Dict[str, List[Dict[str, Any]]], 
                             trait_rankings: Dict[str, int], 
                             summary_type: str) -> str:
        """Generate personality summary based on responses and trait rankings"""
        try:
            # Use Hugging Face AI service for summary generation
            summary = await self.ai_service.generate_summary(user_responses, trait_rankings, summary_type)
            return summary or self._generate_mock_summary(summary_type)
            
        except Exception as e:
            print(f"Error in generate_summary: {e}")
            return self._generate_mock_summary(summary_type)
    
    async def update_trait_rankings(self, current_rankings: Dict[str, int],
                                  new_responses: List[Dict[str, Any]],
                                  round_num: int) -> Dict[str, int]:
        """Update trait rankings based on new follow-up responses"""
        try:
            # Use Hugging Face AI service for trait ranking updates
            updated_rankings = await self.ai_service.update_trait_rankings(
                current_rankings, new_responses, round_num
            )
            return updated_rankings or self._update_mock_trait_rankings(current_rankings)
            
        except Exception as e:
            print(f"Error in update_trait_rankings: {e}")
            return self._update_mock_trait_rankings(current_rankings)
    
    # Helper methods for mock data (used when AI service is unavailable)
    
    def _create_chapter_1_analysis_prompt(self, responses: List[Dict[str, Any]], 
                                         questions: List[Dict[str, Any]]) -> str:
        """Create prompt for Chapter 1 (foundational) response analysis"""
        prompt = f"""
        Analyze these Chapter 1 foundational Likert scale responses to establish baseline CliftonStrengths rankings.
        
        The user responded to side-by-side statements on a 1-5 scale:
        1 = Strongly favor left statement (Statement A)
        2 = Somewhat favor left statement  
        3 = Neutral
        4 = Somewhat favor right statement (Statement B)
        5 = Strongly favor right statement
        
        Questions and Responses:
        """
        
        for response in responses:
            question = next((q for q in questions if q['QuestionID'] == response['questionId']), None)
            if question:
                prompt += f"""
                Question {question['QuestionID']} (Theme: {question.get('Theme', 'Unknown')}):
                Left: "{question['LeftStatement']}"
                Right: "{question['RightStatement']}"
                Response: {response['response']} (User preference)
                """
        
        prompt += f"""
        
        Based on these responses, rank all 34 CliftonStrengths from 1 (strongest) to 34 (weakest).
        
        All 34 CliftonStrengths to rank:
        {', '.join(self.traits)}
        
        Consider the user's current self (not aspirational) and subconscious patterns.
        
        Provide rankings in JSON format:
        {{"Analytical": 1, "Strategic": 2, "Achiever": 3, ...}}
        """
        
        return prompt
    
    def _create_chapter_2_prompt(self, previous_responses: List[Dict[str, Any]],
                                trait_rankings: Dict[str, int]) -> str:
        """Create prompt for Chapter 2 question generation (Emotional truth)"""
        top_10_traits = sorted(trait_rankings.items(), key=lambda x: x[1])[:10]
        
        prompt = get_chapter_2_generation_prompt({
            'top_traits': [trait[0] for trait in top_10_traits],
            'rankings': trait_rankings
        })
        
        prompt += f"""
        
        Current top 10 traits from Chapter 1: {[trait[0] for trait in top_10_traits]}
        
        Generate exactly 13 situational questions. Each question should:
        1. Present a specific, realistic scenario
        2. Offer 4 distinct choices (A, B, C, D)
        3. Each choice should clearly represent different CliftonStrengths traits
        4. Avoid vague scenarios that could apply to multiple traits
        5. Focus on revealing how the user actually responds, not how they think they should respond
        
        Format:
        Question 1: [Specific scenario description]
        A. [Choice reflecting specific trait(s)]
        B. [Choice reflecting different trait(s)]  
        C. [Choice reflecting different trait(s)]
        D. [Choice reflecting different trait(s)]
        Traits tested: A([trait names]) B([trait names]) C([trait names]) D([trait names])
        
        [Continue for all 13 questions]
        """
        
        return prompt
    
    def _create_chapter_3_prompt(self, previous_responses: List[Dict[str, Any]],
                                trait_rankings: Dict[str, int]) -> str:
        """Create prompt for Chapter 3 question generation (Story & Demonstration)"""
        top_5_traits = sorted(trait_rankings.items(), key=lambda x: x[1])[:5]
        
        prompt = get_chapter_3_generation_prompt(
            {'top_traits': [trait[0] for trait in top_5_traits]},
            {'refined_insights': 'from_chapter_2'}
        )
        
        prompt += f"""
        
        Current top 5 traits: {[trait[0] for trait in top_5_traits]}
        
        Generate exactly 7 in-depth perception questions that focus on:
        - How the user perceives and processes feedback
        - What brings them happiness and fulfillment
        - How they handle stress and pressure
        - What motivates them intrinsically
        - How they view success and achievement
        - Their relationship with learning and growth
        - Their ideal work environment and team dynamics
        
        Each question should:
        1. Be open-ended and require thoughtful reflection
        2. Reveal deep perception patterns
        3. Help resolve any contradictions from previous chapters
        4. Avoid leading questions or obvious answers
        5. Focus on current reality, not aspirations
        
        Format:
        Question 1: [Deep, perception-focused question]
        Purpose: [What this reveals about CliftonStrengths]
        
        [Continue for all 7 questions]
        """
        
        return prompt
    
    def _create_follow_up_prompt(self, previous_responses: List[Dict[str, Any]],
                               trait_rankings: Dict[str, int], round_num: int,
                               num_questions: int) -> str:
        """Create prompt for follow-up question generation"""
        top_traits = sorted(trait_rankings.items(), key=lambda x: x[1])[:5]
        
        prompt = f"""
        Based on the user's assessment responses and current trait rankings, generate {num_questions} 
        personalized follow-up questions for round {round_num}.
        
        Top 5 traits (strongest): {[trait[0] for trait in top_traits]}
        
        Requirements:
        - Questions should be open-ended and require detailed responses
        - Focus on clarifying and refining the understanding of top traits
        - Make questions conversational and engaging
        - Each question should help distinguish between similar traits
        
        Format each question as:
        Question 1: [question text]
        Question 2: [question text]
        ...
        """
        
        return prompt
    
    def _create_summary_prompt(self, user_responses: Dict[str, List[Dict[str, Any]]],
                             trait_rankings: Dict[str, int], summary_type: str) -> str:
        """Create prompt for summary generation"""
        top_5_traits = sorted(trait_rankings.items(), key=lambda x: x[1])[:5]
        
        if summary_type == "initial":
            length = "2-3 sentences"
            focus = "general personality tendencies"
        elif summary_type == "follow_up":
            length = "3-4 sentences"
            focus = "refined personality insights and working style"
        else:  # final
            length = "4-5 sentences"
            focus = "comprehensive personality profile with professional strengths"
        
        prompt = f"""
        Create a {summary_type} personality summary ({length}) focusing on {focus}.
        
        Top 5 traits: {[f"{trait[0]} (rank {trait[1]})" for trait in top_5_traits]}
        
        Requirements:
        - Be positive and encouraging
        - Focus on professional strengths and capabilities
        - Use engaging, human language
        - Avoid psychological jargon
        - Make it feel personalized and insightful
        """
        
        return prompt
    
    def _create_trait_update_prompt(self, current_rankings: Dict[str, int],
                                  new_responses: List[Dict[str, Any]], 
                                  round_num: int) -> str:
        """Create prompt for updating trait rankings"""
        prompt = f"""
        Update the personality trait rankings based on these new round {round_num} responses:
        
        Current rankings: {json.dumps(current_rankings, indent=2)}
        
        New responses:
        """
        
        for i, response in enumerate(new_responses, 1):
            prompt += f"\nQ{i}: {response.get('response', 'No response')}\n"
        
        prompt += """
        
        Provide updated rankings in JSON format, considering how the new responses 
        refine or change your understanding of the user's personality traits.
        """
        
        return prompt
    
    def _parse_trait_rankings(self, response: str) -> Dict[str, int]:
        """Parse trait rankings from LLM response"""
        try:
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                rankings = json.loads(json_str)
                return rankings
        except:
            pass
        
        # Fallback to mock rankings
        return self._generate_mock_trait_rankings()
    
    def _parse_follow_up_questions(self, response: str, user_id: str, 
                                 round_num: int, num_questions: int) -> List[Dict[str, Any]]:
        """Parse follow-up questions from LLM response"""
        try:
            questions = []
            lines = response.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip().startswith(('Question', 'Q')) and ':' in line:
                    question_text = line.split(':', 1)[1].strip()
                    if question_text:
                        questions.append({
                            'QuestionID': f"{user_id}_R{round_num}_Q{len(questions)+1}",
                            'QuestionText': question_text,
                            'QuestionType': 'chapter_2' if round_num == 1 else 'chapter_3'
                        })
            
            # If parsing failed or not enough questions, return mock questions
            if len(questions) < num_questions:
                return self._generate_mock_follow_up_questions(round_num)
            
            return questions[:num_questions]  # Ensure exact number
            
        except Exception as e:
            print(f"Error parsing questions: {e}")
            return self._generate_mock_follow_up_questions(round_num)
    
    def _generate_mock_trait_rankings(self) -> Dict[str, int]:
        """Generate mock trait rankings for development"""
        import random
        traits_copy = self.traits.copy()
        random.shuffle(traits_copy)
        
        rankings = {}
        for i, trait in enumerate(traits_copy):
            rankings[trait] = i + 1
        
        return rankings
    
    def _update_mock_trait_rankings(self, current_rankings: Dict[str, int]) -> Dict[str, int]:
        """Update mock trait rankings"""
        # Slightly modify some rankings
        import random
        updated = current_rankings.copy()
        
        # Randomly adjust 5-10 rankings by ±1-3 positions
        traits_to_adjust = random.sample(list(updated.keys()), min(8, len(updated)))
        
        for trait in traits_to_adjust:
            adjustment = random.randint(-3, 3)
            new_rank = max(1, min(34, updated[trait] + adjustment))
            updated[trait] = new_rank
        
        return updated
    
    def _generate_mock_follow_up_questions(self, round_num: int) -> List[Dict[str, Any]]:
        """Generate mock follow-up questions based on chapter structure"""
        if round_num == 1:
            # Chapter 2: Emotional truth - 13 situational questions
            return [
                {
                    'QuestionID': f"mock_ch2_q{i+1}",
                    'QuestionText': f"Mock Chapter 2 situational question {i+1}: You're leading a project that's behind schedule. What's your first instinct?",
                    'QuestionType': 'chapter_2',
                    'Options': [
                        "A. Create a detailed recovery plan with clear milestones",
                        "B. Rally the team with motivational communication", 
                        "C. Analyze what went wrong to prevent future issues",
                        "D. Take personal responsibility and work extra hours"
                    ]
                }
                for i in range(13)
            ]
        else:
            # Chapter 3: Story & Demonstration - 7 perception questions  
            return [
                {
                    'QuestionID': f"mock_ch3_q{i+1}",
                    'QuestionText': f"Mock Chapter 3 perception question {i+1}: How do you typically process constructive feedback from colleagues?",
                    'QuestionType': 'chapter_3'
                }
                for i in range(7)
            ]
    
    def _generate_mock_summary(self, summary_type: str) -> str:
        """Generate mock personality summary based on CliftonStrengths"""
        summaries = {
            "initial": "Based on your Chapter 1 responses, you demonstrate strong strategic thinking patterns with a natural inclination toward executing on important goals. Your responses suggest balanced preferences across the four CliftonStrengths domains.",
            
            "follow_up": "Your Chapter 2 responses reveal someone who leads with strategic thinking while maintaining strong relationship-building capabilities. You show natural influencing abilities and consistent execution patterns, indicating a well-rounded strength profile.",
            
            "final": "Your comprehensive assessment reveals a unique CliftonStrengths profile combining strategic thinking with authentic relationship building. You demonstrate natural abilities in both analytical problem-solving and team collaboration, making you well-suited for leadership roles that require both strategic vision and interpersonal excellence. Your top strengths likely include domains of Strategic Thinking and Relationship Building, with supporting strengths in Executing and Influencing that complement your natural talents."
        }
        
        return summaries.get(summary_type, summaries["final"])

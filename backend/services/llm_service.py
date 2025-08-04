import openai
import os
from typing import List, Dict, Any
import json
from datetime import datetime

class LLMService:
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = None
        self.model = "gpt-3.5-turbo"
        self._initialize_client()
        
        # Define the 34 traits for analysis
        self.traits = [
            "Strategic", "Activator", "Command", "Significance", "Futuristic",
            "Individualization", "Maximizer", "Competition", "Self-Assurance", "Ideation",
            "Focus", "Communication", "Input", "Achiever", "Learner",
            "Responsibility", "Restorative", "Analytical", "Arranger", "Developer",
            "Intellection", "Empathy", "Belief", "Relator", "Adaptability",
            "Positivity", "Connectedness", "Context", "Woo", "Discipline",
            "Deliberative", "Includer", "Harmony", "Consistency"
        ]
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
                self.client = openai
            else:
                self.client = None
        except Exception as e:
            self.client = None
    
    async def analyze_initial_responses(self, responses: List[Dict[str, Any]], 
                                     questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze initial responses and create baseline trait rankings"""
        try:
            if not self.client:
                return self._generate_mock_trait_rankings()
            
            # Create prompt for analysis
            prompt = self._create_initial_analysis_prompt(responses, questions)
            
            response = await self._call_openai(prompt, "trait_analysis")
            
            # Parse response to get trait rankings
            trait_rankings = self._parse_trait_rankings(response)
            return trait_rankings
            
        except Exception as e:
            return self._generate_mock_trait_rankings()
    
    async def generate_follow_up_questions(self, user_id: str, round_num: int,
                                         previous_responses: List[Dict[str, Any]],
                                         trait_rankings: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate personalized follow-up questions based on previous responses"""
        try:
            if not self.client:
                return self._generate_mock_follow_up_questions(round_num)
            
            num_questions = 12 if round_num == 1 else 4
            prompt = self._create_follow_up_prompt(previous_responses, trait_rankings, 
                                                 round_num, num_questions)
            
            response = await self._call_openai(prompt, "question_generation")
            
            # Parse response to get questions
            questions = self._parse_follow_up_questions(response, user_id, round_num)
            return questions
            
        except Exception as e:
            return self._generate_mock_follow_up_questions(round_num)
    
    async def generate_summary(self, user_responses: Dict[str, List[Dict[str, Any]]], 
                             trait_rankings: Dict[str, int], 
                             summary_type: str) -> str:
        """Generate personality summary based on responses and trait rankings"""
        try:
            if not self.client:
                return self._generate_mock_summary(summary_type)
            
            prompt = self._create_summary_prompt(user_responses, trait_rankings, summary_type)
            
            response = await self._call_openai(prompt, "summary_generation")
            return response.strip()
            
        except Exception as e:
            return self._generate_mock_summary(summary_type)
    
    async def update_trait_rankings(self, current_rankings: Dict[str, int],
                                  new_responses: List[Dict[str, Any]],
                                  round_num: int) -> Dict[str, int]:
        """Update trait rankings based on new follow-up responses"""
        try:
            if not self.client:
                return self._update_mock_trait_rankings(current_rankings)
            
            prompt = self._create_trait_update_prompt(current_rankings, new_responses, round_num)
            
            response = await self._call_openai(prompt, "trait_update")
            
            # Parse updated rankings
            updated_rankings = self._parse_trait_rankings(response)
            return updated_rankings
            
        except Exception as e:
            return current_rankings
    
    async def _call_openai(self, prompt: str, task_type: str) -> str:
        """Make API call to OpenAI"""
        try:
            response = await self.client.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(task_type)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return ""
    
    def _get_system_prompt(self, task_type: str) -> str:
        """Get system prompt based on task type"""
        if task_type == "trait_analysis":
            return """You are an expert psychologist specializing in personality assessment. 
            Analyze the given responses and rank 34 personality traits from 1 (strongest) to 34 (weakest).
            Focus on evidence-based analysis and provide rankings in JSON format."""
        
        elif task_type == "question_generation":
            return """You are an expert in creating personalized psychometric assessment questions.
            Generate insightful, specific questions that will help refine personality trait understanding.
            Make questions conversational yet professional."""
        
        elif task_type == "summary_generation":
            return """You are an expert career counselor and personality analyst.
            Create engaging, positive, and insightful personality summaries that highlight strengths
            and professional qualities. Be encouraging while being accurate."""
        
        elif task_type == "trait_update":
            return """You are an expert psychologist updating personality trait rankings.
            Analyze new responses and adjust previous rankings accordingly.
            Provide updated rankings in JSON format."""
        
        return "You are a helpful AI assistant specializing in personality assessment."
    
    def _create_initial_analysis_prompt(self, responses: List[Dict[str, Any]], 
                                      questions: List[Dict[str, Any]]) -> str:
        """Create prompt for initial response analysis"""
        prompt = f"""
        Analyze the following psychometric assessment responses and rank these 34 personality traits 
        from 1 (strongest) to 34 (weakest):
        
        Traits to rank: {', '.join(self.traits)}
        
        Responses:
        """
        
        for response in responses:
            question_text = next((q['Prompt'] for q in questions 
                               if q['QuestionID'] == response['questionId']), "Unknown")
            prompt += f"\nQ: {question_text}\nResponse: Option {response['response']}\n"
        
        prompt += """
        
        Provide rankings in JSON format:
        {"Strategic": 1, "Activator": 2, ...}
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
                                 round_num: int) -> List[Dict[str, Any]]:
        """Parse follow-up questions from LLM response"""
        try:
            questions = []
            lines = response.split('\n')
            
            for i, line in enumerate(lines):
                if line.strip().startswith(('Question', 'Q')) and ':' in line:
                    question_text = line.split(':', 1)[1].strip()
                    if question_text:
                        questions.append({
                            'QuestionID': f"{user_id}_R{round_num}_Q{i+1}",
                            'QuestionText': question_text
                        })
            
            # If parsing failed, return mock questions
            if not questions:
                return self._generate_mock_follow_up_questions(round_num)
            
            return questions
            
        except Exception as e:
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
        """Generate mock follow-up questions"""
        num_questions = 12 if round_num == 1 else 4
        
        questions = [
            "Describe a time when you had to lead a team through a challenging situation. What was your approach?",
            "How do you typically handle competing priorities and tight deadlines?",
            "Tell me about a project where you had to learn something completely new. How did you approach it?",
            "Describe your ideal work environment and what makes you most productive.",
            "How do you prefer to receive feedback, and how do you typically respond to constructive criticism?",
            "Tell me about a time when you had to persuade others to see your point of view.",
            "How do you maintain relationships with colleagues and what role do you typically play in team dynamics?",
            "Describe a situation where you had to adapt quickly to unexpected changes.",
            "What motivates you most in your work, and how do you maintain that motivation?",
            "How do you approach problem-solving when faced with complex or ambiguous challenges?",
            "Tell me about your communication style and how you adapt it for different audiences.",
            "Describe how you balance attention to detail with meeting deadlines and broader objectives."
        ]
        
        if round_num == 2:
            questions = questions[:4]  # Take first 4 for round 2
        
        mock_questions = []
        for i, question in enumerate(questions[:num_questions]):
            mock_questions.append({
                'QuestionID': f"MOCK_R{round_num}_Q{i+1}",
                'QuestionText': question
            })
        
        return mock_questions
    
    def _generate_mock_summary(self, summary_type: str) -> str:
        """Generate mock personality summary"""
        summaries = {
            "initial": "You demonstrate a balanced approach to challenges and show strong analytical thinking. Your responses indicate someone who values both independence and collaboration, with a natural inclination toward problem-solving.",
            
            "follow_up": "You are a strategic thinker with excellent communication skills and a natural ability to build relationships. Your leadership style combines decisiveness with empathy, making you effective in both individual and team settings.",
            
            "final": "You are a resilient leader with exceptional problem-solving skills and a natural ability to communicate effectively. Your strategic mindset, combined with strong relationship-building capabilities, makes you particularly well-suited for roles that require both analytical thinking and interpersonal collaboration. You demonstrate high emotional intelligence and adaptability, allowing you to thrive in dynamic environments while maintaining focus on long-term objectives."
        }
        
        return summaries.get(summary_type, summaries["final"])

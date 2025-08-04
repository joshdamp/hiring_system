import requests
import json
from typing import List, Dict, Any
import asyncio
import aiohttp
from datetime import datetime
import random

class HuggingFaceAIService:
    """
    Enhanced FREE AI service using Hugging Face Inference API
    No API key required, completely free!
    """
    
    def __init__(self):
        # Enhanced models for better analysis
        self.sentiment_model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.text_classification_model = "facebook/bart-large-mnli"
        
        # Comprehensive personality framework based on Gallup StrengthsFinder
        self.traits = {
            "Strategic Thinking": [
                {"name": "Analytical", "description": "searches for reasons and causes, thinks about factors that might affect a situation"},
                {"name": "Context", "description": "enjoys thinking about the past to understand the present"},
                {"name": "Futuristic", "description": "inspired by the future and what could be, energizes others with visions"},
                {"name": "Ideation", "description": "fascinated by ideas, able to find connections between seemingly disparate phenomena"},
                {"name": "Input", "description": "has a craving to know more, collects and archives information"},
                {"name": "Intellection", "description": "characterized by intellectual activity, introspective and appreciates discussions"},
                {"name": "Learner", "description": "has a great desire to learn and wants to continuously improve"},
                {"name": "Strategic", "description": "creates alternative ways to proceed, sees patterns and issues"}
            ],
            "Executing": [
                {"name": "Achiever", "description": "has a constant need for achievement, works hard and possesses stamina"},
                {"name": "Arranger", "description": "can organize, enjoys managing variables and aligning them for productivity"},
                {"name": "Belief", "description": "has certain core values that are unchanging, has a defined purpose"},
                {"name": "Consistency", "description": "keenly aware of the need to treat people equally"},
                {"name": "Deliberative", "description": "most comfortable with serious decision-making, anticipates obstacles"},
                {"name": "Discipline", "description": "enjoys routine and structure, instinctively imposes order"},
                {"name": "Focus", "description": "takes direction, follows through and makes corrections to stay on track"},
                {"name": "Responsibility", "description": "takes psychological ownership of commitments, utterly dependable"}
            ],
            "Influencing": [
                {"name": "Activator", "description": "can make things happen by turning thoughts into action"},
                {"name": "Command", "description": "has presence and can take control of situations"},
                {"name": "Communication", "description": "generally finds it easy to put thoughts into words"},
                {"name": "Competition", "description": "measures progress against others, strives to win"},
                {"name": "Maximizer", "description": "focuses on strengths to stimulate excellence"},
                {"name": "Self-Assurance", "description": "confident in ability to manage own life"},
                {"name": "Significance", "description": "wants to be very important in others' eyes"},
                {"name": "Woo", "description": "loves the challenge of meeting new people and winning them over"}
            ],
            "Relationship Building": [
                {"name": "Adaptability", "description": "prefers to go with the flow, tends to be a now person"},
                {"name": "Connectedness", "description": "has faith in the links between all things"},
                {"name": "Developer", "description": "recognizes and cultivates potential in others"},
                {"name": "Empathy", "description": "can sense the feelings of other people"},
                {"name": "Harmony", "description": "looks for consensus and doesn't enjoy conflict"},
                {"name": "Includer", "description": "accepts others and wants to include people"},
                {"name": "Individualization", "description": "intrigued with unique qualities of each person"},
                {"name": "Positivity", "description": "has an enthusiasm that is contagious"},
                {"name": "Relator", "description": "enjoys close relationships with others"}
            ]
        }
    
    def inference_api_call(self, model: str, inputs: str, task: str = "text-generation"):
        """
        Call Hugging Face Inference API (FREE)
        No API key required!
        """
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Content-Type": "application/json"}
        
        if task == "text-generation":
            payload = {
                "inputs": inputs,
                "parameters": {
                    "max_length": 100,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
        elif task == "zero-shot-classification":
            candidate_labels = list(self.trait_descriptors.keys())
            payload = {
                "inputs": inputs,
                "parameters": {"candidate_labels": candidate_labels}
            }
        else:
            payload = {"inputs": inputs}
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            return None
    
    async def analyze_initial_responses(self, responses: List[Dict[str, Any]], 
                                     questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analyze initial responses using smart analysis to create trait rankings
        """
        try:
            # Create a detailed analysis of each response
            trait_scores = {}
            
            # Initialize all traits with base scores
            all_traits = []
            for category in self.traits.values():
                for trait in category:
                    all_traits.append(trait['name'])
                    trait_scores[trait['name']] = 0.5
            
            # Analyze each response specifically
            for response in responses:
                question_id = response.get('questionId', '')
                answer_choice = response.get('response', '')
                
                # Get the corresponding question
                question = None
                for q in questions:
                    # Try exact QuestionID match first
                    if q.get('QuestionID') == question_id:
                        question = q
                        break
                    # Try matching by question text if QuestionID doesn't match
                    if q.get('Prompt') == question_id:
                        question = q
                        break
                
                # If still no match and question_id looks like a full question, try partial matching
                if not question and len(question_id) > 10:  # Likely a full question text
                    for q in questions:
                        if question_id.lower() in q.get('Prompt', '').lower() or q.get('Prompt', '').lower() in question_id.lower():
                            question = q
                            break
                
                if question and answer_choice:
                    # Analyze this specific question-answer pair
                    trait_updates = self._analyze_specific_response(question, answer_choice)
                    
                    # Update trait scores
                    for trait_name, score_change in trait_updates.items():
                        if trait_name in trait_scores:
                            trait_scores[trait_name] += score_change
                else:
                    # If no matching question found, apply minimal trait adjustment
                    pass
            
            # Normalize scores and convert to rankings
            trait_rankings = self._convert_scores_to_rankings(trait_scores)
            
            
            return trait_rankings
            
        except Exception as e:
            return self._generate_fallback_rankings()
    
    def _analyze_specific_response(self, question: Dict[str, Any], answer_choice: str) -> Dict[str, float]:
        """
        Analyze a specific question-answer pair and return trait score adjustments
        """
        trait_updates = {}
        
        question_text = question.get('Prompt', '').lower()
        
        # Convert answer_choice to string if it's a number
        answer_str = str(answer_choice)
        
        # Get the selected option text
        option_key = f"Option{answer_str}" if answer_str.isdigit() else None
        selected_option = question.get(option_key, answer_str).lower() if option_key else str(answer_choice).lower()
        
        
        # Question 1: "When you post something and no one reacts to it"
        if "post something" in question_text and "no one reacts" in question_text:
            if "keep going" in selected_option and "results take time" in selected_option:
                trait_updates.update({
                    "Achiever": 0.8,        # Persistent goal pursuit
                    "Self-Assurance": 0.7,  # Confident in their approach  
                    "Futuristic": 0.6,      # Believes in long-term results
                    "Focus": 0.6,           # Stays on track despite lack of response
                    "Belief": 0.5,          # Strong conviction in their actions
                    "Discipline": 0.4       # Consistent behavior
                })
            elif "ask for feedback" in selected_option:
                trait_updates.update({
                    "Learner": 0.8,         # Seeks to improve
                    "Developer": 0.6,       # Values growth and feedback
                    "Communication": 0.5,    # Actively seeks dialogue
                    "Adaptability": 0.5     # Willing to adjust approach
                })
            elif "wait and hope" in selected_option:
                trait_updates.update({
                    "Deliberative": 0.6,    # Thoughtful, patient approach
                    "Harmony": 0.5,         # Prefers not to push
                    "Adaptability": 0.4     # Goes with the flow
                })
            elif "feel discouraged" in selected_option:
                trait_updates.update({
                    "Empathy": 0.4,         # Sensitive to others' reactions
                    "Connectedness": 0.3    # Values connection with others
                })
        
        # Question 2: Team project behavior
        elif "team project" in question_text:
            if "take charge" in selected_option and "delegate" in selected_option:
                trait_updates.update({
                    "Command": 0.9,         # Natural leadership
                    "Activator": 0.8,       # Takes initiative
                    "Arranger": 0.7,        # Organizes resources
                    "Strategic": 0.6,       # Plans and delegates
                    "Significance": 0.5     # Wants to lead and be important
                })
            elif "suggest ideas" in selected_option and "collaborate equally" in selected_option:
                trait_updates.update({
                    "Communication": 0.8,   # Shares ideas effectively
                    "Includer": 0.7,        # Values equal participation
                    "Harmony": 0.6,         # Seeks consensus
                    "Ideation": 0.6,        # Generates ideas
                    "Relator": 0.5          # Builds collaborative relationships
                })
            elif "wait for others" in selected_option:
                trait_updates.update({
                    "Deliberative": 0.6,    # Cautious, waits for direction
                    "Harmony": 0.5,         # Avoids taking control
                    "Adaptability": 0.5     # Flexible with others' plans
                })
            elif "focus on your specific expertise" in selected_option:
                trait_updates.update({
                    "Focus": 0.8,           # Concentrates on their strength
                    "Analytical": 0.6,      # Deep expertise in their area
                    "Intellection": 0.5,    # Thinks deeply about their domain
                    "Maximizer": 0.5        # Focuses on strengths
                })
        
        # Question 3: Stressful situations
        elif "stressful situations" in question_text:
            if "stay calm" in selected_option and "think logically" in selected_option:
                trait_updates.update({
                    "Analytical": 0.9,      # Uses logic under pressure
                    "Deliberative": 0.7,    # Careful thinking
                    "Self-Assurance": 0.6,  # Confident in abilities
                    "Discipline": 0.5,      # Maintains composure
                    "Intellection": 0.5     # Thoughtful approach
                })
            elif "seek support" in selected_option:
                trait_updates.update({
                    "Relator": 0.8,         # Builds on relationships
                    "Empathy": 0.6,         # Understands others can help
                    "Communication": 0.5,    # Reaches out effectively
                    "Includer": 0.4         # Brings others in
                })
            elif "feel overwhelmed" in selected_option and "push through" in selected_option:
                trait_updates.update({
                    "Achiever": 0.7,        # Pushes through challenges
                    "Responsibility": 0.6,   # Feels duty to continue
                    "Discipline": 0.5       # Forces through difficulty
                })
            elif "take breaks" in selected_option:
                trait_updates.update({
                    "Adaptability": 0.7,    # Adjusts approach as needed
                    "Self-Assurance": 0.5,  # Confident in their strategy
                    "Strategic": 0.4        # Plans recovery time
                })
        
        # Question 4: Learning new skills
        elif "learn new skills" in question_text:
            if "hands-on practice" in selected_option:
                trait_updates.update({
                    "Activator": 0.8,       # Learns by doing
                    "Learner": 0.7,         # Active learning approach
                    "Achiever": 0.5,        # Gets results through practice
                    "Adaptability": 0.4     # Adjusts through trial
                })
            elif "structured courses" in selected_option:
                trait_updates.update({
                    "Learner": 0.9,         # Systematic learning
                    "Discipline": 0.7,      # Follows structured approach
                    "Focus": 0.6,           # Concentrates on curriculum
                    "Analytical": 0.5       # Methodical learning
                })
            elif "experienced colleagues" in selected_option:
                trait_updates.update({
                    "Relator": 0.8,         # Learns through relationships
                    "Developer": 0.6,       # Values mentorship
                    "Communication": 0.5,    # Engages with others
                    "Empathy": 0.4          # Understands others' expertise
                })
            elif "reading documentation" in selected_option:
                trait_updates.update({
                    "Intellection": 0.8,    # Prefers thinking and reading
                    "Input": 0.7,           # Collects information
                    "Analytical": 0.6,      # Studies thoroughly
                    "Learner": 0.5          # Self-directed learning
                })
        
        # Question 5: Receiving feedback
        elif "constructive feedback" in question_text:
            if "ask clarifying questions" in selected_option:
                trait_updates.update({
                    "Communication": 0.8,   # Engages in dialogue
                    "Learner": 0.7,         # Wants to understand fully
                    "Analytical": 0.6,      # Seeks deeper understanding
                    "Developer": 0.5        # Values growth through feedback
                })
            elif "take notes" in selected_option and "improvement plan" in selected_option:
                trait_updates.update({
                    "Achiever": 0.8,        # Plans for improvement
                    "Discipline": 0.7,      # Systematic approach
                    "Responsibility": 0.6,   # Takes ownership
                    "Focus": 0.5,           # Concentrates on improvement
                    "Strategic": 0.5        # Plans next steps
                })
            elif "implement changes immediately" in selected_option:
                trait_updates.update({
                    "Activator": 0.9,       # Takes immediate action
                    "Adaptability": 0.7,    # Quick to adjust
                    "Achiever": 0.6,        # Acts on feedback quickly
                    "Responsibility": 0.5    # Takes ownership immediately
                })
            elif "reflect on the feedback" in selected_option:
                trait_updates.update({
                    "Intellection": 0.8,    # Thinks deeply about feedback
                    "Deliberative": 0.7,    # Careful consideration
                    "Self-Assurance": 0.5,  # Confident in reflection process
                    "Context": 0.4          # Considers broader implications
                })
        
        return trait_updates
    
    async def _classify_personality_traits(self, text: str) -> Dict[str, float]:
        """
        Use free zero-shot classification to analyze personality traits
        """
        try:
            # Use the classification model
            result = self.inference_api_call(
                model=self.classification_model,
                inputs=text,
                task="zero-shot-classification"
            )
            
            if result and 'labels' in result and 'scores' in result:
                trait_scores = {}
                for label, score in zip(result['labels'], result['scores']):
                    if label in self.trait_descriptors:
                        trait_scores[label] = score
                
                # Fill in missing traits with baseline scores
                for trait in self.traits:
                    if trait not in trait_scores:
                        trait_scores[trait] = 0.3  # Baseline score
                
                return trait_scores
            else:
                return self._generate_fallback_scores()
                
        except Exception as e:
            return self._generate_fallback_scores()
    
    def _create_analysis_text(self, responses: List[Dict[str, Any]], 
                            questions: List[Dict[str, Any]]) -> str:
        """Create text for AI analysis from responses"""
        analysis_parts = []
        
        for response in responses:
            # Find corresponding question
            question = next((q for q in questions if q['QuestionID'] == response['questionId']), None)
            if question:
                option_key = f"Option{response['response']}"
                selected_option = question.get(option_key, "Unknown response")
                
                analysis_parts.append(f"Question: {question['Prompt']}")
                analysis_parts.append(f"Response: {selected_option}")
                analysis_parts.append("")
        
        return "\n".join(analysis_parts)
    
    def _convert_scores_to_rankings(self, trait_scores: Dict[str, float]) -> Dict[str, int]:
        """Convert trait scores to rankings (1 = best, 34 = worst)"""
        # Sort traits by score (highest first)
        sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
        
        rankings = {}
        for rank, (trait, score) in enumerate(sorted_traits, 1):
            rankings[trait] = rank
        
        return rankings
    
    def _generate_fallback_scores(self) -> Dict[str, float]:
        """Generate fallback scores if AI fails"""
        import random
        return {trait: random.uniform(0.2, 0.8) for trait in self.traits}
    
    def _generate_fallback_rankings(self) -> Dict[str, int]:
        """Generate fallback rankings if AI fails"""
        import random
        traits_copy = self.traits.copy()
        random.shuffle(traits_copy)
        return {trait: i + 1 for i, trait in enumerate(traits_copy)}
    
    async def generate_follow_up_questions(self, user_id: str, round_num: int,
                                         previous_responses: List[Dict[str, Any]],
                                         trait_rankings: Dict[str, int]) -> List[Dict[str, Any]]:
        """
        Generate personalized follow-up questions using FREE AI
        """
        try:
            num_questions = 12 if round_num == 1 else 4
            
            # Get top traits for focus
            top_traits = sorted(trait_rankings.items(), key=lambda x: x[1])[:5]
            top_trait_names = [trait[0] for trait in top_traits]
            
            # Generate questions for each top trait
            questions = []
            for i, trait in enumerate(top_trait_names[:num_questions]):
                question_text = self._generate_trait_question(trait, i + 1)
                questions.append({
                    'QuestionID': f"{user_id}_R{round_num}_Q{i+1}",
                    'QuestionText': question_text
                })
            
            # Fill remaining slots with general questions
            while len(questions) < num_questions:
                general_question = self._get_general_question(len(questions) + 1)
                questions.append({
                    'QuestionID': f"{user_id}_R{round_num}_Q{len(questions)+1}",
                    'QuestionText': general_question
                })
            
            return questions[:num_questions]
            
        except Exception as e:
            return self._generate_fallback_questions(user_id, round_num)
    
    def _generate_trait_question(self, trait: str, question_num: int) -> str:
        """Generate a question focused on a specific trait"""
        trait_questions = {
            "Strategic": "Describe a time when you had to develop a long-term plan. What was your approach and how did you ensure success?",
            "Communication": "Tell me about a situation where you had to explain a complex concept to someone. How did you make it understandable?",
            "Achiever": "Describe your most significant professional accomplishment. What drove you to achieve it?",
            "Learner": "Tell me about a time you had to quickly learn something new for work. How did you approach the learning process?",
            "Responsibility": "Describe a situation where you took ownership of a problem that wasn't directly your responsibility. Why did you do it?",
            "Empathy": "Tell me about a time when you had to understand someone else's perspective in a difficult situation. How did you approach it?",
            "Relator": "Describe how you build and maintain professional relationships. What makes these relationships meaningful to you?",
            "Adaptability": "Tell me about a time when you had to quickly adapt to a major change at work. How did you handle it?",
            "Developer": "Describe a time when you helped someone else grow or improve. What was your approach?",
            "Positivity": "Tell me about a time when you helped boost team morale during a challenging period. What did you do?"
        }
        
        return trait_questions.get(trait, 
            f"Describe how you typically approach situations that require {trait.lower()} skills. Provide specific examples.")
    
    def _get_general_question(self, question_num: int) -> str:
        """Get general follow-up questions"""
        general_questions = [
            "What motivates you most in your professional work?",
            "How do you handle pressure and tight deadlines?",
            "Describe your ideal work environment and team dynamics.",
            "Tell me about a time you had to make a difficult decision with limited information.",
            "How do you prefer to receive feedback and how do you respond to criticism?",
            "Describe a situation where you had to persuade others to see your point of view.",
            "What role do you typically play in team projects and why?",
            "How do you balance attention to detail with meeting deadlines?",
            "Tell me about a time you failed at something. What did you learn?",
            "How do you stay current with trends and developments in your field?",
            "Describe how you prioritize tasks when everything seems urgent.",
            "Tell me about a time you had to work with someone very different from yourself."
        ]
        
        return general_questions[(question_num - 1) % len(general_questions)]
    
    def _generate_fallback_questions(self, user_id: str, round_num: int) -> List[Dict[str, Any]]:
        """Generate fallback questions if AI generation fails"""
        num_questions = 12 if round_num == 1 else 4
        
        fallback_questions = [
            "Describe your leadership style and provide an example of when you successfully led a team.",
            "How do you handle conflict in the workplace? Give me a specific example.",
            "Tell me about a time you had to learn a new skill quickly. How did you approach it?",
            "Describe a situation where you had to work under pressure. How did you manage it?",
            "What strategies do you use to stay organized and manage your time effectively?",
            "Tell me about a time you had to adapt to a significant change. How did you handle it?",
            "Describe how you build relationships with colleagues and clients.",
            "How do you approach problem-solving when faced with a complex challenge?",
            "Tell me about a time you went above and beyond what was expected of you.",
            "How do you handle feedback, both positive and constructive?",
            "Describe your approach to continuous learning and professional development.",
            "Tell me about a time you had to make a decision with incomplete information."
        ]
        
        questions = []
        for i in range(num_questions):
            questions.append({
                'QuestionID': f"{user_id}_R{round_num}_Q{i+1}",
                'QuestionText': fallback_questions[i % len(fallback_questions)]
            })
        
        return questions
    
    async def generate_summary(self, user_responses: Dict[str, List[Dict[str, Any]]], 
                             trait_rankings: Dict[str, int], 
                             summary_type: str) -> str:
        """
        Generate personality summary using smart analysis
        """
        try:
            # Get top 5 traits
            top_traits = sorted(trait_rankings.items(), key=lambda x: x[1])[:5]
            
            
            # Create detailed, personalized summary
            summary = self._create_detailed_summary(top_traits, summary_type)
            
            return summary
            
        except Exception as e:
            return self._generate_fallback_summary(summary_type)
    
    def _create_detailed_summary(self, top_traits: List[tuple], summary_type: str) -> str:
        """Create detailed, accurate summary based on top personality traits"""
        if not top_traits:
            return self._generate_fallback_summary(summary_type)
        
        # Get the trait details
        trait_details = {}
        for category_name, category_traits in self.traits.items():
            for trait in category_traits:
                trait_details[trait['name']] = {
                    'category': category_name,
                    'description': trait['description']
                }
        
        # Build summary based on top traits
        primary_trait = top_traits[0][0]
        secondary_trait = top_traits[1][0] if len(top_traits) > 1 else primary_trait
        tertiary_trait = top_traits[2][0] if len(top_traits) > 2 else secondary_trait
        
        primary_desc = trait_details.get(primary_trait, {}).get('description', 'demonstrates strong capabilities')
        secondary_desc = trait_details.get(secondary_trait, {}).get('description', 'shows excellent skills')
        tertiary_desc = trait_details.get(tertiary_trait, {}).get('description', 'displays notable abilities')
        
        primary_category = trait_details.get(primary_trait, {}).get('category', 'Professional Skills')
        secondary_category = trait_details.get(secondary_trait, {}).get('category', 'Work Style')
        
        if summary_type == "initial":
            summary = f"Based on your responses, your strongest trait is **{primary_trait}** - you {primary_desc}. "
            summary += f"You also demonstrate strong **{secondary_trait}** abilities, as you {secondary_desc}. "
            summary += f"Your **{tertiary_trait}** nature means you {tertiary_desc}. "
            summary += f"This combination suggests you excel in {primary_category.lower()} and have a natural aptitude for {secondary_category.lower()}."
            
        elif summary_type == "follow_up":
            summary = f"Your detailed responses confirm that **{primary_trait}** is indeed your dominant strength - you {primary_desc}. "
            summary += f"Your **{secondary_trait}** capabilities are also pronounced, showing how you {secondary_desc}. "
            summary += f"The way you approach challenges reveals your **{tertiary_trait}** tendencies, where you {tertiary_desc}. "
            summary += f"You appear particularly well-suited for roles requiring {primary_category.lower()} combined with {secondary_category.lower()}."
            
        else:  # final
            summary = f"You are a **{primary_trait}**-driven professional who {primary_desc}. "
            summary += f"Your **{secondary_trait}** abilities complement this perfectly, as you {secondary_desc}. "
            summary += f"Your **{tertiary_trait}** approach ensures that you {tertiary_desc}. "
            
            # Add career implications
            if primary_category == "Strategic Thinking":
                summary += "Your strategic mindset makes you ideal for planning, analysis, and innovation roles. "
            elif primary_category == "Executing":
                summary += "Your execution-focused nature makes you excellent at delivering results and managing operations. "
            elif primary_category == "Influencing":
                summary += "Your influencing abilities make you naturally suited for leadership and communication roles. "
            elif primary_category == "Relationship Building":
                summary += "Your relationship-building strengths make you excellent in collaborative and people-focused roles. "
                
            summary += f"The combination of {primary_category.lower()} and {secondary_category.lower()} skills positions you well for senior roles that require both individual excellence and team collaboration."
        
        return summary
    
    def _generate_fallback_summary(self, summary_type: str) -> str:
        """Generate fallback summary if AI generation fails"""
        summaries = {
            "initial": "You demonstrate a balanced approach to challenges and show strong analytical thinking. Your responses indicate someone who values both independence and collaboration, with a natural inclination toward problem-solving.",
            
            "follow_up": "You are a strategic thinker with excellent communication skills and a natural ability to build relationships. Your leadership style combines decisiveness with empathy, making you effective in both individual and team settings.",
            
            "final": "You are a resilient leader with exceptional problem-solving skills and a natural ability to communicate effectively. Your strategic mindset, combined with strong relationship-building capabilities, makes you particularly well-suited for roles that require both analytical thinking and interpersonal collaboration. You demonstrate high emotional intelligence and adaptability, allowing you to thrive in dynamic environments while maintaining focus on long-term objectives."
        }
        
        return summaries.get(summary_type, summaries["final"])
    
    async def update_trait_rankings(self, current_rankings: Dict[str, int],
                                  new_responses: List[Dict[str, Any]],
                                  round_num: int) -> Dict[str, int]:
        """
        Update trait rankings based on new follow-up responses
        """
        try:
            # Analyze new responses
            response_text = "\n".join([resp.get('response', '') for resp in new_responses])
            
            if response_text.strip():
                # Get trait adjustments from AI analysis
                trait_adjustments = await self._analyze_response_adjustments(response_text)
                
                # Apply adjustments to current rankings
                updated_rankings = self._apply_ranking_adjustments(current_rankings, trait_adjustments)
                return updated_rankings
            else:
                return current_rankings
                
        except Exception as e:
            return current_rankings
    
    async def _analyze_response_adjustments(self, response_text: str) -> Dict[str, int]:
        """Analyze responses to determine trait ranking adjustments"""
        # Simple keyword-based analysis for trait strength indicators
        trait_keywords = {
            "Strategic": ["plan", "strategy", "long-term", "analyze", "systematic"],
            "Communication": ["explain", "communicate", "discuss", "present", "clarify"],
            "Achiever": ["accomplish", "complete", "deliver", "achieve", "finish"],
            "Learner": ["learn", "study", "research", "understand", "knowledge"],
            "Leadership": ["lead", "manage", "direct", "guide", "coordinate"],
            "Empathy": ["understand", "feel", "empathy", "listen", "support"],
            "Adaptability": ["adapt", "flexible", "change", "adjust", "pivot"]
        }
        
        adjustments = {}
        response_lower = response_text.lower()
        
        for trait, keywords in trait_keywords.items():
            if trait in self.traits:
                keyword_count = sum(1 for keyword in keywords if keyword in response_lower)
                if keyword_count > 0:
                    adjustments[trait] = min(keyword_count * 2, 5)  # Max adjustment of 5
        
        return adjustments
    
    def _apply_ranking_adjustments(self, current_rankings: Dict[str, int], 
                                 adjustments: Dict[str, int]) -> Dict[str, int]:
        """Apply adjustments to current trait rankings"""
        updated = current_rankings.copy()
        
        for trait, adjustment in adjustments.items():
            if trait in updated:
                # Improve ranking (lower number = better rank)
                new_rank = max(1, updated[trait] - adjustment)
                updated[trait] = new_rank
        
        return updated

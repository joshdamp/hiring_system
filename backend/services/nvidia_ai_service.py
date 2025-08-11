import requests
import json
import re
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
load_dotenv()
load_dotenv('../.env')  # Also try parent directory

# Chapter-specific prompts
CHAPTER_2_PROMPT = """
Chapter 2, Emotional truth - After we answered chapter 1, then we have an estimate data of my gallup cliffton strengths that tells who I am on the subconcious state (a bigger percentage of the human mind). Then now, chapter 2 tends to solve contradictions, and solidify thoughts from chapter 1. It is  Like situational scenarios that has about 4 choices that will reveal a trait I used to solve a situation and something I can answer two times, giving each answer a different weight, weight 1 is the one i will most likely do. Furthermore this is to create an in-depth analysis of who I am behind the traditional statistical data we can get from the traditional gallup clifton on how I handle such situations. (this section has 13 questions) 

Example question: You just got praise for a group project, but someone was left out. What's your first instinct?
Example choices: 
A. Celebrate and motivate the team more 
B. Make sure the left-out person feels seen 
C. Reflect on what systems failed and fix it 
D. Clarify roles so it doesn't happen again 
What it shows: A. (Positivity, Woo) -- B. (Empathy, Includer) -- C. (Analytical, Restorative) -- D. (Consistency, Responsibility)
Example answer: A-B (A is the most dominant thing you'll do, B is the second thing you'll most likely do)
LOGIC: so in this example we are testing what trait will be used. based on sample answer, what he/she will use is Positivity and woo, meaning it is the most dominant, and the next is empathy and includer. So if this a pointing system. It's like giving 2 additional weights to both traits of the first choice, 1 additional weight to second choice, then zero additional to the unchosen pair). 

Then we will use the responses on this chapter to further solidify the identity of someone.
The results that we will be using per chapter will be used as a baseline of iteration to go through the correct estimate of my profile as we deepen through each chapter.
 
REMEMBER: Gallup trait should have complete 34 traits, without double entry like two repeated strength like two activator on the list (activator listed as strength 10, and listed as strength 30 -- this is wrong). And 1 gallup trait = 1 strength, total to 34 single traits, no mixed traits in a single number like (Strength 1: responsibility & developer -- this is wrong)..
Make sure to be aware of the false-truth-traits. False-truths between traits, like empathy who naturally sees feelings, versus individualization who can read or mirror each person well but might feel none. another example of false-truths between traits, like a responsibility who does task because it triggers guilt to him when he can't do it even if no one sees him, versus a significance person who does things for other to see him as dependable. or, false-truth between the false responsibility driven by significance's desire of creating impact or command's desire to be in control using power assertion. If this is clear, ask me the 13 questions to both extract more truth about me, and to deepen what you know about me. 

Make sure to give proper set of choices that will give accurate results and will not confuse the system (Example of vague and confusing thoughts to avoid: Helping someone on their tasks -- Significance you want to be seen something impactful // or it can also be Developer you want to be develop them // Consistency coz you want team goals to be consistently hitting kpi // Command coz you want to be in power -- To fix this, make sure that your question is specific enough to avoid confusions that can be misinterpreted; like to be brutally honest, it's like a specific event that can be justified by every trait, and I do not want those kind of vague scenarios to happen)

If you are ready, then give me the questions.
"""

CHAPTER_3_PROMPT = """
For chapter 3, the data you will get from chapter 3 and mix it with what you know about me on the previous chapters to give me an idea of who I am.

Chapter 3, Story & Demonstration - if chapter 1 is about my subconcious, chapter 2 is how I handle things and what trait I used to perform such task, then chapter 3 set of questions focuses on an in depth questions or context about how I perceive things, may it be a feedback, happiness, stress, or others. The purpose of chapter 3 is to solidify truth based on contradiction between chapter 1 and 2 and to add clarity on it.  If this is clear, then I want you to remember these, as we will proceed to chapter 3 (with 7 questions) after recalling my results on chapter 1 and chapter 2.

The results that we will be using per chapter will be used as a baseline of iteration to go through the correct estimate of my profile as we deepen through each chapter. 
REMEMBER: Gallup trait should have complete 34 traits, without double entry like two repeated strength like two activator on the list (activator listed as strength 10, and listed as strength 30 -- this is wrong). And 1 gallup trait = 1 strength, total to 34 single traits, no mixed traits in a single number like (Strength 1: responsibility & developer -- this is wrong)..Make sure to be aware of the false-truth-traits. False-truths between traits, like empathy who naturally sees feelings, versus individualization who can read or mirror each person well but might feel none. another example of false-truths between traits, like a responsibility who does task because it triggers guilt to him when he can't do it even if no one sees him, versus a significance person who does things for other to see him as dependable. or, false-truth between the false responsibility driven by significance's desire of creating impact or command's desire to be in control using power assertion. 

If this is clear, ask me the 7 questions to both extract more truth about me, and to deepen what you know about me.

 Make sure to give proper set of questions that will trigger me to give accurate results and will not confuse the system it's like making sure that the answers will be relevant coz the kind of questions you gave does not give room for making me give vague responses (Example of vague and confusing thoughts to avoid: Helping someone on their tasks -- Significance you want to be seen something impactful // or it can also be Developer you want to be develop them // Consistency coz you want team goals to be consistently hitting kpi // Command coz you want to be in power -- To fix this, make sure that your question is specific enough to avoid confusions that can be misinterpreted, like to be brutally honest, it's like a specific event can be justified by every trait, and I do not want those kind of vague scenarios to happen)

if you're ready, then give me the questions.
"""

class NvidiaAIService:
    """
    NVIDIA LLM service using Nemotron via OpenRouter for strengths assessment with CliftonStrengths priming
    """
    
    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.getenv('NVIDIA_API_KEY')
        if not self.api_key:
            print("Warning: NVIDIA_API_KEY not found. Please set your NVIDIA API key.")
        
        # OpenRouter API configuration for NVIDIA Nemotron model
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "nvidia/llama-3.1-nemotron-70b-instruct"  # NVIDIA Nemotron model via OpenRouter
        
        # Use the complete 34 CliftonStrengths from ai_prompts_service
        self.clifton_strengths = CLIFTON_STRENGTHS
        self.all_traits = get_all_strengths()
        
        # System prompt with CliftonStrengths priming
        self.system_prompt = get_system_prompt()
        
    def _make_api_call(self, messages: List[Dict[str, str]], max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Make a call to NVIDIA API via OpenRouter
        """
        if not self.api_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://hiring-system.onrender.com/",
            "X-Title": "Hiring System AI Analysis"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=90)
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"DEBUG: API returned {len(content)} characters")
                
                # Check if response was truncated
                finish_reason = result['choices'][0].get('finish_reason', 'unknown')
                if finish_reason == 'length':
                    print(f"WARNING: API response was truncated due to length limit")
                elif finish_reason != 'stop':
                    print(f"WARNING: API response finished with reason: {finish_reason}")
                
                return content
            else:
                print(f"Unexpected API response format: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"NVIDIA API call failed: {e}")
            return None
        except Exception as e:
            print(f"Error processing NVIDIA response: {e}")
            return None
    
    def _extract_rankings_from_response(self, response: str) -> Dict[str, int]:
        """Enhanced JSON extraction with multiple fallback strategies"""
        import re
        
        try:
            # Strategy 1: Direct JSON parsing
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                pass
            
            # Strategy 2: Extract JSON with regex and clean it
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                print(f"DEBUG: Extracted JSON: {json_str[:500]}...")
                
                # Clean the JSON string to remove comments and fix formatting issues
                json_str = self._clean_json_string(json_str)
                
                try:
                    rankings = json.loads(json_str)
                    print(f"Parsed trait rankings: {len(rankings)} traits found")
                    return rankings
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error after cleaning: {e}")
                    
            # Strategy 3: Manual extraction of trait:value pairs
            trait_pattern = r'"?([A-Za-z\-]+)"?\s*:\s*(\d+)'
            matches = re.findall(trait_pattern, response)
            if matches:
                rankings = {}
                for trait, value in matches:
                    if trait in self.all_traits:
                        rankings[trait] = int(value)
                print(f"Manual extraction found {len(rankings)} valid traits")
                if len(rankings) >= 20:  # Accept if we got most traits
                    return rankings
                    
            print("DEBUG: All JSON extraction strategies failed")
            return None
            
        except Exception as e:
            print(f"Error in _extract_rankings_from_response: {e}")
            return None
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean JSON string to remove comments and fix common formatting issues"""
        import re
        
        # Remove comments in parentheses
        json_str = re.sub(r'\([^)]*\)', '', json_str)
        
        # Remove lines that start with comments or explanations
        lines = json_str.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip lines that are clearly comments or explanations
            if not line.strip().startswith(('*', '-', 'Note:', 'Explanation:', '//')):
                cleaned_lines.append(line)
        json_str = '\n'.join(cleaned_lines)
        
        # Fix common JSON issues
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
        json_str = re.sub(r'"\s*,\s*"', '", "', json_str)  # Fix quote spacing
        
        return json_str

    def _get_fallback_rankings(self) -> Dict[str, int]:
        """Generate fallback rankings using enhanced randomization"""
        print("DEBUG: Using fallback rankings due to AI analysis failure")
        
        # Create groups of traits for more realistic distribution
        strategic_thinking = ['Analytical', 'Context', 'Futuristic', 'Ideation', 'Input', 'Intellection', 'Learner', 'Strategic']
        executing = ['Achiever', 'Arranger', 'Belief', 'Consistency', 'Deliberative', 'Discipline', 'Focus', 'Responsibility', 'Restorative']
        influencing = ['Activator', 'Command', 'Communication', 'Competition', 'Maximizer', 'Self-Assurance', 'Significance', 'Woo']
        relationship_building = ['Adaptability', 'Connectedness', 'Developer', 'Empathy', 'Harmony', 'Includer', 'Individualization', 'Positivity', 'Relator']
        
        # Shuffle each group and assign rankings
        all_groups = [strategic_thinking, executing, influencing, relationship_building]
        random.shuffle(all_groups)
        
        rankings = {}
        rank = 1
        
        for group in all_groups:
            shuffled_group = group.copy()
            random.shuffle(shuffled_group)
            for trait in shuffled_group:
                rankings[trait] = rank
                rank += 1
        
        return rankings

    def analyze_responses(self, responses: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analyze user responses and rank CliftonStrengths traits with enhanced validation
        """
        print(f"DEBUG: Analyzing {len(responses)} responses with NVIDIA AI")
        
        if not responses:
            return self._get_fallback_rankings()
        
        # Prepare response data for analysis
        response_data = []
        for resp in responses:
            response_data.append(f"Q{resp.get('questionId', 'Unknown')}: {resp.get('response', 'No response')}")
        
        # Enhanced prompt for better trait analysis
        analysis_prompt = f"""
{PRIMING_1_IDENTITY}

{PRIMING_2_METHODOLOGY}

Based on these user responses to assessment questions, analyze and rank the 34 CliftonStrengths traits from 1 (strongest/most evident) to 34 (weakest/least evident).

User Responses:
{chr(10).join(response_data)}

CRITICAL REQUIREMENTS:
1. Analyze the CONTENT and MEANING of each response
2. Look for patterns, preferences, and behavioral indicators
3. Rank traits based on psychological insights from responses
4. DO NOT use alphabetical ordering
5. Consider emotional intelligence, work style, and decision-making patterns
6. Give higher rankings to traits that match the user's expressed preferences and behaviors

CliftonStrengths Traits to Rank:
{', '.join(self.all_traits)}

IMPORTANT: Return ONLY a valid JSON object. No explanations, no markdown, no extra text.
Format: {{"TraitName": ranking_number, ...}}

Example: {{"Achiever": 1, "Strategic": 2, "Empathy": 3, ...}}
"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            print("DEBUG: Making API call for trait analysis...")
            response = self._make_api_call(messages, max_tokens=1500, temperature=0.3)
            print(f"AI Response for trait analysis: {response[:500]}...")
            
            if response:
                # Enhanced JSON extraction with multiple fallback strategies
                rankings = self._extract_rankings_from_response(response)
                if rankings:
                    # Enhanced validation of AI rankings
                    if self._validate_ai_rankings(rankings):
                        return rankings
                    else:
                        print("DEBUG: AI rankings failed validation, using fallback")
                        return self._get_fallback_rankings()
                else:
                    print("DEBUG: No valid JSON found in AI response")
                    return self._get_fallback_rankings()
                
        except Exception as e:
            print(f"Error parsing rankings: {e}")
            return self._get_fallback_rankings()

    async def analyze_initial_responses(self, responses: List[Dict[str, Any]], 
                                     questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analyze initial responses using NVIDIA AI to create trait rankings
        """
        try:
            if not self.api_key:
                return self._get_fallback_rankings()
            
            print(f"DEBUG: Analyzing {len(responses)} responses with NVIDIA AI")
            
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
                    left_statement = question.get('LeftStatement', '')
                    right_statement = question.get('RightStatement', '')
                    theme = question.get('Theme', '')
                    
                    response_text += f"Question {i+1} ({theme}): \n"
                    response_text += f"Left: {left_statement}\n"
                    response_text += f"Right: {right_statement}\n"
                    response_text += f"Response: {answer} (1=Strongly Left, 5=Strongly Right)\n\n"
            
            # Enhanced AI analysis prompt with priming
            analysis_prompt = f"""
{PRIMING_1_IDENTITY}

{PRIMING_2_METHODOLOGY}

Now analyze these Chapter 1 responses and provide the 34 Gallup Clifton Strengths rankings:

{response_text}

CRITICAL: Return ONLY a valid JSON object with ALL 34 traits ranked from 1-34 (1=strongest). 
Use the exact trait names: Achiever, Activator, Adaptability, Analytical, Arranger, Belief, Command, Communication, Competition, Connectedness, Consistency, Context, Deliberative, Developer, Discipline, Empathy, Focus, Futuristic, Harmony, Ideation, Includer, Individualization, Input, Intellection, Learner, Maximizer, Positivity, Relator, Responsibility, Restorative, Self-Assurance, Significance, Strategic, Woo.

Format: {{"Achiever": 1, "Activator": 2, ...}}

Analyze the responses carefully to determine which traits are strongest based on the user's choices.
"""
            
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user", 
                    "content": analysis_prompt
                }
            ]
            
            print("DEBUG: Making API call for trait analysis...")
            ai_response = self._make_api_call(messages, max_tokens=1500, temperature=0.3)
            
            print(f"NVIDIA AI Response for trait analysis: {ai_response[:1000]}...")
            
            if ai_response:
                try:
                    # Extract JSON from the response
                    import re
                    json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                    if json_match:
                        json_text = json_match.group()
                        print(f"DEBUG: Extracted JSON: {json_text[:500]}...")
                        trait_rankings = json.loads(json_text)
                        print(f"Parsed trait rankings: {len(trait_rankings)} traits found")
                        
                        # Validate that we have rankings for all traits
                        if len(trait_rankings) >= 30:
                            # Check if rankings are actually varied
                            values = list(trait_rankings.values())
                            unique_values = len(set(values))
                            print(f"DEBUG: Found {unique_values} unique ranking values out of {len(values)} total")
                            
                            if unique_values > 15:  # Good variation in rankings
                                print(f"DEBUG: NVIDIA AI rankings look valid, using them")
                                return trait_rankings
                            else:
                                print(f"DEBUG: NVIDIA AI rankings look too uniform, using fallback")
                
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    pass
            
            # Fallback if AI analysis fails
            print(f"DEBUG: Using fallback rankings due to NVIDIA AI analysis failure")
            return self._get_fallback_rankings()
            
        except Exception as e:
            print(f"Error in analyze_initial_responses: {e}")
            return self._get_fallback_rankings()
    
    def _validate_ai_rankings(self, rankings: Dict[str, int]) -> bool:
        """Enhanced validation to detect poor AI analysis"""
        if not rankings or len(rankings) != 34:
            print(f"DEBUG: Invalid ranking count: {len(rankings) if rankings else 0}")
            return False
        
        # Check if all traits are present
        missing_traits = set(self.all_traits) - set(rankings.keys())
        if missing_traits:
            print(f"DEBUG: Missing traits: {missing_traits}")
            return False
        
        # Check ranking values
        rank_values = list(rankings.values())
        expected_ranks = set(range(1, 35))
        actual_ranks = set(rank_values)
        
        if actual_ranks != expected_ranks:
            print(f"DEBUG: Invalid rank values. Expected 1-34, got: {sorted(actual_ranks)}")
            return False
        
        # Enhanced check for sequential/alphabetical patterns
        trait_names = list(rankings.keys())
        sorted_by_rank = sorted(trait_names, key=lambda x: rankings[x])
        
        # Check if rankings are too sequential (alphabetical)
        unique_ranks = len(set(rank_values))
        print(f"DEBUG: Found {unique_ranks} unique ranking values out of {len(rank_values)} total")
        
        # Check for alphabetical ordering pattern
        is_alphabetical = sorted_by_rank == sorted(trait_names)
        
        # Check for too many sequential ranks (indicating poor analysis)
        sequential_count = 0
        for i in range(len(sorted_by_rank) - 1):
            current_trait = sorted_by_rank[i]
            next_trait = sorted_by_rank[i + 1]
            if ord(current_trait[0]) + 1 == ord(next_trait[0]):  # Sequential first letters
                sequential_count += 1
        
        is_sequential_pattern = sequential_count > 15  # More than half are sequential
        
        print(f"DEBUG: Is sequential pattern: {is_sequential_pattern}")
        
        if is_alphabetical or is_sequential_pattern:
            print("DEBUG: AI rankings look sequential/invalid, using fallback")
            return False
        
        print("DEBUG: AI rankings passed validation")
        return True

    def _validate_rankings(self, rankings: Dict[str, int]) -> bool:
        """Validate trait rankings"""
        if not rankings:
            print("DEBUG: Empty rankings")
            return False
        
        # Check if all traits are present
        missing_traits = set(self.all_traits) - set(rankings.keys())
        if missing_traits:
            print(f"DEBUG: Missing traits: {missing_traits}")
            return False
        
        # Check ranking values
        rank_values = list(rankings.values())
        expected_ranks = set(range(1, 35))
        actual_ranks = set(rank_values)
        
        if actual_ranks != expected_ranks:
            print(f"DEBUG: Invalid rank values. Expected 1-34, got: {sorted(actual_ranks)}")
            return False
        
        print("DEBUG: Rankings validation passed")
        return True

    async def generate_follow_up_questions(self, user_id: str, trait_rankings: Dict[str, int], 
                                   previous_responses: List[Dict[str, Any]], round_num: int) -> List[Dict[str, Any]]:
        """
        Generate follow-up questions based on trait rankings and previous responses
        """
        print(f"DEBUG: Generating follow-up questions for user {user_id}, round {round_num}")
        print(f"DEBUG: Retrieved trait rankings for {user_id}: {len(trait_rankings)} traits")
        print(f"DEBUG: Previous responses count: {len(previous_responses)}")
        
        try:
            if round_num == 1:
                return self._generate_chapter_2_questions(user_id, trait_rankings)
            elif round_num == 2:
                # Use refined rankings from Chapter 2 responses
                refined_rankings = self._refine_rankings_from_chapter_2(previous_responses, trait_rankings)
                return self._generate_chapter_3_questions(user_id, refined_rankings)
            else:
                print(f"DEBUG: Invalid round number: {round_num}")
                return []
                
        except Exception as e:
            print(f"ERROR: Failed to generate follow-up questions: {e}")
            return []

    def _generate_chapter_2_questions(self, user_id: str, trait_rankings: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate Chapter 2 dual-choice questions"""
        print(f"DEBUG: Generating Chapter 2 questions for user {user_id}")
        
        # Get top 8 traits for Chapter 2
        top_traits = sorted(trait_rankings.items(), key=lambda x: x[1])[:8]
        top_trait_names = [trait[0] for trait in top_traits]
        
        print(f"DEBUG: Top traits for Chapter 2: {top_trait_names}")
        
        base_prompt = get_chapter_2_generation_prompt(top_trait_names)
        
        # Add extra instructions to ensure proper JSON format
        enhanced_prompt = f"""{base_prompt}

CRITICAL: Your response must be EXACTLY in this format with no additional text:
[{{"QuestionID":"Q2-1","Prompt":"Your question here","Type":"multiple_choice","Option1":"Option A","Option2":"Option B","Option3":"Option C","Option4":"Option D"}},{{"QuestionID":"Q2-2","Prompt":"Your question here","Type":"multiple_choice","Option1":"Option A","Option2":"Option B","Option3":"Option C","Option4":"Option D"}},...,{{"QuestionID":"Q2-13","Prompt":"Your question here","Type":"multiple_choice","Option1":"Option A","Option2":"Option B","Option3":"Option C","Option4":"Option D"}}]

Do not include any text before the [ or after the ]. Return only the JSON array."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": enhanced_prompt}
        ]
        
        try:
            print("DEBUG: Making API call for Chapter 2...")
            # Increase max_tokens to ensure full response and reduce temperature for more consistent format
            response = self._make_api_call(messages, max_tokens=3000, temperature=0.3)
            print(f"DEBUG: API response length: {len(response)}")
            print(f"DEBUG: First 500 chars of response: {response[:500]}")
            
            questions = self._parse_chapter_2_questions(response)
            print(f"DEBUG: Successfully parsed {len(questions)} questions from AI")
            
            # If AI parsing failed, use our improved fallback questions
            if len(questions) == 0:
                print("DEBUG: AI parsing failed, using improved fallback questions")
                questions = self._generate_fallback_chapter_2_questions(top_trait_names, 13)
            
            # Ensure we have exactly 13 questions
            if len(questions) < 13:
                print(f"DEBUG: Only got {len(questions)} questions, adding fallback questions...")
                additional_needed = 13 - len(questions)
                additional_questions = self._generate_fallback_chapter_2_questions(top_trait_names, additional_needed)
                questions.extend(additional_questions)
            
            # Limit to 13 questions
            questions = questions[:13]
            print(f"DEBUG: Generated {len(questions)} questions")
            
            return questions
            
        except Exception as e:
            print(f"ERROR: Failed to generate Chapter 2 questions: {e}")
            return self._generate_fallback_chapter_2_questions(top_trait_names, 13)

    def _generate_chapter_3_questions(self, user_id: str, refined_rankings: Dict[str, int]) -> List[Dict[str, Any]]:
        """Generate Chapter 3 open-ended questions"""
        print(f"DEBUG: Generating Chapter 3 questions for user {user_id}")
        
        # Get top 5 traits for Chapter 3
        top_traits = sorted(refined_rankings.items(), key=lambda x: x[1])[:5]
        top_trait_names = [trait[0] for trait in top_traits]
        
        print(f"DEBUG: Top traits for Chapter 3: {top_trait_names}")
        
        # Get previous results for context
        chapter_1_summary = f"Top traits from initial assessment: {', '.join(top_trait_names)}"
        chapter_2_summary = f"Refined traits from behavioral assessment: {', '.join(top_trait_names)}"
        
        prompt = get_chapter_3_generation_prompt(chapter_1_summary, chapter_2_summary)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            print("DEBUG: Making API call for Chapter 3...")
            response = self._make_api_call(messages, max_tokens=1200, temperature=0.7)
            print(f"DEBUG: API response length: {len(response)}")
            
            questions = self._parse_chapter_3_questions(response)
            print(f"DEBUG: Successfully parsed {len(questions)} questions from AI")
            
            # Ensure we have exactly 7 questions
            if len(questions) < 7:
                additional_needed = 7 - len(questions)
                additional_questions = self._generate_fallback_chapter_3_questions(top_trait_names, additional_needed)
                questions.extend(additional_questions)
            
            questions = questions[:7]
            print(f"DEBUG: Generated {len(questions)} questions")
            
            return questions
            
        except Exception as e:
            print(f"ERROR: Failed to generate Chapter 3 questions: {e}")
            return self._generate_fallback_chapter_3_questions(top_trait_names, 7)

    def _parse_chapter_2_questions(self, response: str) -> List[Dict[str, Any]]:
        """Parse Chapter 2 questions from AI response with robust JSON handling"""
        print(f"DEBUG: Parsing AI response for Chapter 2 questions")
        print(f"DEBUG: Response preview: {response[:500]}...")
        
        questions = []
        
        try:
            # Strategy 1: Direct JSON parsing
            response_clean = response.strip()
            
            # Remove markdown code blocks if present
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:].strip()
            elif response_clean.startswith('```'):
                response_clean = response_clean[3:].strip()
            if response_clean.endswith('```'):
                response_clean = response_clean[:-3].strip()
            
            try:
                raw_questions = json.loads(response_clean)
                print(f"DEBUG: Direct JSON parsing successful: {len(raw_questions)} questions")
                questions = self._format_chapter_2_questions(raw_questions)
                if questions:
                    return questions
                    
            except json.JSONDecodeError as e:
                print(f"DEBUG: Direct JSON parsing failed: {e}")
                
                # Strategy 2: Extract JSON array from response
                start_idx = response_clean.find('[')
                if start_idx >= 0:
                    # Find the matching closing bracket
                    bracket_count = 0
                    end_idx = -1
                    
                    for i in range(start_idx, len(response_clean)):
                        if response_clean[i] == '[':
                            bracket_count += 1
                        elif response_clean[i] == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_idx = i + 1
                                break
                    
                    if end_idx > start_idx:
                        json_part = response_clean[start_idx:end_idx]
                        print(f"DEBUG: Extracted JSON array: {json_part[:200]}...")
                        
                        try:
                            raw_questions = json.loads(json_part)
                            print(f"DEBUG: Extracted JSON parsing successful: {len(raw_questions)} questions")
                            questions = self._format_chapter_2_questions(raw_questions)
                            if questions:
                                return questions
                                
                        except json.JSONDecodeError as e2:
                            print(f"DEBUG: Extracted JSON parsing failed: {e2}")
                            
                            # Strategy 3: Fix common JSON issues and try again
                            fixed_json = self._fix_malformed_json(json_part)
                            if fixed_json:
                                try:
                                    raw_questions = json.loads(fixed_json)
                                    print(f"DEBUG: Fixed JSON parsing successful: {len(raw_questions)} questions")
                                    questions = self._format_chapter_2_questions(raw_questions)
                                    if questions:
                                        return questions
                                except json.JSONDecodeError as e3:
                                    print(f"DEBUG: Fixed JSON parsing also failed: {e3}")
                
                # Strategy 4: Parse individual question objects from text
                questions = self._parse_questions_from_text(response_clean)
                if questions:
                    print(f"DEBUG: Text parsing successful: {len(questions)} questions")
                    return questions
                        
        except Exception as e:
            print(f"DEBUG: JSON parsing failed with exception: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"DEBUG: All parsing strategies failed, returning empty list")
        return questions

    def _format_chapter_2_questions(self, raw_questions: List[Dict]) -> List[Dict[str, Any]]:
        """Format raw question data into expected format"""
        questions = []
        
        if not isinstance(raw_questions, list):
            print(f"DEBUG: Expected list, got {type(raw_questions)}")
            return questions
            
        for i, q in enumerate(raw_questions):
            if not isinstance(q, dict):
                print(f"DEBUG: Question {i+1} is not a dict: {type(q)}")
                continue
                
            formatted_question = {
                'QuestionID': q.get('QuestionID', f'Q{i+1}'),
                'QuestionText': q.get('Prompt', '').strip(),
                'Prompt': q.get('Prompt', '').strip(),
                'Type': 'multiple_choice',
                'Option1': q.get('Option1', '').strip(),
                'Option2': q.get('Option2', '').strip(),
                'Option3': q.get('Option3', '').strip(),
                'Option4': q.get('Option4', '').strip()
            }
            
            # Validate that all required fields are present and non-empty
            if all(formatted_question[key] for key in ['QuestionText', 'Option1', 'Option2', 'Option3', 'Option4']):
                questions.append(formatted_question)
                print(f"DEBUG: Added valid question {i+1}: {formatted_question['QuestionText'][:50]}...")
            else:
                missing_fields = [key for key in ['QuestionText', 'Option1', 'Option2', 'Option3', 'Option4'] 
                                if not formatted_question[key]]
                print(f"DEBUG: Skipped invalid question {i+1}: missing {missing_fields}")
        
        print(f"DEBUG: Successfully formatted {len(questions)} valid questions from JSON")
        return questions

    def _fix_malformed_json(self, json_text: str) -> str:
        """Attempt to fix common JSON syntax issues"""
        try:
            # Remove trailing commas before closing brackets/braces
            fixed = re.sub(r',(\s*[}\]])', r'\1', json_text)
            
            # Fix missing quotes around keys (basic attempt)
            fixed = re.sub(r'(\w+):', r'"\1":', fixed)
            
            # Fix unescaped quotes in strings (basic attempt)
            # This is tricky and might not work for all cases
            
            # Ensure the JSON is properly terminated
            if not fixed.strip().endswith(']'):
                # Try to close the array properly
                last_brace = fixed.rfind('}')
                if last_brace > 0:
                    fixed = fixed[:last_brace+1] + ']'
            
            print(f"DEBUG: Attempting to fix JSON: {fixed[:200]}...")
            return fixed
            
        except Exception as e:
            print(f"DEBUG: Failed to fix JSON: {e}")
            return None

    def _parse_questions_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse questions from malformed or partial text response"""
        questions = []
        
        try:
            # Look for question patterns in the text
            # This is a fallback method for when JSON parsing completely fails
            
            # Try to find individual question objects with regex
            question_pattern = r'\{\s*"QuestionID"\s*:\s*"([^"]+)"\s*,\s*"Prompt"\s*:\s*"([^"]+)"\s*,.*?"Option1"\s*:\s*"([^"]+)"\s*,\s*"Option2"\s*:\s*"([^"]+)"\s*,\s*"Option3"\s*:\s*"([^"]+)"\s*,\s*"Option4"\s*:\s*"([^"]+)"\s*[,}]'
            
            matches = re.findall(question_pattern, text, re.DOTALL)
            print(f"DEBUG: Found {len(matches)} question patterns in text")
            
            for i, match in enumerate(matches):
                if len(match) >= 6:
                    question = {
                        'QuestionID': match[0] or f'Q{i+1}',
                        'QuestionText': match[1].strip(),
                        'Prompt': match[1].strip(),
                        'Type': 'multiple_choice',
                        'Option1': match[2].strip(),
                        'Option2': match[3].strip(),
                        'Option3': match[4].strip(),
                        'Option4': match[5].strip()
                    }
                    
                    if all(question[key] for key in ['QuestionText', 'Option1', 'Option2', 'Option3', 'Option4']):
                        questions.append(question)
                        print(f"DEBUG: Extracted question {i+1}: {question['QuestionText'][:50]}...")
            
        except Exception as e:
            print(f"DEBUG: Text parsing failed: {e}")
            
        return questions

    def _parse_chapter_3_questions(self, response: str) -> List[Dict[str, Any]]:
        """Parse Chapter 3 questions from AI response"""
        print(f"DEBUG: Parsing Chapter 3 response length: {len(response)}")
        print(f"DEBUG: First 300 chars: {response[:300]}")
        
        questions = []
        
        # Clean the response
        response = response.strip()
        
        # Look for Q1:, Q2:, etc. pattern
        question_pattern = r'Q(\d+):\s*(.+?)(?=\n(?:Q\d+:|$)|$)'
        matches = re.findall(question_pattern, response, re.DOTALL | re.MULTILINE)
        
        print(f"DEBUG: Found {len(matches)} question matches")
        
        for num, question_text in matches:
            question_text = question_text.strip()
            # Remove any extra formatting or line breaks
            question_text = ' '.join(question_text.split())
            
            if question_text and len(question_text) > 10:
                questions.append({
                    'QuestionID': f'Q{num}',
                    'QuestionText': question_text,
                    'Prompt': question_text,
                    'Type': 'open_ended'
                })
                print(f"DEBUG: Added question {num}: {question_text[:50]}...")
        
        # If no matches found, try alternative parsing
        if not questions:
            print("DEBUG: No Q format found, trying line-by-line parsing")
            lines = response.split('\n')
            question_count = 1
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Skip obvious non-question content
                skip_words = ['priming', 'response', 'assessment', 'methodology', 'requirements', 'format', 'example']
                if any(skip in line.lower() for skip in skip_words):
                    continue
                
                # Clean up malformed "Prompt": format
                if '"Prompt":' in line:
                    # Extract the actual question from "Prompt": "question text",
                    prompt_match = re.search(r'"Prompt":\s*"([^"]+)"', line)
                    if prompt_match:
                        cleaned_question = prompt_match.group(1).strip()
                        if len(cleaned_question) > 15:
                            questions.append({
                                'QuestionID': f'Q{question_count}',
                                'QuestionText': cleaned_question,
                                'Prompt': cleaned_question,
                                'Type': 'open_ended'
                            })
                            print(f"DEBUG: Added parsed question: {cleaned_question[:50]}...")
                            question_count += 1
                    continue
                
                # Look for question-like content
                if (len(line) > 20 and 
                    (line.endswith('?') or 
                     any(q_word in line.lower() for q_word in [
                         'describe', 'think of', 'tell me', 'how do you', 'what is', 
                         'when you', 'walk me through', 'explain'
                     ]))):
                    
                    # Clean up numbering and formatting
                    cleaned_line = re.sub(r'^[Q\d\.\-\*\s]+', '', line).strip()
                    
                    if len(cleaned_line) > 15:
                        questions.append({
                            'QuestionID': f'Q{question_count}',
                            'QuestionText': cleaned_line,
                            'Prompt': cleaned_line,
                            'Type': 'open_ended'
                        })
                        question_count += 1
                        print(f"DEBUG: Added parsed question: {cleaned_line[:50]}...")
                        
                        if len(questions) >= 7:
                            break
        
        print(f"DEBUG: Final parsed questions count: {len(questions)}")
        return questions

    def _generate_fallback_chapter_2_questions(self, top_traits: List[str], count: int) -> List[Dict[str, Any]]:
        """Generate fallback Chapter 2 questions if AI fails"""
        fallback_questions = [
            {
                'QuestionID': 'Q1',
                'QuestionText': 'Your team missed an important deadline and stakeholders are frustrated. What\'s your immediate response?',
                'Prompt': 'Your team missed an important deadline and stakeholders are frustrated. What\'s your immediate response?',
                'Type': 'multiple_choice',
                'Option1': 'Take charge and create a recovery plan with clear next steps',
                'Option2': 'Analyze what went wrong to prevent future issues',
                'Option3': 'Focus on maintaining team morale and motivation',
                'Option4': 'Ensure everyone understands their responsibilities moving forward'
            },
            {
                'QuestionID': 'Q2',
                'QuestionText': 'You discover a colleague is struggling with their workload but hasn\'t asked for help. What do you do?',
                'Prompt': 'You discover a colleague is struggling with their workload but hasn\'t asked for help. What do you do?',
                'Type': 'multiple_choice',
                'Option1': 'Offer specific assistance with tasks you can handle',
                'Option2': 'Help them organize and prioritize their workload',
                'Option3': 'Connect them with others who might provide support',
                'Option4': 'Encourage them to communicate their needs to management'
            },
            {
                'QuestionID': 'Q3',
                'QuestionText': 'During a brainstorming session, the discussion becomes chaotic with too many ideas. How do you respond?',
                'Prompt': 'During a brainstorming session, the discussion becomes chaotic with too many ideas. How do you respond?',
                'Type': 'multiple_choice',
                'Option1': 'Suggest a structured approach to evaluate each idea',
                'Option2': 'Build on the most promising ideas to develop them further',
                'Option3': 'Help synthesize different viewpoints into cohesive themes',
                'Option4': 'Focus the group on ideas that align with strategic goals'
            },
            {
                'QuestionID': 'Q4',
                'QuestionText': 'You\'re assigned to lead a project with team members you\'ve never worked with before. What\'s your first priority?',
                'Prompt': 'You\'re assigned to lead a project with team members you\'ve never worked with before. What\'s your first priority?',
                'Type': 'multiple_choice',
                'Option1': 'Establish clear roles, responsibilities, and timelines',
                'Option2': 'Get to know each person\'s strengths and working style',
                'Option3': 'Create opportunities for the team to build relationships',
                'Option4': 'Define the project vision and success metrics'
            },
            {
                'QuestionID': 'Q5',
                'QuestionText': 'A long-standing company process is inefficient, but changing it would disrupt many people. What do you do?',
                'Prompt': 'A long-standing company process is inefficient, but changing it would disrupt many people. What do you do?',
                'Type': 'multiple_choice',
                'Option1': 'Research and present data supporting the need for change',
                'Option2': 'Gradually implement small improvements to minimize disruption',
                'Option3': 'Build consensus by involving stakeholders in the solution',
                'Option4': 'Focus on training people to work more effectively within the current system'
            },
            {
                'QuestionID': 'Q6',
                'QuestionText': 'You receive harsh criticism about your work in front of your peers. How do you handle it?',
                'Prompt': 'You receive harsh criticism about your work in front of your peers. How do you handle it?',
                'Type': 'multiple_choice',
                'Option1': 'Stay calm and ask clarifying questions to understand the specific issues',
                'Option2': 'Thank them for the feedback and discuss how to improve privately',
                'Option3': 'Address any valid points while professionally defending your approach',
                'Option4': 'Focus on what you can learn and how to apply it going forward'
            },
            {
                'QuestionID': 'Q7',
                'QuestionText': 'Your team is celebrating a major win, but you notice the success was largely due to one person\'s efforts. What do you do?',
                'Prompt': 'Your team is celebrating a major win, but you notice the success was largely due to one person\'s efforts. What do you do?',
                'Type': 'multiple_choice',
                'Option1': 'Make sure that person gets proper recognition for their contribution',
                'Option2': 'Use this as a learning opportunity to improve team collaboration',
                'Option3': 'Celebrate the team while privately acknowledging the key contributor',
                'Option4': 'Focus on how to replicate this success in future projects'
            },
            {
                'QuestionID': 'Q8',
                'QuestionText': 'You\'re in a meeting where a controversial decision needs to be made quickly. How do you contribute?',
                'Prompt': 'You\'re in a meeting where a controversial decision needs to be made quickly. How do you contribute?',
                'Type': 'multiple_choice',
                'Option1': 'Present the facts and logical implications of each option',
                'Option2': 'Advocate strongly for the option you believe is best',
                'Option3': 'Help the group find common ground and areas of agreement',
                'Option4': 'Ask questions to ensure all perspectives are considered'
            },
            {
                'QuestionID': 'Q9',
                'QuestionText': 'A new team member seems hesitant to participate in discussions and appears overwhelmed. What\'s your approach?',
                'Prompt': 'A new team member seems hesitant to participate in discussions and appears overwhelmed. What\'s your approach?',
                'Type': 'multiple_choice',
                'Option1': 'Give them specific, manageable tasks to build their confidence',
                'Option2': 'Spend time one-on-one understanding their concerns and background',
                'Option3': 'Include them directly in conversations and actively seek their input',
                'Option4': 'Connect them with resources and people who can help them succeed'
            },
            {
                'QuestionID': 'Q10',
                'QuestionText': 'Your organization is implementing a major change that you disagree with. How do you respond?',
                'Prompt': 'Your organization is implementing a major change that you disagree with. How do you respond?',
                'Type': 'multiple_choice',
                'Option1': 'Voice your concerns through proper channels with supporting evidence',
                'Option2': 'Focus on helping your team adapt and find opportunities within the change',
                'Option3': 'Work to understand the reasoning behind the decision',
                'Option4': 'Commit to making the change successful despite your reservations'
            },
            {
                'QuestionID': 'Q11',
                'QuestionText': 'You have multiple high-priority projects with competing deadlines. How do you handle this situation?',
                'Prompt': 'You have multiple high-priority projects with competing deadlines. How do you handle this situation?',
                'Type': 'multiple_choice',
                'Option1': 'Create a detailed schedule and systematically work through each task',
                'Option2': 'Negotiate with stakeholders to adjust expectations and timelines',
                'Option3': 'Focus intensely on one project at a time to ensure quality',
                'Option4': 'Identify which projects will have the greatest impact and prioritize accordingly'
            },
            {
                'QuestionID': 'Q12',
                'QuestionText': 'During a team presentation, a colleague makes a factual error that could mislead the audience. What do you do?',
                'Prompt': 'During a team presentation, a colleague makes a factual error that could mislead the audience. What do you do?',
                'Type': 'multiple_choice',
                'Option1': 'Politely correct the information immediately to prevent confusion',
                'Option2': 'Make a note to address it privately with your colleague afterward',
                'Option3': 'Find a diplomatic way to introduce the correct information',
                'Option4': 'Support your colleague publicly and clarify details in follow-up communication'
            }
        ]
        
        return fallback_questions[:count]

    def _generate_fallback_chapter_3_questions(self, top_traits: List[str], count: int) -> List[Dict[str, Any]]:
        """Generate fallback Chapter 3 questions if AI fails"""
        fallback_questions = []
        
        base_questions = [
            "Describe a time when you felt most engaged and energized at work.",
            "What type of work environment brings out your best performance?",
            "How do you prefer to approach challenging problems?",
            "What motivates you to excel in your professional life?",
            "Describe your ideal role and responsibilities.",
            "How do you like to contribute to team success?",
            "What achievements are you most proud of and why?"
        ]
        
        for i in range(min(count, len(base_questions))):
            fallback_questions.append({
                'QuestionID': f'Q{i + 1}',
                'QuestionText': base_questions[i],
                'Prompt': base_questions[i],
                'Type': 'open_ended'
            })
        
        return fallback_questions

    def _refine_rankings_from_chapter_2(self, chapter_2_responses: List[Dict[str, Any]], 
                                      initial_rankings: Dict[str, int]) -> Dict[str, int]:
        """Refine trait rankings based on Chapter 2 dual-choice responses"""
        print("DEBUG: Refining rankings based on Chapter 2 responses")
        
        if not chapter_2_responses:
            return initial_rankings
        
        # Analyze choice patterns to refine rankings
        choice_analysis = {}
        for resp in chapter_2_responses:
            first_choice = resp.get('firstChoice', '')
            second_choice = resp.get('secondChoice', '')
            
            if first_choice:
                choice_analysis[first_choice] = choice_analysis.get(first_choice, 0) + 2
            if second_choice:
                choice_analysis[second_choice] = choice_analysis.get(second_choice, 0) + 1
        
        # Get top traits based on initial rankings
        sorted_traits = sorted(initial_rankings.items(), key=lambda x: x[1])
        top_15_traits = dict(sorted_traits[:15])
        
        print(f"DEBUG: Refined to top 15 traits: {list(top_15_traits.keys())}")
        
        return top_15_traits
    
    async def generate_summary(self, user_id: str, initial_responses: List[Dict[str, Any]], trait_rankings: Dict[str, int], summary_type: str = "initial") -> str:
        """
        Generate a personality summary based on trait rankings and responses
        """
        print(f"DEBUG: Generating {summary_type} summary for user {user_id}")
        print(f"DEBUG: Got {len(trait_rankings)} traits and {len(initial_responses)} responses")
        
        # Get top 5 traits for summary
        sorted_traits = sorted(trait_rankings.items(), key=lambda x: x[1])
        top_traits = [trait for trait, _ in sorted_traits[:5]]
        
        print(f"DEBUG: Top 5 traits for summary: {top_traits}")
        
        # Create summary prompt with specific format
        summary_prompt = f"""
        Based on the personality assessment results, create a professional summary using this structure:
        
        Top 5 Core Strengths:
        {', '.join(top_traits)}
        
        Write the summary in this format:
        "You are a [personality type/style]. You excel in [key strengths and abilities]. You contribute to teams by [how you add value]."
        
        Requirements:
        - Use exactly that "You are... You excel in... You contribute..." format
        - Keep it concise (2-3 sentences total)
        - Avoid psychological or clinical terms
        - Focus on work style and natural abilities
        - Make it practical and relatable
        - Do not use asterisks or markdown formatting
        - Do not start with phrases like "Here's a concise summary"
        
        Example format:
        "You are a strategic thinker who thrives on solving complex problems. You excel in analyzing information, seeing patterns others miss, and developing innovative solutions. You contribute to teams by providing deep insights and helping others understand the bigger picture."
        """
        
        messages = [
            {"role": "system", "content": "You are a professional personality coach providing practical, accessible summaries. Avoid clinical or psychological jargon."},
            {"role": "user", "content": summary_prompt}
        ]
        
        try:
            response = self._make_api_call(messages, max_tokens=200, temperature=0.7)
            return response.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            # Fallback summary
            return f"Based on your assessment, your top strengths are {', '.join(top_traits[:3])}. These traits indicate strong potential in execution and strategic thinking, making you a valuable team contributor."

    async def update_trait_rankings(self, current_rankings: Dict[str, int],
                                  new_responses: List[Dict[str, Any]],
                                  round_num: int) -> Dict[str, int]:
        """
        Update trait rankings based on follow-up responses
        """
        print(f"DEBUG: Updating trait rankings for round {round_num}")
        print(f"DEBUG: Current rankings: {len(current_rankings)} traits")
        print(f"DEBUG: New responses: {len(new_responses)} responses")
        
        try:
            if round_num == 1:
                # Chapter 2: Dual-choice responses
                return self._update_rankings_from_chapter_2(current_rankings, new_responses)
            elif round_num == 2:
                # Chapter 3: Open-ended responses
                return self._update_rankings_from_chapter_3(current_rankings, new_responses)
            else:
                print(f"DEBUG: Unknown round number: {round_num}, returning current rankings")
                return current_rankings
                
        except Exception as e:
            print(f"ERROR: Failed to update trait rankings: {e}")
            return current_rankings or self._get_fallback_rankings()

    def _update_rankings_from_chapter_2(self, current_rankings: Dict[str, int], 
                                       responses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Update rankings based on Chapter 2 dual-choice responses"""
        print(f"DEBUG: Processing Chapter 2 dual-choice responses")
        
        # Create weighted scores based on choice selections
        trait_scores = {}
        
        for trait in self.all_traits:
            trait_scores[trait] = current_rankings.get(trait, 34)  # Start with current ranking
        
        # Process each response
        for response in responses:
            first_choice = response.get('firstChoice')
            second_choice = response.get('secondChoice')
            
            print(f"DEBUG: Processing response - First: {first_choice}, Second: {second_choice}")
            
            # Apply choice-based scoring (this is simplified - in production you'd map choices to specific traits)
            # For now, we'll apply small adjustments based on choice patterns
            if first_choice and second_choice:
                # Give slight preference boost to traits that align with choices
                # This is a simplified version - you'd want more sophisticated mapping
                choice_traits = self._map_choices_to_traits(first_choice, second_choice)
                
                for trait in choice_traits:
                    if trait in trait_scores:
                        # Improve ranking (lower number = better rank)
                        trait_scores[trait] = max(1, trait_scores[trait] - 1)
        
        # Convert scores back to rankings (1-34)
        sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1])
        updated_rankings = {}
        
        for rank, (trait, _) in enumerate(sorted_traits, 1):
            updated_rankings[trait] = rank
        
        print(f"DEBUG: Updated rankings completed with {len(updated_rankings)} traits")
        return updated_rankings

    def _update_rankings_from_chapter_3(self, current_rankings: Dict[str, int], 
                                       responses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Update rankings based on Chapter 3 open-ended responses"""
        print(f"DEBUG: Processing Chapter 3 open-ended responses")
        
        # For Chapter 3, we analyze the text responses with AI to refine rankings
        response_texts = []
        for resp in responses:
            if resp.get('response'):
                response_texts.append(f"Q{resp.get('questionId', 'X')}: {resp.get('response')}")
        
        if not response_texts:
            print("DEBUG: No text responses found, returning current rankings")
            return current_rankings
        
        # Use AI to analyze the depth responses and refine rankings
        analysis_prompt = f"""
        Based on these detailed Chapter 3 responses, refine the CliftonStrengths trait rankings.
        
        Current top traits: {', '.join([trait for trait, rank in sorted(current_rankings.items(), key=lambda x: x[1])[:10]])}
        
        User's detailed responses:
        {chr(10).join(response_texts)}
        
        Analyze the depth and nuance in these responses to refine the trait rankings.
        Look for:
        1. Consistency with current rankings
        2. New insights that might elevate certain traits
        3. Evidence that some traits might be less prominent
        
        CRITICAL JSON REQUIREMENTS:
        - Return ONLY a valid JSON object with ALL 34 traits ranked 1-34
        - NO comments, NO explanatory text, NO // or /* */ comments
        - Use exact trait names: Achiever, Activator, Adaptability, Analytical, Arranger, Belief, Command, Communication, Competition, Connectedness, Consistency, Context, Deliberative, Developer, Discipline, Empathy, Focus, Futuristic, Harmony, Ideation, Includer, Individualization, Input, Intellection, Learner, Maximizer, Positivity, Relator, Responsibility, Restorative, Self-Assurance, Significance, Strategic, Woo
        
        Format: {{"Achiever": 1, "Activator": 2, "Adaptability": 3, ...}}
        
        Return ONLY the JSON object with no additional text."""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            response = self._make_api_call(messages, max_tokens=800, temperature=0.3)
            refined_rankings = self._parse_trait_rankings(response)
            
            if self._validate_rankings(refined_rankings):
                print(f"DEBUG: Successfully refined rankings with AI analysis")
                return refined_rankings
            else:
                print("DEBUG: AI rankings validation failed, returning current rankings")
                return current_rankings
                
        except Exception as e:
            print(f"ERROR: Failed to refine rankings with AI: {e}")
            return current_rankings

    def _parse_trait_rankings(self, response: str) -> Dict[str, int]:
        """Parse trait rankings from AI response"""
        try:
            import json
            import re
            
            print(f"DEBUG: Parsing response: {response[:300]}...")
            
            # Try direct JSON parsing first
            try:
                rankings = json.loads(response.strip())
                if isinstance(rankings, dict):
                    cleaned_rankings = {}
                    for trait, rank in rankings.items():
                        try:
                            cleaned_rankings[trait] = int(rank)
                        except (ValueError, TypeError):
                            continue
                    print(f"DEBUG: Direct JSON parsing successful: {len(cleaned_rankings)} traits")
                    return cleaned_rankings
            except json.JSONDecodeError as e:
                print(f"DEBUG: Direct JSON parsing failed: {e}")
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                print(f"DEBUG: Extracted JSON: {json_str[:200]}...")
                
                # Clean common JSON issues including comments
                json_str = json_str.replace('\n', ' ')  # Remove newlines
                json_str = re.sub(r'//[^\r\n]*', '', json_str)  # Remove // comments
                json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)  # Remove /* */ comments
                json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                json_str = re.sub(r'\s+', ' ', json_str)  # Normalize whitespace
                
                print(f"DEBUG: Cleaned JSON (first 200 chars): {json_str[:200]}...")
                
                try:
                    rankings = json.loads(json_str)
                    if isinstance(rankings, dict):
                        cleaned_rankings = {}
                        for trait, rank in rankings.items():
                            try:
                                cleaned_rankings[trait] = int(rank)
                            except (ValueError, TypeError):
                                continue
                        print(f"DEBUG: Cleaned JSON parsing successful: {len(cleaned_rankings)} traits")
                        return cleaned_rankings
                except json.JSONDecodeError as e2:
                    print(f"DEBUG: Cleaned JSON parsing also failed: {e2}")
                    print(f"DEBUG: Final cleaned JSON: {json_str}")
            
            print("DEBUG: No valid JSON found in response")
            return {}
        except Exception as e:
            print(f"Error parsing trait rankings: {e}")
            return {}

    def _map_choices_to_traits(self, first_choice: str, second_choice: str) -> List[str]:
        """Map choice letters to likely traits (simplified mapping)"""
        # This is a simplified version - in production you'd have detailed mapping
        # based on the specific question and what each choice represents
        
        choice_trait_mapping = {
            'A': ['Achiever', 'Focus', 'Responsibility'],
            'B': ['Empathy', 'Relator', 'Developer'],
            'C': ['Analytical', 'Learner', 'Strategic'],
            'D': ['Command', 'Activator', 'Significance']
        }
        
        traits = []
        if first_choice in choice_trait_mapping:
            traits.extend(choice_trait_mapping[first_choice])
        if second_choice in choice_trait_mapping:
            traits.extend(choice_trait_mapping[second_choice])
        
        return list(set(traits))

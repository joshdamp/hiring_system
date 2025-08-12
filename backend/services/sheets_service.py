import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os
import asyncio
import time
from typing import List, Dict, Any, Optional

class SheetsService:
    def __init__(self):
        """Initialize Google Sheets service with credentials"""
        self.spreadsheet_name = "Your_Hiring_System_Data"
        self.gc = None
        self.spreadsheet = None
        self.last_write_time = 0
        self.min_write_interval = 2
        self._initialize_credentials()
    
    async def _rate_limit(self):
        """Ensure we don't exceed Google Sheets rate limits"""
        current_time = time.time()
        time_since_last_write = current_time - self.last_write_time
        
        if time_since_last_write < self.min_write_interval:
            wait_time = self.min_write_interval - time_since_last_write
            await asyncio.sleep(wait_time)
        
        self.last_write_time = time.time()
    
    def _initialize_credentials(self):
        """Initialize Google Sheets credentials"""
        try:
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Use environment variables with fallbacks
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
            spreadsheet_id = os.getenv('GOOGLE_SHEET_ID', '14eHVi6M0nkRf9u2SJ26FFqWp0dNYw05hsFcuCi5rty0')
            
            # Try environment variables first (for production)
            if all([
                os.getenv('GOOGLE_TYPE'),
                os.getenv('GOOGLE_PROJECT_ID'),
                os.getenv('GOOGLE_PRIVATE_KEY'),
                os.getenv('GOOGLE_CLIENT_EMAIL')
            ]):
                # Create credentials from environment variables
                credentials_info = {
                    "type": os.getenv('GOOGLE_TYPE'),
                    "project_id": os.getenv('GOOGLE_PROJECT_ID'),
                    "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
                    "private_key": os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n'),
                    "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                    "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                    "auth_uri": os.getenv('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                    "token_uri": os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                    "auth_provider_x509_cert_url": os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
                    "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL')
                }
                creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
            elif os.path.exists(credentials_path):
                # Fallback to credentials file for local development
                creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
            else:
                raise Exception("No Google credentials found")
            
            self.gc = gspread.authorize(creds)
            self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
            print(f"Successfully connected to Google Sheets: {spreadsheet_id}")
            
        except Exception as e:
            print(f"CRITICAL: Failed to initialize Google Sheets: {e}")
            print("Environment variables check:")
            print(f"GOOGLE_TYPE: {os.getenv('GOOGLE_TYPE')}")
            print(f"GOOGLE_PROJECT_ID: {os.getenv('GOOGLE_PROJECT_ID')}")
            print(f"GOOGLE_CLIENT_EMAIL: {os.getenv('GOOGLE_CLIENT_EMAIL')}")
            print(f"GOOGLE_SHEET_ID: {spreadsheet_id}")
            # Don't fall back to mock - raise the error
            raise Exception(f"Google Sheets connection failed: {e}")
    
    def _create_mock_service(self):
        """Create a mock service for development/testing"""
        print("Using mock Google Sheets service")
        self.gc = None
        self.spreadsheet = None

    async def save_user_info(self, user_data: Dict[str, Any]) -> bool:
        """Save user information to the first available sheet"""
        try:
            await self._rate_limit()
            
            if not self.spreadsheet:
                print("Mock mode: Would save user data to Google Sheets")
                print(f"User data: {user_data}")
                return True
            
            print(f"Saving user data to Google Sheets: {user_data}")
            
            # Try different possible worksheet names
            worksheet = None
            possible_names = ["User_Profiles", "User_Info", "Sheet1", "Users", "UserData"]
            
            for sheet_name in possible_names:
                try:
                    worksheet = self.spreadsheet.worksheet(sheet_name)
                    print(f"Found worksheet: {sheet_name}")
                    break
                except Exception as e:
                    print(f"Worksheet '{sheet_name}' not found: {e}")
                    continue
            
            if not worksheet:
                # Get the first available worksheet
                worksheets = self.spreadsheet.worksheets()
                if worksheets:
                    worksheet = worksheets[0]
                    print(f"Using first available worksheet: {worksheet.title}")
                else:
                    raise Exception("No worksheets found in spreadsheet")
            
            # Map to your actual Google Sheets columns: UserID | Name | Email | Age | Experience | Phone | Consent | Timestamp
            row_data = [
                user_data.get('userId', ''),
                user_data.get('name', ''),
                user_data.get('email', ''),
                user_data.get('age', ''),
                user_data.get('experience', ''),
                user_data.get('phone', ''),
                user_data.get('consent', ''),
                user_data.get('timestamp', '')
            ]
            
            print(f"Attempting to append row with correct column mapping: {row_data}")
            result = worksheet.append_row(row_data)
            print(f"Google Sheets append result: {result}")
            
            return True
            
        except Exception as e:
            print(f"ERROR saving to Google Sheets: {str(e)}")
            print(f"Exception type: {type(e)}")
            # Re-raise the exception so we know about failures
            raise e

    async def get_fixed_questions(self) -> List[Dict[str, Any]]:
        """Get Likert scale questions from the spreadsheet"""
        try:
            if not self.spreadsheet:
                return self._get_mock_likert_questions()
            
            worksheet = self.spreadsheet.worksheet("Fixed_Questions")
            # Get all values and skip the header row (first row)
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:  # Only header or empty
                print("No data rows found, using mock questions")
                return self._get_mock_likert_questions()
            
            # Skip header row (index 0) and process data rows
            questions = []
            for row in all_values[1:]:  # Skip first row (headers)
                if len(row) >= 4 and row[0].strip():  # Ensure we have all required columns and QuestionID is not empty
                    questions.append({
                        "QuestionID": row[0].strip(),
                        "LeftStatement": row[1].strip(),
                        "RightStatement": row[2].strip(),
                        "Theme": row[3].strip()
                    })
            
            print(f"Loaded {len(questions)} questions from Google Sheets")
            return questions
            
        except Exception as e:
            print(f"Error loading questions from sheets: {e}")
            return self._get_mock_likert_questions()
    
    def _get_mock_likert_questions(self) -> List[Dict[str, Any]]:
        """Return mock Likert scale questions for development"""
        return [
            # Strategic Theme (Q001-Q004)
            {
                "QuestionID": "Q001",
                "LeftStatement": "I enjoy imagining what the future could look like",
                "RightStatement": "I prefer dealing with today, not the future",
                "Theme": "Strategic"
            },
            {
                "QuestionID": "Q002", 
                "LeftStatement": "I like to analyze complex problems before making decisions",
                "RightStatement": "I prefer to make quick decisions and adjust later",
                "Theme": "Strategic"
            },
            {
                "QuestionID": "Q003",
                "LeftStatement": "I enjoy setting long-term goals and plans",
                "RightStatement": "I prefer to focus on immediate priorities",
                "Theme": "Strategic"
            },
            {
                "QuestionID": "Q004",
                "LeftStatement": "I like to consider multiple options before choosing",
                "RightStatement": "I prefer to go with my first instinct",
                "Theme": "Strategic"
            },
            # Executing Theme (Q005-Q008)
            {
                "QuestionID": "Q005",
                "LeftStatement": "I plan things out in detail before starting",
                "RightStatement": "I prefer to be flexible and adapt as I go",
                "Theme": "Executing"
            },
            {
                "QuestionID": "Q006",
                "LeftStatement": "I focus on completing tasks efficiently",
                "RightStatement": "I focus on ensuring quality over speed",
                "Theme": "Executing"
            },
            {
                "QuestionID": "Q007",
                "LeftStatement": "I prefer clear rules and procedures",
                "RightStatement": "I prefer creative freedom and flexibility",
                "Theme": "Executing"
            },
            {
                "QuestionID": "Q008",
                "LeftStatement": "I like to finish one task before starting another",
                "RightStatement": "I like to work on multiple tasks simultaneously",
                "Theme": "Executing"
            },
            # Influencing Theme (Q009-Q012)
            {
                "QuestionID": "Q009",
                "LeftStatement": "I speak up in group discussions",
                "RightStatement": "I prefer to listen and observe in groups",
                "Theme": "Influencing"
            },
            {
                "QuestionID": "Q010",
                "LeftStatement": "I enjoy convincing others to see my point of view",
                "RightStatement": "I prefer to understand others' perspectives first",
                "Theme": "Influencing"
            },
            {
                "QuestionID": "Q011",
                "LeftStatement": "I like to take charge in group situations",
                "RightStatement": "I prefer to support others who take the lead",
                "Theme": "Influencing"
            },
            {
                "QuestionID": "Q012",
                "LeftStatement": "I enjoy presenting ideas to large groups",
                "RightStatement": "I prefer one-on-one conversations",
                "Theme": "Influencing"
            },
            # Relationship Building Theme (Q013-Q016)
            {
                "QuestionID": "Q013",
                "LeftStatement": "I feel energized by social interactions",
                "RightStatement": "I feel energized by quiet reflection",
                "Theme": "Relationship Building"
            },
            {
                "QuestionID": "Q014",
                "LeftStatement": "I like to work in teams and collaborate",
                "RightStatement": "I prefer to work independently",
                "Theme": "Relationship Building"
            },
            {
                "QuestionID": "Q015",
                "LeftStatement": "I make decisions based on feelings and values",
                "RightStatement": "I make decisions based on logic and facts",
                "Theme": "Relationship Building"
            },
            {
                "QuestionID": "Q016",
                "LeftStatement": "I focus on building relationships with people",
                "RightStatement": "I focus on completing tasks efficiently",
                "Theme": "Relationship Building"
            }
        ]

    async def save_initial_responses(self, user_id: str, responses: List[Dict[str, Any]]) -> bool:
        """Save initial assessment responses"""
        try:
            await self._rate_limit()
            
            if not self.spreadsheet:
                return True
            
            worksheet = self.spreadsheet.worksheet("User_Response_Initial")
            
            for response in responses:
                row_data = [
                    user_id,
                    response.get('questionId', ''),
                    response.get('response', ''),
                    response.get('timestamp', '')
                ]
                worksheet.append_row(row_data)
                await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            return False

    async def save_follow_up_questions(self, user_id: str, questions: List[Dict[str, Any]], round_num: int) -> bool:
        """Save generated follow-up questions"""
        try:
            await self._rate_limit()
            
            if not self.spreadsheet:
                return True
            
            # Get user name
            user_name = await self.get_user_name(user_id)
            
            sheet_name = f"Follow_Up_Questions{round_num}"
            
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                worksheet.append_row(["UserID", "Name", "QuestionID", "QuestionText", "OptionA", "OptionB", "OptionC", "OptionD"])
            
            for question in questions:
                row_data = [
                    user_id,                                                    # UserId
                    user_name,                                                  # UserName  
                    question.get('questionId', question.get('QuestionID', '')), # QuestionID
                    question.get('question', question.get('Prompt', question.get('QuestionText', ''))),  # QuestionText
                    question.get('Option1', ''),                               # OptionA
                    question.get('Option2', ''),                               # OptionB
                    question.get('Option3', ''),                               # OptionC
                    question.get('Option4', '')                                # OptionD
                ]
                worksheet.append_row(row_data)
                await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            return False

    async def save_follow_up_responses(self, user_id: str, responses: List[Dict[str, Any]], round_num: int) -> bool:
        """Save follow-up responses - handles both single responses and dual choices"""
        try:
            await self._rate_limit()
            
            if not self.spreadsheet:
                return True
            
            # Get user name
            user_name = await self.get_user_name(user_id)
            
            sheet_name = f"User_Response_Follow_Up_{round_num}"
            
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                
                # Create appropriate headers based on round
                if round_num == 1:
                    # Chapter 2: Dual-choice format (round 1)
                    worksheet.append_row(["UserId", "Name", "QuestionID", "FirstChoice", "SecondChoice", "Timestamp"])
                else:
                    # Chapter 3: Regular text response format (round 2)
                    worksheet.append_row(["UserId", "Name", "QuestionID", "Response", "Timestamp"])
            
            for response in responses:
                if round_num == 1:
                    # Chapter 2: Dual-choice responses (round 1)
                    row_data = [
                        user_id,
                        user_name,
                        response.get('questionId', ''),
                        response.get('firstChoice', ''),
                        response.get('secondChoice', ''),
                        response.get('timestamp', '')
                    ]
                else:
                    # Chapter 3: Regular text responses (round 2)
                    row_data = [
                        user_id,
                        user_name,
                        response.get('questionId', ''),
                        response.get('response', ''),
                        response.get('timestamp', '')
                    ]
                
                worksheet.append_row(row_data)
                await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"Error saving follow-up responses: {e}")
            return False

    async def get_user_responses(self, user_id: str, sheet_name: str) -> List[Dict[str, Any]]:
        """Get user responses from a specific sheet"""
        try:
            if not self.spreadsheet:
                return []
            
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
                records = worksheet.get_all_records()
                
                user_responses = []
                for record in records:
                    if record.get('UserId') == user_id:
                        user_responses.append(record)
                
                return user_responses
            except:
                return []
            
        except Exception as e:
            return []

    async def get_user_name(self, user_id: str) -> str:
        """Get user name from User_Profiles sheet"""
        try:
            if not self.spreadsheet:
                return "Unknown User"
            
            
            # Try User_Profiles first, then User_Info as fallback
            for sheet_name in ["User_Profiles", "User_Info"]:
                try:
                    worksheet = self.spreadsheet.worksheet(sheet_name)
                    records = worksheet.get_all_records()
                    
                    
                    for i, record in enumerate(records):
                        
                        # Check both userId and UserId fields - handle case variations
                        record_user_id = (record.get('userId') or record.get('UserId') or 
                                        record.get('UserID') or record.get('userid'))
                        
                        if record_user_id == user_id:
                            # Try different possible name fields - check Name first (capital N)
                            name = (record.get('Name') or record.get('name') or 
                                  record.get('UserName') or record.get('username'))
                            
                            if name:
                                return name
                            
                            # Fallback to firstName + lastName
                            first_name = record.get('firstName', '') or record.get('FirstName', '')
                            last_name = record.get('lastName', '') or record.get('LastName', '')
                            full_name = f"{first_name} {last_name}".strip()
                            if full_name:
                                return full_name
                    
                    break  # If we found the sheet, don't try the fallback
                except Exception as e:
                    continue
            
            return "Unknown User"
            
        except Exception as e:
            print(f"Error getting user name: {e}")
            return "Unknown User"
    
    async def save_final_results(self, user_id: str, name: str, trait_rankings: Dict[str, int], summary_text: str = "") -> bool:
        """Save final trait rankings and summary to Final_Results sheet with all 34 CliftonStrengths"""
        try:
            await self._rate_limit()
            
            if not self.spreadsheet:
                print(f"Mock mode: Would save final results for {user_id} - {name}")
                print(f"Trait rankings: {trait_rankings}")
                print(f"Summary: {summary_text[:100]}...")
                return True
            
            worksheet = self.spreadsheet.worksheet("Final_Results")
            
            # Check if this user's results already exist
            existing_data = worksheet.get_all_values()
            for row in existing_data:
                if row and user_id in str(row[0]):
                    print(f"Results for user {user_id} already exist, skipping...")
                    return True
            
            # Check if this is the first entry (add headers)
            try:
                if not existing_data or (len(existing_data) == 1 and not existing_data[0][0]):
                    # Add headers
                    headers = ["UserID & Name", "Traits", "Ranking", "Summary"]
                    worksheet.clear()
                    worksheet.append_row(headers)
            except Exception:
                # If worksheet doesn't exist or is empty, create headers
                headers = ["UserID & Name", "Traits", "Ranking", "Summary"]
                worksheet.clear()
                worksheet.append_row(headers)
            
            # Add user info row with summary in the last column
            user_info_row = [f"{user_id} {name}", "", "", summary_text]
            worksheet.append_row(user_info_row)
            
            # Add all 34 traits with their rankings
            # Define the standard order of CliftonStrengths
            all_clifton_strengths = [
                "Strategic", "Activator", "Command", "Significance", "Futuristic",
                "Individualization", "Maximizer", "Competition", "Self-Assurance", "Ideation",
                "Focus", "Communication", "Input", "Achiever", "Learner",
                "Responsibility", "Restorative", "Analytical", "Arranger", "Developer",
                "Intellection", "Empathy", "Belief", "Relator", "Adaptability",
                "Positivity", "Connectedness", "Context", "Woo", "Discipline",
                "Deliberative", "Includer", "Harmony", "Consistency"
            ]
            
            # Add each trait with its ranking
            for trait in all_clifton_strengths:
                ranking = trait_rankings.get(trait, 35)  # Default to 35 if trait not found
                trait_row = ["", trait, ranking, ""]
                worksheet.append_row(trait_row)
            
            # Add empty row for separation
            worksheet.append_row(["", "", "", ""])
            
            return True
            
        except Exception as e:
            print(f"Error saving final results: {e}")
            return False

    async def get_final_results(self, user_id: str) -> Dict:
        """Retrieve final results and summary from Final_Results sheet"""
        try:
            await self._rate_limit()
            
            if not self.spreadsheet:
                print(f"Mock mode: Would get final results for {user_id}")
                return None
            
            worksheet = self.spreadsheet.worksheet("Final_Results")
            all_data = worksheet.get_all_values()
            
            if not all_data:
                return None
            
            # Find the user's data
            user_data_start = None
            for i, row in enumerate(all_data):
                if row and user_id in str(row[0]):
                    user_data_start = i
                    break
            
            if user_data_start is None:
                return None
            
            # Extract user info and summary
            user_row = all_data[user_data_start]
            user_name = user_row[0].replace(user_id, "").strip()
            summary_text = user_row[3] if len(user_row) > 3 else ""
            
            # Extract trait rankings
            trait_rankings = {}
            for i in range(user_data_start + 1, len(all_data)):
                row = all_data[i]
                if not row or not row[1]:  # Empty row or no trait name
                    break
                if len(row) >= 3 and row[1] and row[2]:
                    trait_name = row[1].strip()
                    try:
                        ranking = int(row[2])
                        trait_rankings[trait_name] = ranking
                    except (ValueError, IndexError):
                        continue
            
            return {
                "user_id": user_id,
                "user_name": user_name,
                "trait_rankings": trait_rankings,
                "summary_text": summary_text
            }
            
        except Exception as e:
            print(f"Error getting final results: {e}")
            return None

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
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
            
            if os.path.exists(credentials_path):
                creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
                self.gc = gspread.authorize(creds)
                self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
            else:
                raise Exception("credentials.json not found")
            
        except Exception as e:
            self._create_mock_service()
    
    def _create_mock_service(self):
        """Create a mock service for development/testing"""
        self.gc = None
        self.spreadsheet = None

    async def save_user_info(self, user_data: Dict[str, Any]) -> bool:
        """Save user information to User_Info sheet"""
        try:
            await self._rate_limit()
            
            if not self.spreadsheet:
                return True
            
            worksheet = self.spreadsheet.worksheet("User_Info")
            
            row_data = [
                user_data.get('userId', ''),
                user_data.get('name', ''),
                user_data.get('email', ''),
                user_data.get('phone', ''),
                user_data.get('experience', ''),
                user_data.get('position', ''),
                user_data.get('timestamp', '')
            ]
            worksheet.append_row(row_data)
            
            return True
            
        except Exception as e:
            return False

    async def get_fixed_questions(self) -> List[Dict[str, Any]]:
        """Get fixed questions from the spreadsheet"""
        try:
            if not self.spreadsheet:
                return self._get_mock_fixed_questions()
            
            worksheet = self.spreadsheet.worksheet("Fixed_Questions")
            records = worksheet.get_all_records()
            
            questions = []
            for record in records:
                questions.append({
                    "QuestionID": record.get("QuestionID", ""),
                    "Prompt": record.get("Prompt", ""),
                    "Option1": record.get("Option1", ""),
                    "Option2": record.get("Option2", ""),
                    "Option3": record.get("Option3", ""),
                    "Option4": record.get("Option4", "")
                })
            
            return questions
            
        except Exception as e:
            return self._get_mock_fixed_questions()
    
    def _get_mock_fixed_questions(self) -> List[Dict[str, Any]]:
        """Return mock fixed questions for development"""
        return [
            {
                "QuestionID": "Q1",
                "Prompt": "When you post something and no one reacts to it, what do you usually do?",
                "Option1": "Wait and hope someone notices eventually",
                "Option2": "Ask for feedback so I can improve",
                "Option3": "Feel discouraged and stop posting for now",
                "Option4": "Keep going—results take time anyway"
            },
            {
                "QuestionID": "Q2",
                "Prompt": "When working on a team project, you typically:",
                "Option1": "Take charge and delegate tasks",
                "Option2": "Wait for others to assign you tasks",
                "Option3": "Suggest ideas and collaborate equally",
                "Option4": "Focus on your specific expertise area"
            },
            {
                "QuestionID": "Q3",
                "Prompt": "In stressful situations, you tend to:",
                "Option1": "Stay calm and think logically",
                "Option2": "Feel overwhelmed but push through",
                "Option3": "Seek support from others",
                "Option4": "Take breaks to recharge"
            },
            {
                "QuestionID": "Q4",
                "Prompt": "How do you prefer to learn new skills?",
                "Option1": "Hands-on practice and experimentation",
                "Option2": "Structured courses or tutorials",
                "Option3": "Learning from experienced colleagues",
                "Option4": "Reading documentation and best practices"
            },
            {
                "QuestionID": "Q5",
                "Prompt": "When receiving constructive feedback, you:",
                "Option1": "Ask clarifying questions to understand better",
                "Option2": "Take notes and create an improvement plan",
                "Option3": "Implement changes immediately",
                "Option4": "Reflect on the feedback before responding"
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
            
            sheet_name = f"Follow_Up_Questions{round_num}"
            
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                worksheet.append_row(["UserId", "QuestionID", "QuestionText"])
            
            for question in questions:
                row_data = [
                    user_id,
                    question.get('QuestionID', ''),
                    question.get('QuestionText', '')
                ]
                worksheet.append_row(row_data)
                await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            return False

    async def save_follow_up_responses(self, user_id: str, responses: List[Dict[str, Any]], round_num: int) -> bool:
        """Save follow-up responses"""
        try:
            await self._rate_limit()
            
            if not self.spreadsheet:
                return True
            
            sheet_name = f"User_Response_Follow_Up_{round_num}"
            
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                worksheet.append_row(["UserId", "QuestionID", "Response", "Timestamp"])
            
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

    async def save_final_results(self, user_id: str, name: str, traits: List[Dict[str, Any]]) -> bool:
        """Save final trait rankings to Final_Results sheet"""
        try:
            await self._rate_limit()
            
            if not self.spreadsheet:
                return True
            
            worksheet = self.spreadsheet.worksheet("Final_Results")
            
            traits_summary = " | ".join([f"{trait['name']}: {trait['score']:.1f}" for trait in traits])
            
            row_data = [
                user_id,
                name,
                datetime.now().isoformat(),
                traits_summary,
                json.dumps(traits)
            ]
            worksheet.append_row(row_data)
            
            return True
            
        except Exception as e:
            return False

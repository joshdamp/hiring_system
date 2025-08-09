"""
Theme Analysis Service for Likert Scale Responses
Analyzes user responses by theme categories: Strategic, Executing, Influencing, Relationship Building
"""

from typing import List, Dict, Any
from collections import defaultdict
import statistics

class ThemeAnalysisService:
    
    @staticmethod
    def analyze_responses_by_theme(responses: List[Dict[str, Any]], questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze user responses grouped by theme
        
        Args:
            responses: List of user responses [{"questionId": "Q001", "response": 4}, ...]
            questions: List of questions with themes [{"QuestionID": "Q001", "Theme": "Strategic"}, ...]
        
        Returns:
            Dict with theme analysis results
        """
        # Create question-to-theme mapping
        question_themes = {q.get("QuestionID"): q.get("Theme") for q in questions}
        
        # Group responses by theme
        theme_responses = defaultdict(list)
        
        for response in responses:
            question_id = response.get("questionId")
            response_value = response.get("response")
            theme = question_themes.get(question_id)
            
            if theme and response_value is not None:
                theme_responses[theme].append(response_value)
        
        # Calculate theme statistics
        theme_analysis = {}
        
        for theme, values in theme_responses.items():
            if values:
                theme_analysis[theme] = {
                    "average_score": round(statistics.mean(values), 2),
                    "total_questions": len(values),
                    "responses": values,
                    "strength_level": ThemeAnalysisService._get_strength_level(statistics.mean(values))
                }
        
        # Calculate overall profile
        overall_analysis = ThemeAnalysisService._generate_overall_profile(theme_analysis)
        
        return {
            "theme_scores": theme_analysis,
            "overall_profile": overall_analysis,
            "recommendations": ThemeAnalysisService._generate_recommendations(theme_analysis)
        }
    
    @staticmethod
    def _get_strength_level(average_score: float) -> str:
        """Convert average score to strength level description"""
        if average_score >= 4.0:
            return "Very Strong"
        elif average_score >= 3.5:
            return "Strong"
        elif average_score >= 2.5:
            return "Moderate"
        elif average_score >= 2.0:
            return "Developing"
        else:
            return "Area for Growth"
    
    @staticmethod
    def _generate_overall_profile(theme_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall personality profile summary"""
        if not theme_analysis:
            return {}
        
        # Find strongest and weakest themes
        theme_scores = {theme: data["average_score"] for theme, data in theme_analysis.items()}
        strongest_theme = max(theme_scores, key=theme_scores.get)
        weakest_theme = min(theme_scores, key=theme_scores.get)
        
        # Calculate overall balance
        scores = list(theme_scores.values())
        overall_average = statistics.mean(scores)
        score_variance = statistics.variance(scores) if len(scores) > 1 else 0
        
        balance_level = "Well-Balanced" if score_variance < 0.5 else "Specialized"
        
        return {
            "strongest_theme": strongest_theme,
            "weakest_theme": weakest_theme,
            "overall_average": round(overall_average, 2),
            "balance_level": balance_level,
            "profile_type": ThemeAnalysisService._determine_profile_type(theme_scores)
        }
    
    @staticmethod
    def _determine_profile_type(theme_scores: Dict[str, float]) -> str:
        """Determine personality profile type based on theme strengths"""
        # Find the highest scoring theme(s)
        max_score = max(theme_scores.values())
        top_themes = [theme for theme, score in theme_scores.items() if score >= max_score - 0.3]
        
        if len(top_themes) == 1:
            return f"{top_themes[0]}-Focused"
        elif len(top_themes) >= 3:
            return "Multi-Dimensional"
        else:
            return f"{'-'.join(sorted(top_themes))} Oriented"
    
    @staticmethod
    def _generate_recommendations(theme_analysis: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations based on theme analysis"""
        recommendations = []
        
        for theme, data in theme_analysis.items():
            avg_score = data["average_score"]
            
            if avg_score >= 4.0:
                recommendations.append(f"Leverage your strong {theme} abilities in leadership roles and challenging projects.")
            elif avg_score >= 3.0:
                recommendations.append(f"Continue developing your {theme} skills through targeted practice and feedback.")
            else:
                recommendations.append(f"Focus on building {theme} competencies through training and mentorship.")
        
        return recommendations
    
    @staticmethod
    def generate_hiring_insights(theme_analysis: Dict[str, Any], role_requirements: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Generate hiring insights based on theme analysis and role requirements
        
        Args:
            theme_analysis: Results from analyze_responses_by_theme
            role_requirements: Optional dict of required theme scores for the role
        
        Returns:
            Hiring recommendation insights
        """
        if not role_requirements:
            # Default role requirements (can be customized per position)
            role_requirements = {
                "Strategic": 3.0,
                "Executing": 3.5,
                "Influencing": 3.0,
                "Relationship Building": 3.5
            }
        
        theme_scores = theme_analysis.get("theme_scores", {})
        fit_analysis = {}
        
        for theme, required_score in role_requirements.items():
            user_score = theme_scores.get(theme, {}).get("average_score", 0)
            
            fit_analysis[theme] = {
                "user_score": user_score,
                "required_score": required_score,
                "meets_requirement": user_score >= required_score,
                "gap": round(required_score - user_score, 2) if user_score < required_score else 0
            }
        
        # Calculate overall fit percentage
        total_requirements = len(role_requirements)
        met_requirements = sum(1 for analysis in fit_analysis.values() if analysis["meets_requirement"])
        fit_percentage = (met_requirements / total_requirements) * 100 if total_requirements > 0 else 0
        
        return {
            "fit_analysis": fit_analysis,
            "overall_fit_percentage": round(fit_percentage, 1),
            "recommendation": "Strong Fit" if fit_percentage >= 75 else "Moderate Fit" if fit_percentage >= 50 else "Needs Development",
            "development_areas": [theme for theme, analysis in fit_analysis.items() if not analysis["meets_requirement"]]
        }

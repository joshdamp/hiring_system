"""
Test script to verify Groq AI service is working
Run this after setting up your GROQ_API_KEY
"""
import os
import sys
sys.path.append('.')

from services.groq_ai_service import GroqAIService

def test_groq_service():
    print("Testing Groq AI Service...")
    
    # Check if API key is set
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY not found!")
        print("Please set your API key:")
        print("1. Get free key from https://console.groq.com/")
        print("2. Create .env file with: GROQ_API_KEY=your_key_here")
        print("3. Or set environment variable")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Test AI service
    ai_service = GroqAIService()
    
    # Test simple API call
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Hello, Groq is working!' and nothing else."}
    ]
    
    response = ai_service._make_api_call(messages, max_tokens=50)
    
    if response:
        print(f"✅ API call successful: {response}")
        return True
    else:
        print("❌ API call failed!")
        print("Check your API key and internet connection")
        return False

if __name__ == "__main__":
    test_groq_service()

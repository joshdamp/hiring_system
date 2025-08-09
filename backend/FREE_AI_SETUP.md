# FREE AI API SETUP GUIDE

## Current Issue
The HuggingFace Inference API now requires authentication and is returning 401 errors, causing the system to always fall back to static data.

## Solution: Groq API (FREE & Fast)

### 1. Get Free Groq API Key
1. Go to https://console.groq.com/
2. Sign up for a free account (GitHub/Google signin works)
3. Go to "API Keys" section
4. Create a new API key
5. Copy the API key (starts with `gsk_...`)

### 2. Set Environment Variable

#### Option A: Create .env file (Recommended)
Create a `.env` file in the backend folder:
```
GROQ_API_KEY=your_api_key_here
```

#### Option B: Set in Windows PowerShell
```powershell
$env:GROQ_API_KEY="your_api_key_here"
```

#### Option C: Add to main.py
Add this line at the top of main.py:
```python
os.environ['GROQ_API_KEY'] = 'your_api_key_here'
```

### 3. Install Required Package
```bash
pip install python-dotenv
```

## Groq Benefits
- ✅ **Completely FREE**: 14,400 requests/day
- ✅ **Very Fast**: Sub-second response times
- ✅ **High Quality**: Llama 3.1 70B model
- ✅ **Reliable**: Much more stable than HuggingFace
- ✅ **No Rate Limiting**: Within free tier limits

## Alternative Free Options

### 1. Ollama (Local, Unlimited)
- Download from https://ollama.ai/
- Run `ollama pull llama3.1`
- Completely free, runs on your computer
- No API keys needed

### 2. Google AI Studio (Gemini)
- Go to https://aistudio.google.com/
- Free tier: 15 requests/minute, 1,500/day
- Very capable Gemini models

### 3. Cohere (Limited Free)
- Go to https://cohere.ai/
- 1,000 API calls/month free
- Good for text generation

## Current Implementation
The system has been updated to use Groq API instead of HuggingFace. Just add your free API key and restart the backend.

## Testing
After setting up the API key, the system will:
- Generate unique trait rankings for each user
- Create personalized follow-up questions
- Generate custom personality summaries
- Stop using fallback data

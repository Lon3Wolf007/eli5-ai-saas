from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ELI5.ai API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("⚠️  Warning: No API key found! Set OPENAI_API_KEY in .env file")
client = OpenAI(api_key=api_key) if api_key else None


class ExplainRequest(BaseModel):
    topic: str
    complexity: str = "eli5"


@app.get("/")
async def root():
    return {
        "message": "Welcome to ELI5.ai API!",
        "status": "Server is running 🚀",
        "model": "GPT-4o-mini (Fast & Reliable)",
        "endpoints": {
            "/explain": "POST - Get ELI5 explanation",
            "/health": "GET - Check server health"
        }
    }


@app.get("/health")
async def health():
    api_status = "connected" if client else "no API key"
    return {
        "status": "healthy",
        "api": api_status,
        "model": "GPT-4o-mini"
    }


@app.post("/explain")
async def explain_topic(request: ExplainRequest):
    if not client:
        raise HTTPException(
            status_code=500,
            detail="API key not configured. Please set OPENAI_API_KEY in .env file"
        )
    
    if not request.topic or len(request.topic.strip()) == 0:
        raise HTTPException(
            status_code=400,
            detail="Please provide a topic to explain"
        )
    
    complexity_prompts = {
        "eli5": "Explain this like I'm 5 years old, using very simple words and fun examples:",
        "eli10": "Explain this like I'm 10 years old, using clear language and relatable examples:",
        "teen": "Explain this like I'm a teenager, with some detail but still easy to understand:",
        "college": "Explain this at a college level with proper terminology:",
        "expert": "Explain this with full technical detail for an expert:"
    }
    
    complexity_instruction = complexity_prompts.get(
        request.complexity,
        complexity_prompts["eli5"]
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a friendly AI tutor that explains complex topics in simple, engaging ways. Use analogies, examples, and a conversational tone."
                },
                {
                    "role": "user",
                    "content": f"{complexity_instruction}\n\nTopic: {request.topic}\n\nPlease provide a clear, engaging explanation with examples. Keep it friendly and conversational!"
                }
            ],
            max_tokens=1024,
            temperature=0.7
        )
        
        explanation = response.choices[0].message.content
        
        return {
            "success": True,
            "topic": request.topic,
            "complexity": request.complexity,
            "explanation": explanation,
            "tokens_used": response.usage.total_tokens,
            "model": "GPT-4o-mini",
            "cost": f"${response.usage.total_tokens * 0.0000015:.6f}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ELI5.ai Backend Server...")
    print("📍 Server will run on: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    print("🤖 Using OpenAI GPT-4o-mini - Fast & Reliable!")
    print("💰 ~$0.0015 per explanation (your $5 = ~3,300 explanations!)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
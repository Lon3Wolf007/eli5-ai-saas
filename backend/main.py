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
        "model": "GPT-4o-mini (Optimized)",
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
    
    complexity_configs = {
        "eli5": {
            "instruction": "Explain in 5-10 sentences using simple words a 5-year-old would understand. Use a fun analogy.",
            "max_tokens": 150,
            "temperature": 0.7
        },
        "eli10": {
            "instruction": "Explain in 3-4 sentences for a 10-year-old. Use clear, relatable examples. Break into 2 short paragraphs.",
            "max_tokens": 200,
            "temperature": 0.7
        },
        "teen": {
            "instruction": "Explain in 4-5 sentences for a teenager. Include some detail but keep it interesting. Use 2 paragraphs.",
            "max_tokens": 250,
            "temperature": 0.7
        },
        "college": {
            "instruction": "Provide a concise college-level explanation in 5-6 sentences. Use proper terminology. Structure in 2-3 short paragraphs.",
            "max_tokens": 300,
            "temperature": 0.6
        },
        "expert": {
            "instruction": "Provide an expert-level technical explanation using advanced terminology, academic language, and field-specific jargon. Be precise and sophisticated. 3 paragraphs max. Sound impressive and authoritative.",
            "max_tokens": 350,
            "temperature": 0.5
        }
    }
    
    config = complexity_configs.get(request.complexity, complexity_configs["eli5"])
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise AI tutor. Keep explanations SHORT and TO THE POINT. Always break longer answers into short paragraphs for readability. No fluff or unnecessary details."
                },
                {
                    "role": "user",
                    "content": f"{config['instruction']}\n\nTopic: {request.topic}\n\nBe concise and clear. Use paragraph breaks for readability."
                }
            ],
            max_tokens=config["max_tokens"],
            temperature=config["temperature"]
        )
        
        explanation = response.choices[0].message.content.strip()
        
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
    print("🚀 Starting ELI5.ai Backend Server (OPTIMIZED)...")
    print("📍 Server will run on: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    print("🤖 Using OpenAI GPT-4o-mini - Optimized for cost!")
    print("💰 Reduced tokens = More explanations per dollar!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException
from typing import Optional, Any
from workers.ai_chatbot import run_agent_for_prompt
import logging
import sys
import os
from model import ChatRequest, ChatResponse 


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ai_services")

app = FastAPI(title="AI Services", version="1.0.0")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received chat request: {request.prompt}")
        result = await run_agent_for_prompt(request.prompt)
        
        # The agent runner might return a complex object or just the result.
        # We try to extract 'final_output' which is common in some agent frameworks,
        # or convert the whole result to string.
        final_text = getattr(result, "final_output", str(result))
        
        return ChatResponse(
            response=str(final_text),
            # safely serialize the raw result if it's a dict/list, or stringify it
            # raw_result=result if isinstance(result, (dict, list)) else str(result)
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        # return detailed error during dev, generic in prod? 
        # For now, return the error message for debugging.
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

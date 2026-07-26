import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from backend.schemas import ChatRequestSchema
from backend.llm_helper import LLMService

router = APIRouter(prefix="/api/chat", tags=["chat"])

async def event_generator(request: ChatRequestSchema):
    """Format streamed tokens as Server-Sent Events (SSE)."""
    async for token in LLMService.stream_chat_tokens(request):
        # Format as SSE event data payload
        payload = json.dumps({"token": token})
        yield f"data: {payload}\n\n"
    yield "data: [DONE]\n\n"

@router.post("/stream")
async def chat_stream(request: ChatRequestSchema):
    """Stream token completions asynchronously for Gemini, OpenAI, and Anthropic."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty.")
    
    return StreamingResponse(
        event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

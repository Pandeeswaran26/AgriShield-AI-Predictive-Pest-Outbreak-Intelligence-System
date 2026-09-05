from fastapi import APIRouter

from .schemas import ChatRequest, ChatResponse
from .service import get_ai_response

router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"]
)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    history_dicts = [{"role": m.role, "content": m.content} for m in request.history] if request.history else []
    reply = get_ai_response(request.message, history=history_dicts)
    return ChatResponse(reply=reply)
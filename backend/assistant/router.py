from fastapi import APIRouter

from .schemas import ChatRequest, ChatResponse
from .service import get_ai_response

router = APIRouter(
    prefix="/assistant",
    tags=["AI Assistant"]
)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    reply = get_ai_response(request.message)

    return ChatResponse(reply=reply)
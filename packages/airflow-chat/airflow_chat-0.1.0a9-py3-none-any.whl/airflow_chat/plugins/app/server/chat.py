import uuid

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from .llm import get_stream_agent_responce


chat_router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@chat_router.post("/new")
async def new_chat(request: Request):
    """Create a new chat session."""
    request.session['chat_session_id'] = f'user_{uuid.uuid4()}'
    return {'results': 'ok'}


@chat_router.post("/ask")
async def chat(
    request: Request,
    chat_request: ChatRequest,
):
    if 'chat_session_id' not in request.session:
        await new_chat(request)
    # Get the user chat configuration and the LLM agent.
    stream_agent_response = await get_stream_agent_responce(request.session[
        'chat_session_id'],
                                                      chat_request.message)

    # Return the agent's response as a stream of JSON objects.
    return StreamingResponse(stream_agent_response(),
                             media_type='application/json')

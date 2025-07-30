from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import List, Literal

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

# assistant comes from the user script loaded by cli.py
from grafi.assistants.assistant import Assistant
from grafi.common.containers.container import container
from grafi.common.models.message import Messages
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ---------- pydantic ↔ grafi helpers ------------------------------------
class MsgIn(BaseModel):
    role: str = Literal["system", "user", "assistant", "tool"]
    content: str


class ChatRequest(BaseModel):
    conversation_id: str
    assistant_request_id: str
    messages: List[MsgIn]


class ChatReply(BaseModel):
    messages: Messages


def _to_messages(msgs_in: List[MsgIn]) -> Messages:
    from grafi.common.models.message import Message

    return [Message(role=m.role, content=m.content) for m in msgs_in]


def _invoke_context(conv_id: str, req_id: str):
    from grafi.common.models.invoke_context import InvokeContext

    return InvokeContext(
        conversation_id=conv_id,
        assistant_request_id=req_id,
        invoke_id=uuid.uuid4().hex,
    )


# ---------- conversation helpers ----------------------------------------
def get_conversation_ids():
    evs = container.event_store.get_events()
    conv_ids = {e.invoke_context.conversation_id for e in evs}
    return sorted(
        conv_ids,
        key=lambda conv_id: min(
            e.timestamp for e in evs if e.invoke_context.conversation_id == conv_id
        ),
    )


def get_request_ids(conv_id: str):
    evs = container.event_store.get_conversation_events(conv_id)
    req_ids = {e.invoke_context.assistant_request_id for e in evs}
    return sorted(
        req_ids,
        key=lambda req_id: min(
            e.timestamp for e in evs if e.invoke_context.assistant_request_id == req_id
        ),
    )


# ---------- FastAPI factory ---------------------------------------------
def create_app(assistant: Assistant, is_async: bool = True) -> FastAPI:
    api = FastAPI(title="Graphite-Dev API")

    @api.post("/chat", response_model=ChatReply)
    async def chat(req: ChatRequest):
        try:
            out: Messages = []
            if is_async:

                async for messages in assistant.a_invoke(
                    _invoke_context(req.conversation_id, req.assistant_request_id),
                    _to_messages(req.messages),
                ):
                    out.extend(messages)
            else:
                out = assistant.invoke(
                    _invoke_context(req.conversation_id, req.assistant_request_id),
                    _to_messages(req.messages),
                )
            logger.info(out)
            return ChatReply(messages=out)
        except Exception as exc:
            logger.exception(
                "Error in assistant execution: %s, Traceback: %s",
                exc,
                exc.__traceback__,
            )
            raise HTTPException(500, str(exc)) from exc

    @api.get("/events/{conv_id}", response_model=list)
    async def events_convo_dump(conv_id: str):
        return [
            e.model_dump()  # type: ignore
            for e in container.event_store.get_conversation_events(conv_id)
        ]

    @api.get("/workflow", response_model=dict)
    async def workflow():
        return assistant.to_dict()

    @api.get("/conversations", response_model=list[str])
    async def list_convs():
        return get_conversation_ids()

    @api.get("/conversations/{conv_id}/requests", response_model=list[str])
    async def list_reqs(conv_id: str):
        return get_request_ids(conv_id)

    ui_dir = Path(__file__).parent / "frontend"
    api.mount("/", StaticFiles(directory=ui_dir, html=True), name="ui")
    return api


if __name__ == "__main__":
    uvicorn.run(create_app(), host="127.0.0.1", port=8080, reload=True)

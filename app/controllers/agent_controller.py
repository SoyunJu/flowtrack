"""MCP 에이전트와 대화하는 채팅 컨트롤러."""

from __future__ import annotations

import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.agents.inventory_agent import InventoryAgent
from app.controllers.upload_controller import get_last_report

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.post("/agent/chat")
async def agent_chat(body: ChatRequest) -> JSONResponse:
    """사용자 질문을 에이전트에 전달하고 답변을 반환한다."""
    report = get_last_report()
    if report is None:
        return JSONResponse(
            {"answer": "먼저 파일을 업로드해주세요."}, status_code=400
        )

    agent = InventoryAgent(report.records)
    use_mock = not os.getenv("OPENAI_API_KEY")

    if use_mock:
        answer = await agent.run_mock(body.query)
    else:
        answer = await agent.run(body.query)

    return JSONResponse({"answer": answer})

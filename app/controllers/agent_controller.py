"""MCP 에이전트와 대화하는 채팅 컨트롤러."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.post("/agent/chat")
async def agent_chat(body: ChatRequest) -> JSONResponse:
    """사용자 질문을 에이전트에 전달하고 답변을 반환한다.

    TODO:
    - get_last_report()가 None이면 400 에러 반환
    - InventoryAgent(report.records) 생성
    - OPENAI_API_KEY 존재 여부에 따라 run() 또는 run_mock() 호출
    - {"answer": answer} JSON 반환
    """
    raise NotImplementedError

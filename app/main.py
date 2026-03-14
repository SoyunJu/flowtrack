"""FlowTrack FastAPI 애플리케이션 진입점."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.controllers import agent_router, report_router, upload_router

app = FastAPI(
    title="FlowTrack",
    description="물류 입출고 자동화 대시보드 — MVC + MCP Agent",
    version="0.1.0",
)

# 정적 파일
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 라우터 등록
app.include_router(upload_router)
app.include_router(report_router)
app.include_router(agent_router)

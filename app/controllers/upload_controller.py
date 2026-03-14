"""파일 업로드 및 재고 분석 흐름을 처리하는 컨트롤러."""

from __future__ import annotations

import os
from datetime import datetime

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.models.inventory import InventoryReport
from app.services.excel_service import ExcelService
from app.services.gpt_service import GPTService
from app.services.inventory_service import InventoryService

router = APIRouter()
templates = Jinja2Templates(directory="app/views")

# 세션 대신 메모리에 마지막 리포트 캐시 (단일 사용자 데모용)
_last_report: InventoryReport | None = None


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/sample-download")
async def download_sample() -> StreamingResponse:
    """데모용 샘플 엑셀 파일 다운로드."""
    data = ExcelService.generate_sample_excel()
    return StreamingResponse(
        iter([data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=sample_inventory.xlsx"},
    )


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)) -> RedirectResponse:
    """엑셀 파일을 업로드하고 분석 결과를 생성한다."""
    global _last_report

    contents = await file.read()
    records = ExcelService.parse(contents)
    items = InventoryService.aggregate(records)
    rule_alerts = InventoryService.detect_anomalies(items, records)

    # GPT 분석 (API 키 없으면 mock 사용)
    use_mock = not os.getenv("OPENAI_API_KEY")
    if use_mock:
        alerts, summary = await GPTService.analyze_mock(items, rule_alerts)
    else:
        alerts, summary = await GPTService.analyze(items, rule_alerts)

    _last_report = InventoryReport(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        records=records,
        items=items,
        anomalies=alerts,
        gpt_summary=summary,
    )
    return RedirectResponse(url="/report", status_code=303)


def get_last_report() -> InventoryReport | None:
    return _last_report

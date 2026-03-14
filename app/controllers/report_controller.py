"""분석 리포트 조회 및 다운로드 컨트롤러."""

from __future__ import annotations

import io
import json

import pandas as pd
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.controllers.upload_controller import get_last_report

router = APIRouter()
templates = Jinja2Templates(directory="app/views")


@router.get("/report", response_class=HTMLResponse)
async def report_page(request: Request) -> HTMLResponse:
    """리포트 페이지를 렌더링한다."""
    report = get_last_report()
    if report is None:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "먼저 파일을 업로드해주세요."},
        )
    return templates.TemplateResponse(
        "report.html",
        {"request": request, "report": report},
    )


@router.get("/report/json")
async def report_json() -> JSONResponse:
    """리포트를 JSON으로 반환 (API 활용 용도)."""
    report = get_last_report()
    if report is None:
        return JSONResponse({"error": "리포트 없음"}, status_code=404)
    return JSONResponse(json.loads(report.model_dump_json()))


@router.get("/report/download/excel")
async def download_excel() -> StreamingResponse:
    """현재고 및 이상 징후를 엑셀로 다운로드한다."""
    report = get_last_report()
    if report is None:
        return StreamingResponse(iter([b""]), status_code=404)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # 시트 1: 재고 현황
        items_data = [
            {
                "품목코드": i.item_code,
                "품목명": i.item_name,
                "총입고": i.total_in,
                "총출고": i.total_out,
                "현재고": i.current_stock,
                "단위": i.unit,
                "출고율": f"{i.turnover_ratio * 100:.0f}%",
            }
            for i in report.items
        ]
        pd.DataFrame(items_data).to_excel(writer, sheet_name="재고현황", index=False)

        # 시트 2: 이상 징후
        alerts_data = [
            {
                "품목코드": a.item_code,
                "품목명": a.item_name,
                "유형": a.alert_type,
                "심각도": a.severity,
                "설명": a.description,
            }
            for a in report.anomalies
        ]
        pd.DataFrame(alerts_data).to_excel(writer, sheet_name="이상징후", index=False)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=inventory_report.xlsx"},
    )

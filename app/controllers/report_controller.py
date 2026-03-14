"""분석 리포트 조회 및 다운로드 컨트롤러."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.controllers.upload_controller import get_last_report

router = APIRouter()
templates = Jinja2Templates(directory="app/views")


@router.get("/report", response_class=HTMLResponse)
async def report_page(request: Request) -> HTMLResponse:
    """리포트 페이지를 렌더링한다.

    TODO:
    - get_last_report()가 None이면 index.html에 에러 메시지 포함하여 반환
    - 리포트 있으면 report.html 렌더링
    """
    raise NotImplementedError


@router.get("/report/json")
async def report_json() -> JSONResponse:
    """리포트를 JSON으로 반환 (API 활용 용도).

    TODO: 리포트 없으면 404, 있으면 model_dump_json() 직렬화 후 반환
    """
    raise NotImplementedError


@router.get("/report/download/excel")
async def download_excel() -> StreamingResponse:
    """현재고 및 이상 징후를 엑셀로 다운로드한다.

    TODO:
    - pandas ExcelWriter로 BytesIO에 두 시트 작성
      - 시트1: 재고현황 (품목코드/명/총입고/총출고/현재고/단위/출고율)
      - 시트2: 이상징후 (품목코드/명/유형/심각도/설명)
    - StreamingResponse로 xlsx 반환
    """
    raise NotImplementedError

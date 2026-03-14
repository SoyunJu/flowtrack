"""파일 업로드 및 재고 분석 흐름을 처리하는 컨트롤러."""

from __future__ import annotations

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.models.inventory import InventoryReport

router = APIRouter()
templates = Jinja2Templates(directory="app/views")

# 세션 대신 메모리에 마지막 리포트 캐시 (단일 사용자 데모용)
_last_report: InventoryReport | None = None


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """메인 페이지 (파일 업로드 화면) 렌더링."""
    # TODO: index.html 템플릿 렌더링
    raise NotImplementedError


@router.get("/sample-download")
async def download_sample() -> StreamingResponse:
    """데모용 샘플 엑셀 파일 다운로드.

    TODO:
    - ExcelService.generate_sample_excel() 호출
    - StreamingResponse로 xlsx 파일 반환
    """
    raise NotImplementedError


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)) -> RedirectResponse:
    """엑셀 파일을 업로드하고 분석 결과를 생성한다.

    TODO:
    1. file.read()로 파일 내용 읽기
    2. ExcelService.parse() → records
    3. InventoryService.aggregate() → items
    4. InventoryService.detect_anomalies() → rule_alerts
    5. OPENAI_API_KEY 존재 여부에 따라 GPTService.analyze() 또는 analyze_mock()
    6. _last_report에 InventoryReport 저장
    7. /report로 303 리다이렉트
    """
    raise NotImplementedError


def get_last_report() -> InventoryReport | None:
    return _last_report

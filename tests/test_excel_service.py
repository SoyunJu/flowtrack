"""ExcelService 단위 테스트."""

import io

import pandas as pd
import pytest

from app.models.inventory import TransactionType
from app.services.excel_service import ExcelService


def _make_excel_bytes(rows: list[dict]) -> bytes:
    buf = io.BytesIO()
    pd.DataFrame(rows).to_excel(buf, index=False)
    return buf.getvalue()


class TestExcelServiceParse:
    def test_parse_korean_columns(self):
        """한글 컬럼명으로 된 엑셀을 파싱하여 InventoryRecord 목록을 반환해야 한다."""
        # TODO: 구현 후 테스트 실행
        pytest.skip("ExcelService.parse() 미구현")

    def test_skip_invalid_rows(self):
        """필수 필드가 빠진 행은 건너뛰어야 한다."""
        # TODO: 구현 후 테스트 실행
        pytest.skip("ExcelService.parse() 미구현")

    def test_generate_sample_excel(self):
        """샘플 엑셀 생성 후 파싱하면 레코드가 반환되어야 한다."""
        # TODO: 구현 후 테스트 실행
        pytest.skip("ExcelService.generate_sample_excel() 미구현")

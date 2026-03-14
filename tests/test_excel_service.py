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
        data = _make_excel_bytes([
            {"날짜": "2024-01-01", "품목코드": "A001", "품목명": "노트북", "구분": "입고", "수량": 100},
            {"날짜": "2024-01-02", "품목코드": "A001", "품목명": "노트북", "구분": "출고", "수량": 30},
        ])
        records = ExcelService.parse(data)
        assert len(records) == 2
        assert records[0].transaction_type == TransactionType.IN
        assert records[1].transaction_type == TransactionType.OUT
        assert records[0].quantity == 100

    def test_skip_invalid_rows(self):
        data = _make_excel_bytes([
            {"날짜": "2024-01-01", "품목코드": "A001", "품목명": "노트북", "구분": "입고", "수량": 100},
            {"날짜": None, "품목코드": None, "품목명": None, "구분": None, "수량": None},  # 빈 행
        ])
        records = ExcelService.parse(data)
        assert len(records) == 1

    def test_generate_sample_excel(self):
        data = ExcelService.generate_sample_excel()
        records = ExcelService.parse(data)
        assert len(records) > 0

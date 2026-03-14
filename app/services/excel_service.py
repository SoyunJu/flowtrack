"""엑셀 파일을 읽어 InventoryRecord 목록으로 변환하는 서비스."""

from __future__ import annotations

import io
from typing import BinaryIO

import pandas as pd

from app.models.inventory import InventoryRecord, TransactionType

# 엑셀 컬럼명 → 내부 필드명 매핑 (유연하게 처리)
_COLUMN_MAP: dict[str, str] = {
    "날짜": "date",
    "date": "date",
    "품목코드": "item_code",
    "item_code": "item_code",
    "품목명": "item_name",
    "item_name": "item_name",
    "구분": "transaction_type",
    "type": "transaction_type",
    "수량": "quantity",
    "quantity": "quantity",
    "단위": "unit",
    "unit": "unit",
    "비고": "note",
    "note": "note",
}


class ExcelService:
    """엑셀 파일 파싱 담당 서비스."""

    @staticmethod
    def parse(file: BinaryIO | bytes) -> list[InventoryRecord]:
        """업로드된 엑셀/CSV 파일을 파싱하여 레코드 목록을 반환한다."""
        if isinstance(file, bytes):
            file = io.BytesIO(file)

        # 확장자 구분 없이 먼저 xlsx 시도, 실패하면 csv
        try:
            df = pd.read_excel(file, dtype=str)
        except Exception:
            file.seek(0)
            df = pd.read_csv(file, dtype=str)

        df = ExcelService._normalize_columns(df)
        df = df.dropna(subset=["date", "item_code", "transaction_type", "quantity"])

        records: list[InventoryRecord] = []
        for _, row in df.iterrows():
            try:
                records.append(
                    InventoryRecord(
                        date=row["date"],
                        item_code=row["item_code"],
                        item_name=row.get("item_name", row["item_code"]),
                        transaction_type=TransactionType(row["transaction_type"].strip()),
                        quantity=int(float(row["quantity"])),
                        unit=row.get("unit", "EA") or "EA",
                        note=row.get("note") or None,
                    )
                )
            except Exception:
                # 파싱 실패 행은 조용히 건너뜀 (로깅 추가 가능)
                continue

        return records

    @staticmethod
    def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """컬럼명을 내부 필드명으로 통일."""
        renamed = {col: _COLUMN_MAP.get(col.strip(), col.strip()) for col in df.columns}
        return df.rename(columns=renamed)

    @staticmethod
    def generate_sample_excel() -> bytes:
        """데모용 샘플 엑셀을 생성하여 bytes로 반환."""
        sample = [
            {"날짜": "2024-01-02", "품목코드": "A001", "품목명": "노트북", "구분": "입고", "수량": 100, "단위": "EA"},
            {"날짜": "2024-01-05", "품목코드": "A001", "품목명": "노트북", "구분": "출고", "수량": 40, "단위": "EA"},
            {"날짜": "2024-01-10", "품목코드": "A001", "품목명": "노트북", "구분": "출고", "수량": 90, "단위": "EA"},  # 과다출고
            {"날짜": "2024-01-03", "품목코드": "B002", "품목명": "마우스", "구분": "입고", "수량": 200, "단위": "EA"},
            {"날짜": "2024-01-07", "품목코드": "B002", "품목명": "마우스", "구분": "출고", "수량": 50, "단위": "EA"},
            {"날짜": "2024-01-04", "품목코드": "C003", "품목명": "키보드", "구분": "입고", "수량": 30, "단위": "EA"},
            {"날짜": "2024-01-08", "품목코드": "C003", "품목명": "키보드", "구분": "출고", "수량": 35, "단위": "EA"},  # 마이너스재고
        ]
        df = pd.DataFrame(sample)
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        return buf.getvalue()

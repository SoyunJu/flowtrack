"""엑셀 파일을 읽어 InventoryRecord 목록으로 변환하는 서비스."""

from __future__ import annotations

from typing import BinaryIO

from app.models.inventory import InventoryRecord

# 엑셀 컬럼명 → 내부 필드명 매핑
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
        """업로드된 엑셀/CSV 파일을 파싱하여 레코드 목록을 반환한다.

        TODO:
        - pandas로 엑셀(xlsx) 또는 CSV 읽기
        - _normalize_columns()로 컬럼명 통일
        - 각 행을 InventoryRecord로 변환 (파싱 실패 행 건너뜀)
        """
        raise NotImplementedError

    @staticmethod
    def _normalize_columns(df):  # type: ignore[no-untyped-def]
        """컬럼명을 내부 필드명으로 통일.

        TODO: _COLUMN_MAP을 이용해 df의 컬럼명을 rename
        """
        raise NotImplementedError

    @staticmethod
    def generate_sample_excel() -> bytes:
        """데모용 샘플 엑셀을 생성하여 bytes로 반환.

        TODO: pandas DataFrame → BytesIO → xlsx bytes 반환
        샘플 데이터: 노트북(과다출고), 마우스(정상), 키보드(마이너스재고) 포함
        """
        raise NotImplementedError

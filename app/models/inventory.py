from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    IN = "입고"
    OUT = "출고"


class InventoryRecord(BaseModel):
    """엑셀에서 파싱된 입출고 단건 레코드."""

    date: date
    item_code: str = Field(..., description="품목 코드")
    item_name: str = Field(..., description="품목명")
    transaction_type: TransactionType
    quantity: int = Field(..., ge=0, description="수량 (0 이상)")
    unit: str = Field(default="EA", description="단위")
    note: Optional[str] = None

    @field_validator("item_code", "item_name", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return str(v).strip()


class InventoryItem(BaseModel):
    """품목별 현재고 집계 결과."""

    item_code: str
    item_name: str
    total_in: int = Field(default=0, description="총 입고량")
    total_out: int = Field(default=0, description="총 출고량")
    current_stock: int = Field(default=0, description="현재고 (입고 - 출고)")
    unit: str = "EA"

    @property
    def is_negative(self) -> bool:
        return self.current_stock < 0

    @property
    def turnover_ratio(self) -> float:
        """출고율 = 총출고 / 총입고 (입고 0이면 0 반환)."""
        if self.total_in == 0:
            return 0.0
        return round(self.total_out / self.total_in, 2)


class AnomalyAlert(BaseModel):
    """이상 징후 탐지 결과."""

    item_code: str
    item_name: str
    alert_type: str = Field(..., description="이상 유형 (예: 마이너스재고, 급감, 과다출고)")
    severity: str = Field(..., description="심각도: LOW / MEDIUM / HIGH")
    description: str = Field(..., description="자연어 설명")


class InventoryReport(BaseModel):
    """최종 리포트 — 컨트롤러가 뷰에 전달하는 단일 객체."""

    generated_at: str
    records: list[InventoryRecord]
    items: list[InventoryItem]
    anomalies: list[AnomalyAlert]
    gpt_summary: str = Field(default="", description="GPT 전체 요약 문장")

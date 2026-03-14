"""입출고 레코드를 집계하여 현재고 및 이상 징후 목록을 계산하는 서비스."""

from __future__ import annotations

from app.models.inventory import AnomalyAlert, InventoryItem, InventoryRecord

# 이상 탐지 임계값
_NEGATIVE_STOCK_THRESHOLD = 0        # 현재고 0 미만 → 마이너스 재고
_TURNOVER_HIGH_THRESHOLD = 0.9       # 출고율 90% 이상 → 과다 출고 경고
_SINGLE_OUT_LARGE_RATIO = 0.5        # 단건 출고가 총입고의 50% 이상 → 급감


class InventoryService:
    """재고 집계 및 규칙 기반 이상 탐지 담당 서비스."""

    @staticmethod
    def aggregate(records: list[InventoryRecord]) -> list[InventoryItem]:
        """레코드 목록을 품목별로 집계하여 현재고를 계산한다.

        TODO:
        - item_code를 키로 입고/출고 수량을 합산
        - current_stock = total_in - total_out
        - InventoryItem 리스트 반환
        """
        raise NotImplementedError

    @staticmethod
    def detect_anomalies(
        items: list[InventoryItem],
        records: list[InventoryRecord],
    ) -> list[AnomalyAlert]:
        """규칙 기반으로 이상 징후를 탐지하고 AnomalyAlert 목록을 반환한다.

        탐지 규칙:
        1. 마이너스 재고: current_stock < 0  → severity HIGH
        2. 과다 출고: turnover_ratio >= 0.9  → severity MEDIUM
        3. 단건 급감: 단일 출고량 / total_in >= 0.5  → severity MEDIUM

        TODO: 각 규칙을 순회하며 조건 충족 시 AnomalyAlert 생성
        """
        raise NotImplementedError

"""InventoryService 단위 테스트."""

from datetime import date

import pytest

from app.models.inventory import InventoryRecord, TransactionType
from app.services.inventory_service import InventoryService


def _make_record(code: str, name: str, tx: TransactionType, qty: int, d: str = "2024-01-01") -> InventoryRecord:
    return InventoryRecord(
        date=date.fromisoformat(d),
        item_code=code,
        item_name=name,
        transaction_type=tx,
        quantity=qty,
    )


class TestAggregate:
    def test_basic_in_out(self):
        """입고 100, 출고 40 → 현재고 60이어야 한다."""
        # TODO: 구현 후 테스트 실행
        pytest.skip("InventoryService.aggregate() 미구현")

    def test_negative_stock(self):
        """출고가 입고를 초과하면 현재고가 음수여야 한다."""
        # TODO: 구현 후 테스트 실행
        pytest.skip("InventoryService.aggregate() 미구현")

    def test_multiple_items(self):
        """여러 품목을 집계하면 각 품목별로 분리되어야 한다."""
        # TODO: 구현 후 테스트 실행
        pytest.skip("InventoryService.aggregate() 미구현")


class TestDetectAnomalies:
    def test_negative_stock_alert(self):
        """마이너스 재고 발생 시 '마이너스재고' 알림이 생성되어야 한다."""
        # TODO: 구현 후 테스트 실행
        pytest.skip("InventoryService.detect_anomalies() 미구현")

    def test_high_turnover_alert(self):
        """출고율 90% 이상 시 '과다출고' 알림이 생성되어야 한다."""
        # TODO: 구현 후 테스트 실행
        pytest.skip("InventoryService.detect_anomalies() 미구현")

    def test_no_anomaly_for_normal_stock(self):
        """정상 재고 상태에서는 알림이 없어야 한다."""
        # TODO: 구현 후 테스트 실행
        pytest.skip("InventoryService.detect_anomalies() 미구현")

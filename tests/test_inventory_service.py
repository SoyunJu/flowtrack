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
        records = [
            _make_record("A001", "노트북", TransactionType.IN, 100),
            _make_record("A001", "노트북", TransactionType.OUT, 40),
        ]
        items = InventoryService.aggregate(records)
        assert len(items) == 1
        item = items[0]
        assert item.total_in == 100
        assert item.total_out == 40
        assert item.current_stock == 60

    def test_negative_stock(self):
        records = [
            _make_record("B001", "마우스", TransactionType.IN, 10),
            _make_record("B001", "마우스", TransactionType.OUT, 15),
        ]
        items = InventoryService.aggregate(records)
        assert items[0].current_stock == -5
        assert items[0].is_negative is True

    def test_multiple_items(self):
        records = [
            _make_record("A001", "노트북", TransactionType.IN, 50),
            _make_record("B002", "마우스", TransactionType.IN, 100),
            _make_record("B002", "마우스", TransactionType.OUT, 30),
        ]
        items = InventoryService.aggregate(records)
        codes = {i.item_code for i in items}
        assert codes == {"A001", "B002"}


class TestDetectAnomalies:
    def test_negative_stock_alert(self):
        records = [
            _make_record("A001", "노트북", TransactionType.IN, 10),
            _make_record("A001", "노트북", TransactionType.OUT, 15),
        ]
        items = InventoryService.aggregate(records)
        alerts = InventoryService.detect_anomalies(items, records)
        types = [a.alert_type for a in alerts]
        assert "마이너스재고" in types

    def test_high_turnover_alert(self):
        records = [
            _make_record("A001", "노트북", TransactionType.IN, 100),
            _make_record("A001", "노트북", TransactionType.OUT, 95),
        ]
        items = InventoryService.aggregate(records)
        alerts = InventoryService.detect_anomalies(items, records)
        types = [a.alert_type for a in alerts]
        assert "과다출고" in types

    def test_no_anomaly_for_normal_stock(self):
        records = [
            _make_record("A001", "노트북", TransactionType.IN, 100),
            _make_record("A001", "노트북", TransactionType.OUT, 30),
        ]
        items = InventoryService.aggregate(records)
        alerts = InventoryService.detect_anomalies(items, records)
        assert len(alerts) == 0

"""입출고 레코드를 집계하여 현재고 및 이상 징후 목록을 계산하는 서비스."""

from __future__ import annotations

from collections import defaultdict

from app.models.inventory import AnomalyAlert, InventoryItem, InventoryRecord, TransactionType

# 이상 탐지 임계값
_NEGATIVE_STOCK_THRESHOLD = 0        # 현재고 0 미만 → 마이너스 재고
_TURNOVER_HIGH_THRESHOLD = 0.9       # 출고율 90% 이상 → 과다 출고 경고
_SINGLE_OUT_LARGE_RATIO = 0.5        # 단건 출고가 총입고의 50% 이상 → 급감


class InventoryService:
    """재고 집계 및 규칙 기반 이상 탐지 담당 서비스."""

    @staticmethod
    def aggregate(records: list[InventoryRecord]) -> list[InventoryItem]:
        """레코드 목록을 품목별로 집계하여 현재고를 계산한다."""
        bucket: dict[str, dict] = defaultdict(
            lambda: {"total_in": 0, "total_out": 0, "item_name": "", "unit": "EA"}
        )

        for r in records:
            b = bucket[r.item_code]
            b["item_name"] = r.item_name
            b["unit"] = r.unit
            if r.transaction_type == TransactionType.IN:
                b["total_in"] += r.quantity
            else:
                b["total_out"] += r.quantity

        return [
            InventoryItem(
                item_code=code,
                item_name=data["item_name"],
                total_in=data["total_in"],
                total_out=data["total_out"],
                current_stock=data["total_in"] - data["total_out"],
                unit=data["unit"],
            )
            for code, data in bucket.items()
        ]

    @staticmethod
    def detect_anomalies(
        items: list[InventoryItem],
        records: list[InventoryRecord],
    ) -> list[AnomalyAlert]:
        """규칙 기반으로 이상 징후를 탐지하고 AnomalyAlert 목록을 반환한다.

        GPT 서비스로 넘기기 전에 구조화된 컨텍스트를 제공하기 위해 사용된다.
        """
        alerts: list[AnomalyAlert] = []

        for item in items:
            # 1. 마이너스 재고
            if item.current_stock < _NEGATIVE_STOCK_THRESHOLD:
                alerts.append(
                    AnomalyAlert(
                        item_code=item.item_code,
                        item_name=item.item_name,
                        alert_type="마이너스재고",
                        severity="HIGH",
                        description=(
                            f"현재고가 {item.current_stock}{item.unit}으로 음수입니다. "
                            "데이터 오류 또는 미등록 입고가 있을 수 있습니다."
                        ),
                    )
                )

            # 2. 과다 출고 (출고율 90% 이상)
            if item.turnover_ratio >= _TURNOVER_HIGH_THRESHOLD and item.total_in > 0:
                alerts.append(
                    AnomalyAlert(
                        item_code=item.item_code,
                        item_name=item.item_name,
                        alert_type="과다출고",
                        severity="MEDIUM",
                        description=(
                            f"출고율이 {item.turnover_ratio * 100:.0f}%로 높습니다. "
                            f"입고 {item.total_in}{item.unit} 대비 출고 {item.total_out}{item.unit}."
                        ),
                    )
                )

            # 3. 단건 급감 (단일 출고 건이 총입고의 50% 이상)
            large_outs = [
                r for r in records
                if r.item_code == item.item_code
                and r.transaction_type == TransactionType.OUT
                and item.total_in > 0
                and r.quantity / item.total_in >= _SINGLE_OUT_LARGE_RATIO
            ]
            for out_record in large_outs:
                alerts.append(
                    AnomalyAlert(
                        item_code=item.item_code,
                        item_name=item.item_name,
                        alert_type="급감",
                        severity="MEDIUM",
                        description=(
                            f"{out_record.date} 단건 출고 {out_record.quantity}{item.unit}이 "
                            f"총입고({item.total_in}{item.unit})의 "
                            f"{out_record.quantity / item.total_in * 100:.0f}%입니다."
                        ),
                    )
                )

        return alerts

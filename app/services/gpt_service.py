"""OpenAI GPT를 사용하여 이상 징후 자연어 리포트를 생성하는 서비스."""

from __future__ import annotations

from app.models.inventory import AnomalyAlert, InventoryItem

_MODEL = "gpt-4o-mini"


class GPTService:
    """GPT 기반 재고 이상 탐지 리포트 생성 서비스."""

    @staticmethod
    async def analyze(
        items: list[InventoryItem],
        rule_alerts: list[AnomalyAlert],
    ) -> tuple[list[AnomalyAlert], str]:
        """GPT에 재고 현황과 규칙 기반 알림을 보내고,
        보강된 알림 목록과 전체 요약 문장을 반환한다.

        Returns:
            (enriched_alerts, summary_text)

        TODO:
        - items, rule_alerts를 JSON payload로 변환
        - OpenAI AsyncOpenAI 클라이언트로 chat completion 호출
        - response_format={"type": "json_object"} 사용
        - 응답 파싱 후 (alerts, summary) 반환
        """
        raise NotImplementedError

    @staticmethod
    async def analyze_mock(
        items: list[InventoryItem],
        rule_alerts: list[AnomalyAlert],
    ) -> tuple[list[AnomalyAlert], str]:
        """API 키 없이 테스트할 수 있는 모의 응답.

        TODO: rule_alerts를 그대로 반환하고, 간단한 요약 문자열 생성
        """
        raise NotImplementedError

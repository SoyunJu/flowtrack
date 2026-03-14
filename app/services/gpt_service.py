"""OpenAI GPT를 사용하여 이상 징후 자연어 리포트를 생성하는 서비스."""

from __future__ import annotations

import json
import os

from openai import AsyncOpenAI

from app.models.inventory import AnomalyAlert, InventoryItem

_MODEL = "gpt-4o-mini"
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        _client = AsyncOpenAI(api_key=api_key)
    return _client


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
        """
        payload = _build_prompt_payload(items, rule_alerts)
        client = _get_client()

        response = await client.chat.completions.create(
            model=_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 물류 재고 분석 전문가입니다. "
                        "주어진 재고 현황과 이상 징후를 분석하여 JSON 형식으로 응답하세요. "
                        "응답 형식: {\"alerts\": [{\"item_code\", \"item_name\", \"alert_type\", \"severity\", \"description\"}], \"summary\": \"한 줄 요약\"}"
                    ),
                },
                {"role": "user", "content": payload},
            ],
            temperature=0.2,
            max_tokens=1024,
        )

        return _parse_response(response.choices[0].message.content, rule_alerts)

    @staticmethod
    async def analyze_mock(
        items: list[InventoryItem],
        rule_alerts: list[AnomalyAlert],
    ) -> tuple[list[AnomalyAlert], str]:
        """API 키 없이 테스트할 수 있는 모의 응답."""
        summary = (
            f"총 {len(items)}개 품목 분석 완료. "
            f"{len(rule_alerts)}건의 이상 징후가 감지되었습니다. "
            "즉각적인 재고 확인이 필요합니다."
        )
        return rule_alerts, summary


def _build_prompt_payload(items: list[InventoryItem], alerts: list[AnomalyAlert]) -> str:
    items_data = [
        {
            "품목코드": i.item_code,
            "품목명": i.item_name,
            "총입고": i.total_in,
            "총출고": i.total_out,
            "현재고": i.current_stock,
            "출고율": f"{i.turnover_ratio * 100:.0f}%",
        }
        for i in items
    ]
    alerts_data = [
        {
            "품목코드": a.item_code,
            "유형": a.alert_type,
            "심각도": a.severity,
            "설명": a.description,
        }
        for a in alerts
    ]
    return (
        f"재고 현황:\n{json.dumps(items_data, ensure_ascii=False, indent=2)}\n\n"
        f"사전 탐지된 이상 징후:\n{json.dumps(alerts_data, ensure_ascii=False, indent=2)}\n\n"
        "위 데이터를 분석하여 이상 징후를 보강하고 전체 요약을 작성해주세요."
    )


def _parse_response(
    content: str | None,
    fallback: list[AnomalyAlert],
) -> tuple[list[AnomalyAlert], str]:
    if not content:
        return fallback, "GPT 응답을 받지 못했습니다."
    try:
        data = json.loads(content)
        alerts = [AnomalyAlert(**a) for a in data.get("alerts", [])]
        summary = data.get("summary", "")
        return alerts or fallback, summary
    except Exception:
        return fallback, content[:300]

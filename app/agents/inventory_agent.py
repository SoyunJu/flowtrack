"""MCP(Model Context Protocol) 기반 재고 분석 에이전트.

에이전트는 "도구(tool)"들을 순서대로 호출하며 스스로 분석 흐름을 결정합니다.
MCP 스타일로 각 단계를 독립적인 Tool로 정의하고,
에이전트가 GPT Function Calling을 통해 필요한 도구를 선택합니다.
"""

from __future__ import annotations

import json
import os
from typing import Any

from openai import AsyncOpenAI

from app.models.inventory import AnomalyAlert, InventoryItem, InventoryRecord
from app.services.inventory_service import InventoryService

_MODEL = "gpt-4o-mini"

# ──────────────────────────────────────────
# MCP Tool 정의 (OpenAI function calling 형식)
# ──────────────────────────────────────────
_TOOLS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_summary",
            "description": "품목별 현재고 집계 요약을 반환합니다.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_anomaly_alerts",
            "description": "규칙 기반으로 탐지된 이상 징후 목록을 반환합니다.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_item_detail",
            "description": "특정 품목의 입출고 이력을 반환합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_code": {
                        "type": "string",
                        "description": "조회할 품목 코드",
                    }
                },
                "required": ["item_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "최종 재고 분석 리포트를 생성합니다.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


class InventoryAgent:
    """재고 분석 MCP 에이전트.

    사용법:
        agent = InventoryAgent(records)
        result = await agent.run("현재고가 위험한 품목이 있어?")
    """

    def __init__(self, records: list[InventoryRecord]) -> None:
        self._records = records
        self._items: list[InventoryItem] = InventoryService.aggregate(records)
        self._alerts: list[AnomalyAlert] = InventoryService.detect_anomalies(
            self._items, records
        )
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise EnvironmentError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
            self._client = AsyncOpenAI(api_key=api_key)
        return self._client

    # ──────────────────────────────────────────
    # Tool 핸들러 (실제 실행 함수)
    # ──────────────────────────────────────────

    def _handle_tool(self, name: str, arguments: dict) -> str:
        """도구 이름에 따라 적절한 핸들러를 실행하고 JSON 문자열을 반환한다."""
        if name == "get_stock_summary":
            return self._tool_get_stock_summary()
        if name == "get_anomaly_alerts":
            return self._tool_get_anomaly_alerts()
        if name == "get_item_detail":
            return self._tool_get_item_detail(arguments.get("item_code", ""))
        if name == "generate_report":
            return self._tool_generate_report()
        return json.dumps({"error": f"알 수 없는 도구: {name}"}, ensure_ascii=False)

    def _tool_get_stock_summary(self) -> str:
        data = [
            {
                "품목코드": i.item_code,
                "품목명": i.item_name,
                "총입고": i.total_in,
                "총출고": i.total_out,
                "현재고": i.current_stock,
                "단위": i.unit,
            }
            for i in self._items
        ]
        return json.dumps(data, ensure_ascii=False)

    def _tool_get_anomaly_alerts(self) -> str:
        data = [a.model_dump() for a in self._alerts]
        return json.dumps(data, ensure_ascii=False)

    def _tool_get_item_detail(self, item_code: str) -> str:
        records = [
            {
                "날짜": str(r.date),
                "구분": r.transaction_type.value,
                "수량": r.quantity,
                "단위": r.unit,
                "비고": r.note,
            }
            for r in self._records
            if r.item_code == item_code
        ]
        return json.dumps(
            {"item_code": item_code, "records": records}, ensure_ascii=False
        )

    def _tool_generate_report(self) -> str:
        report = {
            "품목수": len(self._items),
            "이상징후수": len(self._alerts),
            "마이너스재고품목": [
                i.item_name for i in self._items if i.is_negative
            ],
            "이상징후목록": [a.model_dump() for a in self._alerts],
        }
        return json.dumps(report, ensure_ascii=False)

    # ──────────────────────────────────────────
    # 에이전트 루프 (agentic loop)
    # ──────────────────────────────────────────

    async def run(self, user_query: str, max_steps: int = 6) -> str:
        """사용자 질문을 받아 MCP 에이전트 루프를 실행하고 최종 답변을 반환한다.

        Args:
            user_query: 자연어 질문 (예: "마이너스 재고 품목이 있어?")
            max_steps: 최대 도구 호출 횟수 (무한루프 방지)
        """
        client = self._get_client()
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "당신은 물류 재고 분석 에이전트입니다. "
                    "사용 가능한 도구를 활용하여 사용자의 질문에 답하세요. "
                    "필요한 도구를 순서대로 호출한 뒤 최종 답변을 한국어로 작성하세요."
                ),
            },
            {"role": "user", "content": user_query},
        ]

        for _ in range(max_steps):
            response = await client.chat.completions.create(
                model=_MODEL,
                messages=messages,
                tools=_TOOLS,
                tool_choice="auto",
                temperature=0.2,
            )
            msg = response.choices[0].message

            # 도구 호출 없음 → 최종 답변
            if not msg.tool_calls:
                return msg.content or "응답을 생성할 수 없습니다."

            # 도구 호출 처리
            messages.append(msg)  # type: ignore[arg-type]
            for tool_call in msg.tool_calls:
                args = json.loads(tool_call.function.arguments or "{}")
                result = self._handle_tool(tool_call.function.name, args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

        return "최대 단계 수에 도달했습니다. 분석을 완료하지 못했습니다."

    async def run_mock(self, user_query: str) -> str:
        """API 키 없이 테스트할 수 있는 모의 실행."""
        alerts_text = "\n".join(
            f"- [{a.severity}] {a.item_name}: {a.description}"
            for a in self._alerts
        ) or "이상 징후 없음"
        return (
            f"질문: {user_query}\n\n"
            f"재고 현황: {len(self._items)}개 품목\n"
            f"이상 징후:\n{alerts_text}"
        )

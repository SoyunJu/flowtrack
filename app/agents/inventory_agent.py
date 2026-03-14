"""MCP(Model Context Protocol) 기반 재고 분석 에이전트.

에이전트는 "도구(tool)"들을 순서대로 호출하며 스스로 분석 흐름을 결정합니다.
MCP 스타일로 각 단계를 독립적인 Tool로 정의하고,
에이전트가 GPT Function Calling을 통해 필요한 도구를 선택합니다.
"""

from __future__ import annotations

from app.models.inventory import InventoryRecord

_MODEL = "gpt-4o-mini"

# MCP Tool 정의 (OpenAI function calling 형식)
# TODO: 아래 4개 도구의 스펙(name, description, parameters)을 정의
_TOOLS: list[dict] = [
    # get_stock_summary  - 품목별 현재고 집계 요약 반환
    # get_anomaly_alerts - 규칙 기반 이상 징후 목록 반환
    # get_item_detail    - 특정 품목 코드의 입출고 이력 반환 (item_code 파라미터)
    # generate_report    - 최종 재고 분석 리포트 생성
]


class InventoryAgent:
    """재고 분석 MCP 에이전트.

    사용법:
        agent = InventoryAgent(records)
        result = await agent.run("현재고가 위험한 품목이 있어?")
    """

    def __init__(self, records: list[InventoryRecord]) -> None:
        self._records = records
        # TODO: InventoryService.aggregate(), detect_anomalies() 호출하여 초기화
        self._items = []
        self._alerts = []
        self._client = None

    def _handle_tool(self, name: str, arguments: dict) -> str:
        """도구 이름에 따라 적절한 핸들러를 실행하고 JSON 문자열을 반환한다.

        TODO: name에 따라 아래 _tool_* 메서드 중 하나를 호출
        """
        raise NotImplementedError

    def _tool_get_stock_summary(self) -> str:
        """self._items를 품목별 요약 JSON으로 직렬화하여 반환.

        TODO: 각 InventoryItem의 코드/명/입출고/현재고/단위를 dict로 변환 후 json.dumps
        """
        raise NotImplementedError

    def _tool_get_anomaly_alerts(self) -> str:
        """self._alerts를 JSON으로 직렬화하여 반환.

        TODO: [a.model_dump() for a in self._alerts] → json.dumps
        """
        raise NotImplementedError

    def _tool_get_item_detail(self, item_code: str) -> str:
        """특정 품목 코드의 self._records를 필터링하여 JSON으로 반환.

        TODO: item_code 일치하는 레코드만 추출 → 날짜/구분/수량/단위/비고 dict → json.dumps
        """
        raise NotImplementedError

    def _tool_generate_report(self) -> str:
        """품목 수, 이상 징후 수, 마이너스 재고 품목 목록 등을 JSON으로 반환.

        TODO: 요약 dict 생성 → json.dumps
        """
        raise NotImplementedError

    async def run(self, user_query: str, max_steps: int = 6) -> str:
        """사용자 질문을 받아 MCP 에이전트 루프를 실행하고 최종 답변을 반환한다.

        Args:
            user_query: 자연어 질문 (예: "마이너스 재고 품목이 있어?")
            max_steps: 최대 도구 호출 횟수 (무한루프 방지)

        TODO (agentic loop):
        1. system + user 메시지로 초기 messages 구성
        2. max_steps 횟수만큼 반복:
           a. client.chat.completions.create(tools=_TOOLS, tool_choice="auto")
           b. tool_calls 없으면 → 최종 답변 반환
           c. tool_calls 있으면 → _handle_tool() 실행 후 messages에 tool 결과 추가
        3. max_steps 초과 시 안내 메시지 반환
        """
        raise NotImplementedError

    async def run_mock(self, user_query: str) -> str:
        """API 키 없이 테스트할 수 있는 모의 실행.

        TODO: self._alerts를 텍스트로 포맷하여 간단한 응답 반환
        """
        raise NotImplementedError

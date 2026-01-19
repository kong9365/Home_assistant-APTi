"""APT.i Webhook 기반 API 클라이언트."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .const import LOGGER


@dataclass
class APTiData:
    """APT.i 데이터 구조."""

    # 사용자 정보
    dong_ho: str = ""
    apt_name: str = ""

    # 관리비 정보
    maint_items: list[dict] = field(default_factory=list)
    maint_payment: dict = field(default_factory=dict)

    # 에너지 정보
    energy_category: list[dict] = field(default_factory=list)
    energy_type: list[dict] = field(default_factory=list)

    # 납부 내역
    payment_history: list[dict] = field(default_factory=list)

    # 상태
    last_update: str = ""


class APTiAPI:
    """APT.i Webhook 기반 API 클라이언트.

    GitHub Actions에서 Webhook으로 데이터를 수신합니다.
    """

    def __init__(self, webhook_id: str) -> None:
        """초기화."""
        self.webhook_id = webhook_id
        self._logged_in = False
        self.data = APTiData()

    def update_from_webhook(self, payload: dict) -> None:
        """Webhook 페이로드로 데이터 업데이트."""
        LOGGER.info("Webhook 데이터 수신")

        self.data.dong_ho = payload.get("dong_ho", "")
        self.data.maint_items = payload.get("maint_items", [])
        self.data.maint_payment = payload.get("maint_payment", {})
        self.data.energy_category = payload.get("energy_category", [])
        self.data.energy_type = payload.get("energy_type", [])
        self.data.payment_history = payload.get("payment_history", [])
        self.data.last_update = payload.get("timestamp", datetime.now().isoformat())

        self._logged_in = True

        LOGGER.info(
            "데이터 업데이트 완료 - 동호: %s, 관리비: %d항목, 에너지: %d항목",
            self.data.dong_ho,
            len(self.data.maint_items),
            len(self.data.energy_category),
        )

    async def login(self) -> bool:
        """로그인 (Webhook 방식에서는 사용하지 않음)."""
        return True

    async def fetch_all_data(self) -> APTiData:
        """데이터 반환 (Webhook으로 이미 수신된 데이터)."""
        return self.data

    async def close(self) -> None:
        """세션 종료 (Webhook 방식에서는 필요 없음)."""
        pass

    @property
    def logged_in(self) -> bool:
        """데이터 수신 여부."""
        return self._logged_in

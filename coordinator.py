"""DataUpdateCoordinator for APT.i integration."""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import APTiAPI, APTiData
from .const import (
    DOMAIN,
    LOGGER,
    CONF_WEBHOOK_ID,
)


class APTiDataUpdateCoordinator(DataUpdateCoordinator[APTiData]):
    """APT.i Data Update Coordinator.

    Webhook 방식으로 동작하므로 주기적 업데이트는 하지 않습니다.
    GitHub Actions에서 Webhook으로 데이터를 전송하면 업데이트됩니다.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=None,  # Webhook 방식이므로 주기적 업데이트 없음
        )

        self.hass = hass
        self.entry = entry

        # API 클라이언트 생성
        self.api = APTiAPI(
            webhook_id=entry.data[CONF_WEBHOOK_ID],
        )

        LOGGER.info("APT.i Coordinator 초기화 (Webhook 방식)")

    async def _async_update_data(self) -> APTiData:
        """데이터 업데이트 (Webhook으로 이미 수신된 데이터 반환)."""
        return self.api.data

    def handle_webhook(self, payload: dict) -> None:
        """Webhook 데이터 처리."""
        self.api.update_from_webhook(payload)
        self.async_set_updated_data(self.api.data)

    @property
    def dong_ho(self) -> str:
        """동호 정보 반환."""
        if self.data:
            return self.data.dong_ho
        return ""

    @property
    def apt_name(self) -> str:
        """아파트 이름 반환."""
        if self.data:
            return self.data.apt_name
        return "APT.i"

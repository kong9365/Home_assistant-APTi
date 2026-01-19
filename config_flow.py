"""Config flow for APT.i integration."""
from __future__ import annotations

import secrets
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.network import get_url
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    LOGGER,
    CONF_WEBHOOK_ID,
    CONF_APT_NAME,
)


class APTiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for APT.i."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self._webhook_id: str | None = None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            apt_name = user_input.get(CONF_APT_NAME, "APT.i")

            # 고유한 webhook_id 생성
            self._webhook_id = secrets.token_hex(16)

            # 중복 체크
            await self.async_set_unique_id(self._webhook_id)
            self._abort_if_unique_id_configured()

            # 엔트리 생성
            return self.async_create_entry(
                title=f"APT.i ({apt_name})",
                data={
                    CONF_WEBHOOK_ID: self._webhook_id,
                    CONF_APT_NAME: apt_name,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_APT_NAME, default="우리 아파트"): cv.string,
                }
            ),
            errors=errors,
            description_placeholders={
                "webhook_info": "설정 완료 후 Webhook URL이 표시됩니다.",
            },
        )

    async def async_step_import(self, import_data: dict) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_data)

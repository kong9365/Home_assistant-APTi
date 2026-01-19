"""The APT.i component."""

from __future__ import annotations

from aiohttp import web

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.webhook import (
    async_register,
    async_unregister,
)

from .coordinator import APTiDataUpdateCoordinator
from .const import DOMAIN, LOGGER, PLATFORMS, CONF_WEBHOOK_ID


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the APT.i integration."""
    coordinator = APTiDataUpdateCoordinator(hass, entry)

    entry.runtime_data = coordinator

    # Webhook 등록
    webhook_id = entry.data[CONF_WEBHOOK_ID]
    async_register(
        hass,
        DOMAIN,
        "APT.i Data",
        webhook_id,
        handle_webhook,
    )
    LOGGER.info("Webhook 등록 완료: %s", webhook_id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def handle_webhook(
    hass: HomeAssistant, webhook_id: str, request: web.Request
) -> web.Response:
    """Handle incoming webhook from GitHub Actions."""
    try:
        payload = await request.json()
        LOGGER.info("Webhook 수신: %s", webhook_id)

        # webhook_id로 해당 entry 찾기
        for entry in hass.config_entries.async_entries(DOMAIN):
            if entry.data.get(CONF_WEBHOOK_ID) == webhook_id:
                coordinator: APTiDataUpdateCoordinator = entry.runtime_data
                coordinator.handle_webhook(payload)
                return web.Response(text="OK", status=200)

        LOGGER.warning("일치하는 entry를 찾을 수 없음: %s", webhook_id)
        return web.Response(text="Entry not found", status=404)

    except Exception as err:
        LOGGER.error("Webhook 처리 오류: %s", err)
        return web.Response(text=str(err), status=500)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the APT.i integration."""
    # Webhook 해제
    webhook_id = entry.data[CONF_WEBHOOK_ID]
    async_unregister(hass, webhook_id)
    LOGGER.info("Webhook 해제: %s", webhook_id)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok

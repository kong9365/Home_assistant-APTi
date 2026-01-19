"""Base class for APT.i entities."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import APTiDataUpdateCoordinator
from .const import DOMAIN


class APTiEntity(CoordinatorEntity[APTiDataUpdateCoordinator]):
    """APT.i 기본 엔티티."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: APTiDataUpdateCoordinator,
        device_name: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._device_name = device_name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information."""
        dong = self.coordinator.dong_ho[:4].lstrip("0") if self.coordinator.dong_ho else ""
        ho = self.coordinator.dong_ho[4:].lstrip("0") if self.coordinator.dong_ho else ""
        dong_ho_str = f"{dong}동 {ho}호" if dong and ho else ""

        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.coordinator.entry.entry_id}_{self._device_name}")},
            manufacturer="APT.i",
            model="APT.i",
            name=f"{self._device_name} ({dong_ho_str})" if dong_ho_str else self._device_name,
            configuration_url="https://www.apti.co.kr",
        )

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return self.coordinator.last_update_success

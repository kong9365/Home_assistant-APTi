"""APT.i Sensor Platform."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)

from .coordinator import APTiDataUpdateCoordinator
from .entity import APTiEntity
from .const import (
    LOGGER,
    ICON_MONEY,
    ICON_ELECTRICITY,
    ICON_WATER,
    ICON_HEATING,
    ICON_RECEIPT,
    ICON_CALENDAR,
    UNIT_KRW,
    ENERGY_ICONS,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up APT.i sensors."""
    coordinator: APTiDataUpdateCoordinator = entry.runtime_data

    entities: list[SensorEntity] = []

    # 관리비 총액 센서
    entities.append(APTiMaintenanceTotalSensor(coordinator))

    # 관리비 납부 마감일 센서
    entities.append(APTiMaintenanceDeadlineSensor(coordinator))

    # 관리비 항목별 센서
    if coordinator.data and coordinator.data.maint_items:
        for item in coordinator.data.maint_items:
            entities.append(APTiMaintenanceItemSensor(coordinator, item))

    # 에너지 카테고리별 센서
    if coordinator.data and coordinator.data.energy_category:
        for energy in coordinator.data.energy_category:
            entities.append(APTiEnergyCategorySensor(coordinator, energy))

    # 에너지 종류별 센서
    if coordinator.data and coordinator.data.energy_type:
        for energy in coordinator.data.energy_type:
            entities.append(APTiEnergyTypeSensor(coordinator, energy))

    # 최근 납부내역 센서
    entities.append(APTiPaymentHistorySensor(coordinator))

    async_add_entities(entities)
    LOGGER.info("APT.i 센서 %d개 등록 완료", len(entities))


class APTiMaintenanceTotalSensor(APTiEntity, SensorEntity):
    """관리비 총액 센서."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UNIT_KRW
    _attr_icon = ICON_MONEY

    def __init__(self, coordinator: APTiDataUpdateCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, "관리비")
        self._attr_unique_id = f"{coordinator.entry.entry_id}_maint_total"
        self._attr_translation_key = "maint_total"
        self._attr_name = "납부할 금액"

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        if not self.coordinator.data:
            return None

        payment = self.coordinator.data.maint_payment
        if payment and "amount" in payment:
            try:
                return int(payment["amount"])
            except (ValueError, TypeError):
                return None
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}

        payment = self.coordinator.data.maint_payment
        attrs = {}

        if payment:
            if "charged" in payment:
                attrs["부과금액"] = f"{int(payment['charged']):,}원"
            if "month" in payment:
                attrs["부과월"] = f"{payment['month']}월"
            if "deadline" in payment:
                attrs["납부마감일"] = payment["deadline"]
            if "status" in payment:
                attrs["상태"] = payment["status"]

        # 관리비 항목 요약
        if self.coordinator.data.maint_items:
            items = self.coordinator.data.maint_items
            attrs["항목수"] = len(items)

            # 상위 3개 항목
            sorted_items = sorted(
                items,
                key=lambda x: int(x.get("current", 0) or 0),
                reverse=True
            )[:3]
            for i, item in enumerate(sorted_items, 1):
                attrs[f"항목{i}"] = f"{item['item']}: {int(item['current']):,}원"

        return attrs


class APTiMaintenanceDeadlineSensor(APTiEntity, SensorEntity):
    """관리비 납부 마감일 센서."""

    _attr_icon = ICON_CALENDAR

    def __init__(self, coordinator: APTiDataUpdateCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, "관리비")
        self._attr_unique_id = f"{coordinator.entry.entry_id}_maint_deadline"
        self._attr_translation_key = "maint_deadline"
        self._attr_name = "납부마감일"

    @property
    def native_value(self) -> str | None:
        """Return the state."""
        if not self.coordinator.data:
            return None

        payment = self.coordinator.data.maint_payment
        if payment and "deadline" in payment:
            return payment["deadline"]
        return None


class APTiMaintenanceItemSensor(APTiEntity, SensorEntity):
    """관리비 항목별 센서."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UNIT_KRW
    _attr_icon = ICON_MONEY

    def __init__(
        self,
        coordinator: APTiDataUpdateCoordinator,
        item: dict,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, "관리비")
        self._item_name = item.get("item", "")
        self._attr_unique_id = f"{coordinator.entry.entry_id}_maint_{self._item_name}"
        self._attr_name = self._item_name

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        if not self.coordinator.data:
            return None

        for item in self.coordinator.data.maint_items:
            if item.get("item") == self._item_name:
                try:
                    return int(item.get("current", 0) or 0)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}

        for item in self.coordinator.data.maint_items:
            if item.get("item") == self._item_name:
                attrs = {}
                if "previous" in item:
                    try:
                        attrs["전월"] = f"{int(item['previous']):,}원"
                    except (ValueError, TypeError):
                        attrs["전월"] = item["previous"]

                if "change" in item:
                    try:
                        change = int(item["change"])
                        attrs["증감"] = f"{change:+,}원"
                    except (ValueError, TypeError):
                        attrs["증감"] = item["change"]

                return attrs
        return {}


class APTiEnergyCategorySensor(APTiEntity, SensorEntity):
    """에너지 카테고리별 센서."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UNIT_KRW

    def __init__(
        self,
        coordinator: APTiDataUpdateCoordinator,
        energy: dict,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, "에너지")
        self._energy_type = energy.get("type", "")
        self._attr_unique_id = f"{coordinator.entry.entry_id}_energy_{self._energy_type}"
        self._attr_name = f"{self._energy_type} 요금"
        self._attr_icon = ENERGY_ICONS.get(self._energy_type, ICON_ELECTRICITY)

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        if not self.coordinator.data:
            return None

        for energy in self.coordinator.data.energy_category:
            if energy.get("type") == self._energy_type:
                try:
                    return int(energy.get("cost", 0) or 0)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}

        for energy in self.coordinator.data.energy_category:
            if energy.get("type") == self._energy_type:
                attrs = {}
                if "usage" in energy:
                    attrs["사용량"] = energy["usage"]
                if "comparison" in energy:
                    attrs["비교"] = energy["comparison"]
                return attrs
        return {}


class APTiEnergyTypeSensor(APTiEntity, SensorEntity):
    """에너지 종류별 상세 센서."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = UNIT_KRW

    def __init__(
        self,
        coordinator: APTiDataUpdateCoordinator,
        energy: dict,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, "에너지")
        self._energy_type = energy.get("type", "")
        self._attr_unique_id = f"{coordinator.entry.entry_id}_energy_type_{self._energy_type}"
        self._attr_name = f"{self._energy_type} 상세"
        self._attr_icon = ENERGY_ICONS.get(self._energy_type, ICON_ELECTRICITY)

    @property
    def native_value(self) -> int | None:
        """Return the state."""
        if not self.coordinator.data:
            return None

        for energy in self.coordinator.data.energy_type:
            if energy.get("type") == self._energy_type:
                try:
                    return int(energy.get("total", 0) or 0)
                except (ValueError, TypeError):
                    return None
        return None

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}

        for energy in self.coordinator.data.energy_type:
            if energy.get("type") == self._energy_type:
                attrs = {}
                if "comparison" in energy:
                    attrs["비교"] = energy["comparison"]

                # 상세 항목 (type, total, comparison 제외한 모든 키)
                for key, value in energy.items():
                    if key not in ("type", "total", "comparison"):
                        try:
                            attrs[key] = f"{int(value):,}원"
                        except (ValueError, TypeError):
                            attrs[key] = value
                return attrs
        return {}


class APTiPaymentHistorySensor(APTiEntity, SensorEntity):
    """납부내역 센서."""

    _attr_icon = ICON_RECEIPT

    def __init__(self, coordinator: APTiDataUpdateCoordinator) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, "납부내역")
        self._attr_unique_id = f"{coordinator.entry.entry_id}_payment_history"
        self._attr_translation_key = "payment_history"
        self._attr_name = "최근 납부"

    @property
    def native_value(self) -> str | None:
        """Return the state."""
        if not self.coordinator.data:
            return None

        history = self.coordinator.data.payment_history
        if history and len(history) > 0:
            latest = history[0]
            return latest.get("status", "알 수 없음")
        return "내역 없음"

    @property
    def extra_state_attributes(self) -> dict:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}

        history = self.coordinator.data.payment_history
        attrs = {"총건수": len(history) if history else 0}

        if history and len(history) > 0:
            latest = history[0]
            if "date" in latest:
                attrs["결제일"] = latest["date"]
            if "amount" in latest:
                try:
                    attrs["결제금액"] = f"{int(latest['amount']):,}원"
                except (ValueError, TypeError):
                    attrs["결제금액"] = latest["amount"]
            if "billing_month" in latest:
                attrs["청구월"] = latest["billing_month"]
            if "method" in latest:
                attrs["결제방법"] = latest["method"]
            if "bank" in latest:
                attrs["은행"] = latest["bank"]

            # 최근 5건 요약
            for i, item in enumerate(history[:5], 1):
                if "date" in item and "amount" in item:
                    try:
                        attrs[f"내역{i}"] = f"{item['date']}: {int(item['amount']):,}원"
                    except (ValueError, TypeError):
                        attrs[f"내역{i}"] = f"{item['date']}: {item['amount']}"

        return attrs

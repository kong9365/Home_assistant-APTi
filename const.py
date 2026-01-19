"""APT.i 통합을 위한 상수 정의."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.const import Platform

DOMAIN = "apti"
VERSION = "2.1.0"

PLATFORMS: list[Platform] = [Platform.SENSOR]

LOGGER = logging.getLogger(__package__)

# 업데이트 간격 (기본 24시간, 최소 1시간)
DEFAULT_SCAN_INTERVAL = timedelta(hours=24)
MIN_SCAN_INTERVAL = timedelta(hours=1)

# Base URL for 단지 홈페이지
BASE_URL = "https://xn--3-v85erd9xh0vctai95f4a637hvqbda945jmkaw30h.apti.co.kr"

# Page codes
PAGE_CODE_MAINTENANCE = "AAEB"
PAGE_CODE_ENERGY = "AAEC"
PAGE_CODE_PAYMENT_HISTORY = "AAFH"

# 설정 키
CONF_USER_ID = "user_id"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_APT_NAME = "apt_name"
CONF_WEBHOOK_ID = "webhook_id"

# 데이터 키
DATA_COORDINATOR = "coordinator"
DATA_API = "api"

# 센서 타입
SENSOR_TYPE_MAINT_TOTAL = "maint_total"
SENSOR_TYPE_MAINT_ITEM = "maint_item"
SENSOR_TYPE_ENERGY = "energy"
SENSOR_TYPE_PAYMENT = "payment"

# 아이콘
ICON_MONEY = "mdi:currency-krw"
ICON_ELECTRICITY = "mdi:flash"
ICON_WATER = "mdi:water"
ICON_GAS = "mdi:fire"
ICON_HEATING = "mdi:radiator"
ICON_CALENDAR = "mdi:calendar"
ICON_RECEIPT = "mdi:receipt"
ICON_HOME = "mdi:home-city"

# 에너지 타입별 아이콘
ENERGY_ICONS = {
    "전기": ICON_ELECTRICITY,
    "온수": ICON_WATER,
    "수도": ICON_WATER,
    "난방": ICON_HEATING,
    "가스": ICON_GAS,
}

# 단위
UNIT_KRW = "원"
UNIT_KWH = "kWh"
UNIT_M3 = "m³"
UNIT_GCAL = "Gcal"

# 에너지 타입별 단위
ENERGY_UNITS = {
    "전기": UNIT_KWH,
    "온수": UNIT_M3,
    "수도": UNIT_M3,
    "난방": UNIT_GCAL,
    "가스": UNIT_M3,
}

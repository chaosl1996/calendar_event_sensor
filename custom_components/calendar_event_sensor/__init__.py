"""
Calendar Event Sensor 集成的主入口文件
"""
import logging
from homeassistant.config_entries import ConfigEntryNotReady
from .const import DOMAIN, PLATFORMS, CONF_CALENDAR_ENTITY

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """设置集成组件。"""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass, entry):
    """从配置项设置集成。"""
    calendar_entity = entry.data[CONF_CALENDAR_ENTITY]
    
    # 检查日历实体是否存在且可用
    if calendar_entity not in hass.states.async_entity_ids("calendar"):
        _LOGGER.error("日历实体 %s 不存在或不可用", calendar_entity)
        raise ConfigEntryNotReady(f"日历实体 {calendar_entity} 不存在或不可用")
    
    hass.data[DOMAIN][entry.entry_id] = entry.data
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        return True
    except Exception as error:
        _LOGGER.error("转发平台设置失败: %s", error)
        # 这里我们不再抛出 ConfigEntryNotReady，而是返回 False
        return False

async def async_unload_entry(hass, entry):
    """卸载配置项。"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
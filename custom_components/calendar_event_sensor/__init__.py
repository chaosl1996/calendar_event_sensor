"""
Calendar Event Sensor 集成的主入口文件
"""
import asyncio
import logging
from homeassistant.config_entries import ConfigEntryNotReady
from homeassistant.helpers.event import async_track_state_added_domain
from .const import DOMAIN, PLATFORMS, CONF_CALENDAR_ENTITY

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    """设置集成组件。"""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass, entry):
    """从配置项设置集成。"""
    calendar_entity = entry.data[CONF_CALENDAR_ENTITY]

    # 日历实体由 remote_calendar/local_calendar 等集成在启动后期注册，
    # 等待其出现（最多 120s）而不是立即报错，消除重启时的启动顺序竞态
    if calendar_entity not in hass.states.async_entity_ids("calendar"):
        _LOGGER.info("等待日历实体 %s 出现…", calendar_entity)
        ready = asyncio.Event()
        remove = async_track_state_added_domain(hass, ["calendar"], lambda _ev: ready.set())
        try:
            await asyncio.wait_for(ready.wait(), timeout=120)
        except asyncio.TimeoutError:
            remove()
            _LOGGER.warning("等待日历实体 %s 超时", calendar_entity)
            raise ConfigEntryNotReady(f"日历实体 {calendar_entity} 不存在或不可用")
        remove()
    
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
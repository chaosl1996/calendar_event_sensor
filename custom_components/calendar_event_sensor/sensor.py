"""
Calendar Event Sensor 集成的传感器实现
"""
import datetime
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntryNotReady
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import utcnow
from .const import DOMAIN, CONF_CALENDAR_ENTITY, CONF_EVENT_COUNT, CONF_FILTER_WORD, CONF_FILTER_WORDS, CONF_INTEGRATION_NAME

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
):
    """设置传感器平台。"""
    calendar_entity = config_entry.data[CONF_CALENDAR_ENTITY]
    event_count = config_entry.data[CONF_EVENT_COUNT]
    integration_name = config_entry.data[CONF_INTEGRATION_NAME]
    # 获取多个筛选词
    filter_words = config_entry.data.get(CONF_FILTER_WORDS, [])
    # 兼容旧配置
    if not filter_words and CONF_FILTER_WORD in config_entry.data:
        filter_words = [config_entry.data[CONF_FILTER_WORD]]

    # 检查日历实体是否存在且可用 (移除异常，改为记录日志和返回False)
    if calendar_entity not in hass.states.async_entity_ids("calendar"):
        _LOGGER.error("日历实体 %s 不存在", calendar_entity)
        return False

    # 创建协调器
    coordinator = CalendarEventCoordinator(hass, calendar_entity, event_count, filter_words)
    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed as error:
        _LOGGER.error("获取日历事件失败: %s", error)
        return False

    # 创建传感器
    entities = []
    for i in range(min(event_count, len(coordinator.data))):
        entities.append(CalendarEventSensor(coordinator, calendar_entity, i + 1, integration_name))

    async_add_entities(entities, True)
    return True

class CalendarEventCoordinator(DataUpdateCoordinator):
    """日历事件协调器。"""
    def __init__(self, hass, calendar_entity, event_count, filter_words):
        """初始化协调器。"""
        self.calendar_entity = calendar_entity
        self.event_count = event_count
        self.filter_words = filter_words  # 存储多个筛选词
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=DOMAIN,
            update_interval=datetime.timedelta(minutes=30),
        )

    async def _async_update_data(self):
        """更新数据。"""
        # 计算未来2年的日期
        end_date = utcnow() + datetime.timedelta(days=730)
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")

        # 调用日历服务获取事件
        try:
            result = await self.hass.services.async_call(
                "calendar",
                "get_events",
                {
                    "entity_id": self.calendar_entity,
                    "end_date_time": end_date_str,
                },
                blocking=True,
                return_response=True,
            )

            # 过滤事件
            events = result.get(self.calendar_entity, {}).get("events", [])

            # 如果设置了筛选词，过滤事件摘要包含任一筛选词的事件
            if self.filter_words:
                events = [event for event in events if any(word in event.get("summary", "") for word in self.filter_words)]

            # 按开始时间排序
            events.sort(key=lambda x: x.get("start", ""))

            # 只返回指定数量的事件
            return events[:self.event_count]

        except Exception as error:
            raise UpdateFailed(f"Failed to fetch calendar events: {error}")

class CalendarEventSensor(SensorEntity):
    """日历事件传感器。"""
    _attr_icon = "mdi:calendar"

    def __init__(self, coordinator, calendar_entity, index, integration_name):
        """初始化传感器。"""
        self.coordinator = coordinator
        self.calendar_entity = calendar_entity
        self.index = index
        self.integration_name = integration_name
        self._attr_unique_id = f"{calendar_entity}_{integration_name}_{index}_event"
        
        # 中文数字映射
        chinese_numbers = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
                          6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}
        number_str = chinese_numbers.get(index, str(index))
        self._attr_name = f"未来第{number_str}个{integration_name}"

    async def async_added_to_hass(self):
        """当传感器添加到HASS时。"""
        self.async_on_remove(
            self.coordinator.async_add_listener(
                self._handle_coordinator_update
            )
        )

    @callback
    def _handle_coordinator_update(self):
        """处理协调器更新。"""
        self.async_write_ha_state()

    @property
    def available(self):
        """传感器是否可用。"""
        return (
            self.coordinator.last_update_success
            and len(self.coordinator.data) >= self.index
        )

    @property
    def native_value(self):
        """传感器的原生值。"""
        if not self.available:
            return None
        return self.coordinator.data[self.index - 1].get("summary", "")

    @property
    def extra_state_attributes(self):
        """传感器的额外属性。"""
        if not self.available:
            return {}

        event = self.coordinator.data[self.index - 1]
        start_time = event.get("start", "")
        end_time = event.get("end", "")

        # 计算倒计时
        if start_time:
            try:
                start_datetime = datetime.datetime.strptime(start_time, "%Y-%m-%d")
                start_datetime = start_datetime.replace(tzinfo=datetime.timezone.utc)
                now = utcnow()
                countdown = (start_datetime - now).total_seconds()
                countdown_days = max(0, int(countdown / 86400))
            except ValueError:
                countdown_days = None
        else:
            countdown_days = None

        return {
            "start_time": start_time,
            "end_time": end_time,
            "countdown_days": countdown_days,
        }

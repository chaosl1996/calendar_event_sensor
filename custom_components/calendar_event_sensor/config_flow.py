"""
Calendar Event Sensor 集成的配置流程
"""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.entity_registry import async_get
from .const import (
    DOMAIN, 
    CONF_CALENDAR_ENTITY, 
    CONF_EVENT_COUNT, 
    CONF_FILTER_WORD, 
    CONF_FILTER_WORDS, 
    CONF_INTEGRATION_NAME
)

class CalendarEventSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """处理日历事件传感器的配置流程。"""
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """处理初始配置步骤。"""
        errors = {}
    
        if user_input is not None:
            # 处理多个筛选词
            filter_words_input = user_input.get(CONF_FILTER_WORDS, "").strip()
            if filter_words_input:
                user_input[CONF_FILTER_WORDS] = [word.strip() for word in filter_words_input.split(",")]
            else:
                user_input[CONF_FILTER_WORDS] = []
    
            # 保留对旧筛选词的支持
            if CONF_FILTER_WORD in user_input and user_input[CONF_FILTER_WORD]:
                user_input[CONF_FILTER_WORDS] = [user_input[CONF_FILTER_WORD]]
            user_input.pop(CONF_FILTER_WORD, None)
    
            # 验证日历实体
            calendar_entity = user_input[CONF_CALENDAR_ENTITY]
            if not calendar_entity.startswith("calendar."):
                errors[CONF_CALENDAR_ENTITY] = "invalid_calendar_entity"
            else:
                # 创建唯一标识符，结合日历实体和集成名称
                integration_name = user_input.get(CONF_INTEGRATION_NAME, "default")
                unique_id = f"{calendar_entity}_{integration_name}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=integration_name, data=user_input)
    
        # 获取所有日历实体
        entity_registry = async_get(self.hass)
        calendars = [
            entity_id for entity_id in entity_registry.entities
            if entity_id.startswith("calendar.")
        ]
    
        if not calendars:
            errors["base"] = "no_calendar_entities"
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({}),
                errors=errors,
            )
    
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_INTEGRATION_NAME): str,  # 添加集成名称输入
                vol.Required(CONF_CALENDAR_ENTITY): vol.In(calendars),
                vol.Required(CONF_EVENT_COUNT, default=5): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
                vol.Optional(CONF_FILTER_WORDS, default=""): str,
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """获取选项流程。"""
        return CalendarEventSensorOptionsFlow(config_entry)

class CalendarEventSensorOptionsFlow(config_entries.OptionsFlow):
    """处理日历事件传感器的选项流程。"""
    def __init__(self, config_entry):
        """初始化选项流程。"""
        self.config_entry_id = config_entry.entry_id

    async def async_step_init(self, user_input=None):
        """处理选项初始化步骤。"""
        if user_input is not None:
            # 处理多个筛选词
            filter_words_input = user_input.get(CONF_FILTER_WORDS, "").strip()
            if filter_words_input:
                user_input[CONF_FILTER_WORDS] = [word.strip() for word in filter_words_input.split(",")]
            else:
                user_input[CONF_FILTER_WORDS] = []
            
            # 更新配置条目数据
            config_entry = self.hass.config_entries.async_get_entry(self.config_entry_id)
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input}
            )
            # 重新加载集成
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)

        # 获取所有日历实体
        entity_registry = async_get(self.hass)
        calendars = [
            entity_id for entity_id in entity_registry.entities
            if entity_id.startswith("calendar.")
        ]

        # 安全获取当前配置值
        current_name = self.config_entry.data.get(CONF_INTEGRATION_NAME, "")
        current_calendar = self.config_entry.data.get(CONF_CALENDAR_ENTITY, calendars[0] if calendars else "")
        current_event_count = self.config_entry.data.get(CONF_EVENT_COUNT, 5)
        current_filter_words = ", ".join(self.config_entry.data.get(CONF_FILTER_WORDS, []))

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_INTEGRATION_NAME, default=current_name): str,
                vol.Required(CONF_CALENDAR_ENTITY, default=current_calendar): vol.In(calendars),
                vol.Required(CONF_EVENT_COUNT, default=current_event_count): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
                vol.Optional(CONF_FILTER_WORDS, default=current_filter_words): str,
            }),
        )
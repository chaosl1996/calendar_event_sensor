"""
Calendar Event Sensor 集成的常量定义
"""
DOMAIN = "calendar_event_sensor"
PLATFORMS = ["sensor"]
CONF_CALENDAR_ENTITY = "calendar_entity"
CONF_EVENT_COUNT = "event_count"
CONF_FILTER_WORD = "filter_word"  # 保留旧常量以兼容现有配置
CONF_FILTER_WORDS = "filter_words"  # 新增：多个筛选词
CONF_INTEGRATION_NAME = "integration_name"  # 新增：自定义集成名称
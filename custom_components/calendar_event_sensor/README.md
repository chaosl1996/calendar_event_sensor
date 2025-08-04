# Calendar Event Sensor

一个 Home Assistant 自定义集成，用于从日历实体中提取事件并创建传感器。

## 功能特点

- 从指定日历实体中获取即将发生的事件
- 支持自定义集成名称，方便区分多个实例
- 支持多筛选词过滤事件
- 可配置获取的事件数量
- 同一日历可以配置多次
- 生成的实体名为"未来第X个[集成名]"

## 安装方法

### 手动安装
1. 下载或克隆此仓库
2. 将 `calendar_event_sensor` 文件夹复制到 Home Assistant 的 `custom_components` 目录下
3. 重启 Home Assistant

### 通过 HACS 安装
1. 打开 HACS
2. 点击 "集成"
3. 点击右上角的三个点，选择 "自定义存储库"
4. 输入仓库 URL 和类别（集成）
5. 点击 "添加"
6. 搜索 "Calendar Event Sensor" 并安装
7. 重启 Home Assistant

## 配置说明

### 基本配置
1. 在 Home Assistant 中，进入 "设置" -> "设备与服务" -> "集成"
2. 点击 "添加集成"，搜索 "Calendar Event Sensor"
3. 选择要监控的日历实体
4. 输入自定义集成名称（可选，默认为"日历事件"）
5. 设置要获取的事件数量（默认为5）
6. 输入筛选词（可选，多个词用逗号分隔）
7. 点击 "提交"

### 配置选项
- **日历实体**: 要监控的日历实体
- **集成名称**: 自定义集成名称，用于生成传感器名称
- **事件数量**: 要获取的即将发生的事件数量
- **筛选词**: 用于过滤事件标题的关键词，多个词用逗号分隔

## 使用示例

### 查看事件
配置完成后，系统将创建多个传感器实体，格式为"未来第X[集成名]"，例如：
- `sensor.future_1_calendar_event`
- `sensor.future_2_calendar_event`

每个传感器将显示对应事件的标题、开始时间和结束时间。

### 自动化示例
```yaml
automation:
  - alias: "提醒即将到来的会议"
    trigger:
      platform: state
      entity_id: sensor.future_1_work_events
      to: "团队周会"
    action:
      - service: notify.mobile_app_your_phone
        data:
          message: "10分钟后有团队周会"
```

## 已知问题
- 不支持重复事件的高级过滤
- 筛选词区分大小写
- 暂不支持日历事件的地点过滤

## 更新日志

### v1.0.0
- 初始版本
- 支持从日历实体获取事件
- 支持自定义集成名称
- 支持多筛选词过滤

## 贡献指南
1. Fork 此仓库
2. 创建功能分支 (`git checkout -b feature/fooBar`)
3. 提交更改 (`git commit -am 'Add some fooBar'`)
4. 推送到分支 (`git push origin feature/fooBar`)
5. 创建新的 Pull Request

## 联系我们
如有问题或建议，请在 GitHub 上提交 issue。
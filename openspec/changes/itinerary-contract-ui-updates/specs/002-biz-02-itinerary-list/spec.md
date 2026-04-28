## ADDED Requirements

### Requirement: Destination column does not show status tag
行程列表中目的地字段的显示区域 SHALL NOT 附加任何行程状态标签；状态 SHALL 仅在独立的状态列（或状态区域）中展示。

#### Scenario: 桌面端目的地单元格仅显示文本
- **WHEN** 用户查看桌面端行程列表 Table
- **THEN** 目的地列单元格仅显示目的地文本，不附加颜色标签或状态文字

#### Scenario: 移动端行程卡片目的地不带状态标签
- **WHEN** 用户查看移动端行程卡片列表
- **THEN** 行程卡片的目的地显示区域仅显示目的地文本，状态标签不紧跟目的地出现

## Purpose
产品管理：产品 CRUD，以及行程模板的自动生成与天数同步功能。

## Requirements

### Requirement: 产品表单支持根据天数一键生成行程模板骨架
在产品新增/编辑抽屉的行程模板区域，系统 SHALL 提供"根据天数生成"按钮；点击后，系统 SHALL 根据 `form.days`（最多取 30）生成对应数量的空白模板条目，替换现有 `itinerary_template`。

#### Scenario: 正常生成（无已有内容）
- **WHEN** 用户填写了有效天数（1–365），当前行程模板为空，点击"根据天数生成"
- **THEN** 系统生成 `Math.min(days, 30)` 条记录，每条 `seq` 从 1 开始递增，其余字段为空值

#### Scenario: 天数超过 30 时截断并提示
- **WHEN** `form.days` > 30，用户点击"根据天数生成"
- **THEN** 系统生成恰好 30 条记录，并通过 `message.warning` 提示"天数超过上限，已生成 30 天行程模板"

#### Scenario: 天数未填或无效时按钮禁用
- **WHEN** `form.days` 为 null、undefined 或 < 1
- **THEN** "根据天数生成"按钮处于 disabled 状态

#### Scenario: 已有内容时弹出覆盖确认
- **WHEN** `itinerary_template` 中至少一条记录的 `details` 非空，用户点击"根据天数生成"
- **THEN** 系统弹出 Modal.confirm 对话框，提供"确认生成"与"取消"选项

#### Scenario: 用户确认覆盖
- **WHEN** 出现覆盖确认对话框后，用户点击"确认生成"
- **THEN** 现有 `itinerary_template` 被替换为新生成的骨架条目

#### Scenario: 用户取消覆盖
- **WHEN** 出现覆盖确认对话框后，用户点击"取消"
- **THEN** `itinerary_template` 内容保持不变，对话框关闭

#### Scenario: 当前行程模板均为空白时不弹确认
- **WHEN** `itinerary_template` 有条目但所有条目的 `details` 均为空
- **THEN** 系统直接生成新骨架，不弹出覆盖确认对话框

### Requirement: 产品表单天数字段变化时自动同步行程模板数量
在产品新增/编辑抽屉中，系统 SHALL 监听 `form.days` 字段的变化；当天数变为有效值且当前行程模板**无实质内容**时，系统 SHALL 自动将 `itinerary_template` 条目数调整为 `Math.min(days, 30)`（约 400ms 防抖）。增量对齐：末尾追加或截断尾部，不清空已有内容。

#### Scenario: 新增产品时填写天数自动生成骨架
- **WHEN** 用户在新增抽屉中将 `days` 从空值输入为有效值（如 5），且 `itinerary_template` 为空
- **THEN** 系统在约 400ms 防抖延迟后自动生成 5 条空白模板记录

#### Scenario: 修改天数时追加不足的条目
- **WHEN** 当前 `itinerary_template` 有 3 条空白条目，用户将 `days` 改为 5
- **THEN** 系统自动在末尾追加 2 条新空白条目，`seq` 接续为 4、5

#### Scenario: 修改天数时截断超出的条目
- **WHEN** 当前 `itinerary_template` 有 5 条条目（均无 details 内容），用户将 `days` 改为 3
- **THEN** 系统自动移除末尾 2 条，保留前 3 条

#### Scenario: 已有实质内容时不自动覆盖
- **WHEN** `itinerary_template` 中至少一条记录的 `details` 非空，用户修改 `days` 值
- **THEN** 系统**不触发**自动填充，`itinerary_template` 内容保持不变

#### Scenario: 防抖期间快速修改天数只触发最后一次
- **WHEN** 用户在 400ms 内连续调整天数
- **THEN** 系统仅以最终值触发一次生成，中间值不产生多余操作

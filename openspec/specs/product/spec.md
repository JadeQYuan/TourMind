
## Purpose
产品管理：支持产品的分页查询、搜索、新增、编辑、禁用、查看详情、行程模板自动生成与天数同步等操作。

## Fields
| 字段名              | 中文名         | 类型     | 约束/说明                         |
|-------------------|--------------|---------|----------------------------------|
| id                | 产品ID        | int     | 主键，自增                        |
| name              | 产品名称      | string  | 必填，1-200 字符                  |
| destination       | 目的地        | string  | 必填，1-200 字符                  |
| days              | 天数          | int     | 必填，1-365，决定行程模板天数      |
| price             | 价格          | number  | 必填，单位：元，精度2位            |
| includes          | 费用包含      | string  | 可选，长文本                       |
| excludes          | 费用不含      | string  | 可选，长文本                       |
| cancellation_policy | 取消政策     | string  | 可选，长文本                       |
| travel_notice     | 出行提示      | string  | 可选，长文本                       |
| important_tips    | 重要提示      | string  | 可选，长文本                       |
| itinerary_template | 行程模板     | array   | 可选，JSON 数组，见下方说明         |
| remark            | 备注          | string  | 可选，最长 128 字符                |
| status            | 状态          | string  | 必填，枚举：enabled/disabled，默认 enabled |
| created_by        | 创建者ID      | int     | 外键，关联 users.id               |
| created_at        | 创建时间      | string  | 创建时间，ISO8601                  |
| updated_at        | 更新时间      | string  | 更新时间，ISO8601                  |

> itinerary_template 字段为 JSON 数组，每条包含：
> - seq（天序号，int）
> - details（行程内容，string，可空）
> - accommodation_area（住宿区域，string，可空）
> - notes（备注，string，可空）

## Requirements


### Requirement: 产品列表查询
系统 SHALL 支持产品列表的展示，支持按产品名称模糊搜索、按状态筛选。

#### Scenario: 加载产品列表
- **WHEN** 用户进入产品管理页面
- **THEN** 系统自动加载产品数据

#### Scenario: 输入关键词搜索
- **WHEN** 用户在搜索框输入关键词并提交
- **THEN** 系统按关键词过滤产品列表，显示匹配结果

#### Scenario: 按状态筛选
- **WHEN** 用户选择状态筛选条件
- **THEN** 系统按状态过滤产品列表


### Requirement: 新增/编辑产品
系统 SHALL 支持通过表单新增产品和编辑产品信息，表单字段包括：名称、目的地、天数、价格、费用包含、费用不含、取消政策、出行提示、重要提示、行程模板、备注、状态。

#### Scenario: 新建产品表单校验
- **WHEN** 用户点击“新增产品”并填写表单后提交
- **THEN** 系统校验必填项（名称、目的地、天数、价格、状态），校验通过则保存新产品，失败则显示错误提示

#### Scenario: 编辑产品信息
- **WHEN** 用户在产品列表点击“编辑”并修改信息后保存
- **THEN** 系统保存变更


### Requirement: 产品状态变更
系统 SHALL 支持用户在产品列表中对产品进行禁用和启用操作。

#### Scenario: 禁用产品
- **WHEN** 用户在产品列表点击“禁用”按钮
- **THEN** 系统将该产品状态设为禁用

#### Scenario: 启用产品
- **WHEN** 用户在产品列表点击“启用”按钮
- **THEN** 系统将该产品状态设为启用


### Requirement: 查看产品详情
系统 SHALL 支持查看产品详细信息，展示所有字段。

#### Scenario: 查看详情抽屉
- **WHEN** 用户点击产品列表的“查看”按钮
- **THEN** 系统右侧弹出抽屉，展示该产品的全部信息


### Requirement: 产品表单支持根据天数一键生成行程模板骨架
在产品新增/编辑抽屉的行程模板区域，系统 SHALL 支持手动添加/删除行程模板条目；当天数字段变化时，系统 SHALL 自动同步行程模板数量（约 400ms 防抖）。

#### Scenario: 手动添加行程条目
- **WHEN** 用户点击“+ 添加一天”按钮
- **THEN** 系统在行程模板末尾添加一条新条目，seq 自动递增

#### Scenario: 手动删除行程条目
- **WHEN** 用户点击某行程条目的“删除”按钮
- **THEN** 系统删除该条目，其余条目 seq 自动重新排序

#### Scenario: 天数变化时自动同步（无已有内容）
- **WHEN** 用户填写或修改天数，当前行程模板无实质内容
- **THEN** 系统自动调整行程模板条目数量为 Math.min(days, 30)，增量追加或截断尾部

#### Scenario: 天数超过 30 时截断并提示
- **WHEN** days > 30
- **THEN** 系统最多生成 30 条记录，并提示“天数超过上限，已自动生成 30 天行程模板”

#### Scenario: 已有实质内容时不自动覆盖
- **WHEN** itinerary_template 中至少一条记录的 details 非空，用户修改 days 值
- **THEN** 系统不触发自动调整，行程模板内容保持不变

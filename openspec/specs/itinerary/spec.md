
## Purpose
行程管理：支持行程的新增、编辑、查看、列表分页、自动填充、分享、状态流转等操作。

## Fields
| 字段名             | 中文名         | 类型     | 约束/说明                         |
|------------------|--------------|---------|----------------------------------|
| id               | 行程ID        | int     | 主键，自增                        |
| origin           | 出发地        | string  | 必填，最大100字符                 |
| order_id         | 订单ID        | int     | 关联订单，唯一                    |
| destination      | 目的地        | string  | 必填，自动联动订单产品，最大200字符|
| days             | 天数          | int     | 必填，1-365，自动同步订单/产品天数  |
| departure_date   | 出发日期      | date    | 必填                             |
| notes            | 备注          | string  | 可选，文本                        |
| customer_name    | 客户姓名      | string  | 必填，最大100字符                 |
| customer_phone   | 客户电话      | string  | 必填，最大20字符                  |
| pax              | 出行人数      | int     | 必填                             |
| travelers        | 出行人员      | string  | 可选，单行文本，逗号分隔           |
| details          | 行程明细      | array   | 必填，数组，每天一条，见下方说明    |
| product_id       | 产品ID        | int     | 可选，关联产品                    |
| status           | 状态          | string  | 必填，枚举：not_started/in_progress/completed/canceled |
| share_token      | 分享码        | string  | 自动生成，唯一，永久有效           |
| created_by       | 创建者ID      | int     | 必填，关联用户                    |
| created_at       | 创建时间      | string  | 创建时间，ISO8601                  |
| updated_at       | 更新时间      | string  | 更新时间，ISO8601                  |

&gt; details 字段为数组，每条包含：
&gt; - day_number（天序号，int）
&gt; - date（日期，string，ISO8601）
&gt; - details（行程内容，string）
&gt; - accommodation_area（住宿区域，string，可空）
&gt; - notes（备注，string，可空）
&gt; - attachments（附件列表，array，可空）
&gt;   - file_key（文件key，string）
&gt;   - file_url（文件URL，string）
&gt;   - original_name（原始文件名，string）
&gt;   - created_at（创建时间，string，ISO8601）

## Requirements

### Requirement: 行程列表分页查询
系统 SHALL 支持行程列表的分页展示，默认每页 20 条。

#### Scenario: 分页加载行程列表
- **WHEN** 用户进入行程管理页面
- **THEN** 系统自动加载第一页行程数据，显示分页控件，可切换页码加载对应数据

### Requirement: 行程搜索
系统 SHALL 支持按目的地、出行人员、订单号等字段模糊搜索。

#### Scenario: 输入关键词搜索
- **WHEN** 用户在搜索框输入关键词并提交
- **THEN** 系统按关键词过滤行程列表，显示匹配结果

### Requirement: 行程新增/编辑
系统 SHALL 支持行程的新增和编辑，表单校验必填项，自动填充目的地、天数、明细等，部分字段只读不可编辑。

#### Scenario: 新增行程
- **WHEN** 用户点击"新增行程"并填写表单后提交
- **THEN** 系统校验必填项，校验通过则保存新行程，失败则显示错误提示

#### Scenario: 编辑行程
- **WHEN** 用户在行程列表点击"编辑"并修改信息后保存
- **THEN** 系统保存变更，部分字段只读不可编辑

### Requirement: 查看行程详情
系统 SHALL 支持查看行程详细信息，展示所有字段。

#### Scenario: 查看详情抽屉
- **WHEN** 用户点击行程列表的"查看"按钮
- **THEN** 系统右侧弹出抽屉，展示该行程的全部信息

### Requirement: 关联订单自动填充目的地
用户选择订单后，系统 SHALL 自动将订单关联产品的目的地填入行程表单。

#### Scenario: 选择订单自动填充目的地
- **WHEN** 用户在行程表单中选择订单
- **THEN** 目的地字段自动填充为订单产品的目的地

### Requirement: 出行人员为单行文本
系统 SHALL 支持出行人员以逗号分隔的单行文本输入。

#### Scenario: 输入出行人员
- **WHEN** 用户在表单中填写出行人员
- **THEN** 系统保存为单行字符串，逗号分隔

### Requirement: 选择订单后自动填充每日明细
用户选择订单后，系统 SHALL 自动根据产品模板填充每日明细。

#### Scenario: 自动填充每日明细
- **WHEN** 用户选择订单且有产品模板
- **THEN** 系统自动生成与天数一致的明细条目

### Requirement: 已有内容时确认覆盖
当行程明细已有内容时，自动填充需弹出确认覆盖提示。

#### Scenario: 明细有内容时弹窗确认
- **WHEN** 用户选择订单且明细有内容
- **THEN** 系统弹窗确认，用户确认后才覆盖

### Requirement: 无模板或无产品时友好提示
无产品模板或未选择产品时，系统 SHALL 友好提示用户。

#### Scenario: 无模板提示
- **WHEN** 用户选择订单但无产品模板
- **THEN** 系统提示"无可用模板"

### Requirement: 行程编辑页通过路由加载数据
通过路由参数访问编辑页时，系统 SHALL 自动加载对应行程数据。

#### Scenario: 路由加载行程数据
- **WHEN** 用户通过路由进入编辑页
- **THEN** 系统自动加载并填充表单

### Requirement: 行程列表操作区
系统 SHALL 支持在列表中查看、编辑、分享等操作，采用抽屉展示详情。

#### Scenario: 列表操作抽屉
- **WHEN** 用户在列表点击操作按钮
- **THEN** 右侧抽屉展示详情或编辑表单

### Requirement: 行程表单双列布局
表单采用双列布局，提升信息密度。

#### Scenario: 双列布局展示
- **WHEN** 用户打开行程表单
- **THEN** 表单以两列方式展示主要字段

### Requirement: 公开分享页独立视图
每个行程可生成独立的公开分享页，支持通过分享码访问。

#### Scenario: 生成分享页
- **WHEN** 用户点击"分享"按钮
- **THEN** 系统生成分享链接，外部可访问

### Requirement: 分享按钮仅活跃状态可见
仅 not_started 和 in_progress 状态下可见分享按钮。

#### Scenario: 状态判断分享按钮
- **WHEN** 行程状态为 not_started 或 in_progress
- **THEN** 显示分享按钮，否则隐藏

### Requirement: 行程状态变更
系统 SHALL 支持行程的状态流转：
- not_started → in_progress
- in_progress → completed
- in_progress → canceled
- completed → in_progress
- canceled → in_progress

完成仅在所有明细日期已过时可用，撤销限时 24 小时内可用，已完成行程可回退为进行中。

#### Scenario: 行程结束后可完成
- **WHEN** 当前日期大于所有明细日期
- **THEN** "完成"按钮可用

#### Scenario: 撤销限时
- **WHEN** 行程完成且24小时内
- **THEN** "撤销"按钮可用，超时禁用

#### Scenario: 回退为进行中
- **WHEN** 用户点击"回退"按钮
- **THEN** 行程状态变为 in_progress

### Requirement: 分享码自动生成
新建行程时，系统 SHALL 自动生成唯一分享码。

#### Scenario: 自动生成分享码
- **WHEN** 新建行程成功
- **THEN** 系统生成唯一分享码

### Requirement: 分享无需API
行程分享链接为静态生成，无需额外API调用。

#### Scenario: 访问分享链接
- **WHEN** 用户访问分享链接
- **THEN** 直接展示行程内容，无需API

### Requirement: 分享码永久有效
分享码一经生成永久有效，不会失效。

#### Scenario: 分享码长期可用
- **WHEN** 用户保存分享码
- **THEN** 任何时间访问均可展示行程内容

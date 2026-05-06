
## Purpose
合同管理：支持合同的创建、编辑、查看、签署、状态流转、复制签署链接、出行提示等操作。

## Fields
| 字段名             | 中文名         | 类型     | 约束/说明                         |
|------------------|--------------|---------|----------------------------------|
| id               | 合同ID        | int     | 主键，自增                        |
| order_id         | 订单ID        | int     | 必填，关联订单                    |
| itinerary_id     | 行程ID        | int     | 必填，二次确认行程存在             |
| product_id       | 产品ID        | int     | 必填，自动预填                     |
| contract_no      | 合同编号      | string  | 必填，唯一，自动生成               |
| party_a          | 甲方名称      | string  | 必填，客户名称                     |
| party_b          | 乙方名称      | string  | 必填，旅行社名称                   |
| amount           | 合同金额      | number  | 必填，单位：元，精度2位            |
| terms            | 费用条款      | string  | 必填，自动预填，可编辑             |
| travel_notice    | 出行提示      | string  | 可选，支持多行文本                 |
| status           | 状态          | string  | 必填，枚举：pending_sign/signed/revoked |
| sign_url         | 签署链接      | string  | 自动生成，唯一                     |
| created_at       | 创建时间      | string  | 创建时间，ISO8601                  |
| updated_at       | 更新时间      | string  | 更新时间，ISO8601                  |

## Requirements

### Requirement: 新建合同仅显示未关联合同的订单
仅可选择未关联合同的订单进行合同创建。

### Requirement: 选中订单后检查行程存在性
选择订单后，系统 SHALL 检查是否已存在对应行程。

### Requirement: 从产品预填费用条款字段
合同表单中的费用条款字段 SHALL 自动从产品模板预填。

### Requirement: 合同支持存储出行提示字段
合同表单支持填写出行提示，内容可多行。

### Requirement: 合同新增/编辑与状态变更
系统 SHALL 支持合同的新增和编辑，仅 pending_sign 状态下可编辑。合同状态仅包含 pending_sign、signed、revoked，状态流转仅允许合法变更。

#### Scenario: 新增合同
- **WHEN** 用户点击“新建合同”并填写表单后提交
- **THEN** 系统校验必填项，合同编号自动生成，状态为 pending_sign

#### Scenario: 编辑合同
- **WHEN** 合同处于 pending_sign 状态，用户点击“编辑”并修改信息后保存
- **THEN** 系统保存变更，其他状态不可编辑

#### Scenario: 合同状态流转
- **WHEN** 合同签署或撤销等操作发生
- **THEN** 仅允许 pending_sign→signed、pending_sign→revoked 等合法状态变更，后端校验

### Requirement: 合同详情页展示完整字段
详情页应展示合同所有字段内容。

### Requirement: 签署页展示出行提示
签署页应展示出行提示字段内容。

### Requirement: 合同状态枚举精简为三个
合同状态仅包含 pending_sign、signed、revoked。

### Requirement: 合同创建即进入待签署状态
新建合同后状态自动为 pending_sign。

### Requirement: 签署链接创建后即可复制
合同创建后即可复制签署链接。

### Requirement: 合同列表操作统一为“复制链接”
合同列表操作按钮统一为“复制链接”。

### Requirement: 状态标签全中文显示
所有状态标签均显示为中文。

### Requirement: 后端状态跃迁只包含合法状态
后端仅允许合法的状态流转。

### Requirement: 合同详情页编辑按钮无死代码条件
详情页编辑按钮仅在 pending_sign 状态下可见。
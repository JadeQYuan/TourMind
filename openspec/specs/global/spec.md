## Purpose
全局规范：Mock 开发、接口约定、API 错误处理、文件编码、业务字段等全局规范。

### Requirement: API 错误与接口约束
所有 API 错误须统一通过前端 message.error() 提示，不允许静默吞噬。
接口返回结构推荐：
- 成功：{ code: 0, data, message: '' }
- 失败：{ code: 非0, data: null, message: '错误信息' }
所有接口返回均为 UTF-8 编码（无 BOM）。

#### Scenario: API 错误统一提示
- **WHEN** 前端收到后端接口错误响应
- **THEN** 统一调用 message.error() 展示错误信息

#### Scenario: 接口返回结构规范
- **WHEN** 后端接口返回数据
- **THEN** 返回结构包含 code/data/message 字段，且编码为 UTF-8（无 BOM）

### Requirement: Mock 响应函数需防御参数
所有 `mock/` 目录下的 response 函数，在使用 `params.id` 或 `params.token` 之前，SHALL 先检查 `params` 及对应字段是否存在；若不存在，SHALL 立即返回结构化错误响应 `{ code: 400, message: '参数错误' }`，不得抛出未捕获的异常。

#### Scenario: params 未定义返回 400
- **WHEN** vite-plugin-mock 调用 response 函数时 `params` 为 `undefined`
- **THEN** 函数返回 `{ code: 400, message: '参数错误' }`，不抛出 TypeError

#### Scenario: params.id 缺失返回 400
- **WHEN** `params` 是空对象 `{}` 或不含 `id` 字段
- **THEN** 函数返回 `{ code: 400, message: '参数错误' }`，不执行后续查找逻辑

#### Scenario: 参数有效时正常执行
- **WHEN** `params.id` 或 `params.token` 有有效值
- **THEN** 函数按原有逻辑执行，返回正确数据或 404

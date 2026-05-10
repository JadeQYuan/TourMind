## 1. 模型层更新

- [ ] 1.1 backend/app/models/user.py：
  - 将 `is_active: bool` 替换为 `status: str`，默认值为 "enabled"
  - 将 `last_login_at` 重命名为 `last_login`
  - 删除 `must_change_password` 字段
  - 新增 `remark: str | None` 字段，长度 128
  - 更新相关导入

- [ ] 1.2 backend/app/models/__init__.py：检查是否需要更新导出

## 2. Schema 层更新

- [ ] 2.1 backend/app/schemas/user.py：
  - 将 `UserOut` 中的 `is_active` 替换为 `status`
  - 删除 `must_change_password` 字段
  - 将 `last_login_at` 重命名为 `last_login`
  - 在 `UserCreate`、`UserUpdate` 中新增 `remark` 可选字段
  - 更新 `UserRole` 保持现状
  - 更新 `UserUpdate` 中的 `is_active` → `status`

- [ ] 2.2 backend/app/schemas/auth.py：
  - `LoginUserInfo`：删除 `must_change_password` 字段
  - `UserOut`：更新字段名与用户模型一致

## 3. 路由层更新

- [ ] 3.1 backend/app/routers/users.py：
  - 新增单个用户详情 GET 端点 `/users/{user_id}`
  - 更新列表查询参数：`is_active` → `status`（值为 "enabled"/"disabled"）
  - 更新创建用户逻辑：删除 `must_change_password` 相关代码
  - 更新状态变更逻辑：从切换 `is_active` 改为设置 `status`
  - 更新用户更新逻辑：`is_active` → `status`
  - 更新重置密码逻辑：删除 `must_change_password` 设置

- [ ] 3.2 backend/app/routers/auth.py：
  - 更新登录逻辑：删除 `must_change_password` 相关处理
  - 更新 `change-password` 端点：删除 `must_change_password` 设置
  - 更新 `get_me` 端点：返回数据与新 Schema 一致

## 4. 依赖检查

- [ ] 4.1 backend/app/core/deps.py：检查是否有 `must_change_password` 相关依赖

## 5. 数据库迁移

- [ ] 5.1 生成 Alembic 迁移脚本：处理字段重命名、删除、新增

## 6. 验证测试

- [ ] 6.1 启动后端服务，验证 API 正常
- [ ] 6.2 检查数据库表结构正确

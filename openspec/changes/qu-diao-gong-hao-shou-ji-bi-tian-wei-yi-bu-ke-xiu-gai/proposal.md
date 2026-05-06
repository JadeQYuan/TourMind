## Why

当前系统用户表包含“工号”字段，但实际业务中并未使用，且存在冗余。为简化用户管理流程，提升数据一致性，决定去除工号。同时，手机号作为用户唯一标识，需设为必填、唯一且不可修改，以满足实际运营需求并防止重复注册。

## What Changes

- **BREAKING** 移除用户表中的“工号”字段及相关前端展示、输入项
- 用户手机号字段设为必填项，注册/编辑时必须填写
- 用户手机号字段全局唯一，禁止重复
- 用户手机号一经注册后不可修改，前端禁用编辑，后端校验

## Capabilities

### New Capabilities
- `user-mobile-immutable`: 用户手机号不可修改，注册后锁定

### Modified Capabilities
- `user`: 移除工号字段，手机号必填、唯一且不可修改

## Impact

- 涉及后端 models/user.py、schemas/user.py、routers/users.py
- 涉及前端 src/views/user/、src/api/user.ts、src/components/user/
- 涉及数据库迁移脚本
- 影响用户注册、编辑、展示、登录等相关功能（登录仅支持手机号）

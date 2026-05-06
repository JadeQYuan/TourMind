## 1. 后端实现

- [ ] 1.1 修改 backend/app/routers/users.py，用户列表接口根据当前用户角色过滤可见用户
- [ ] 1.2 修改 backend/app/routers/users.py，新增用户接口根据当前用户角色限制可选角色
- [ ] 1.3 增加后端单元测试，覆盖不同角色下的用户列表和新增用户权限

## 2. 前端实现

- [ ] 2.1 修改 frontend/src/views/user/UserListView.vue，用户列表根据当前用户角色动态展示
- [ ] 2.2 修改 frontend/src/views/user/UserListView.vue，新增用户表单可选角色根据当前用户角色动态调整
- [ ] 2.3 修改 frontend/src/api/user.ts，适配后端接口变更
- [ ] 2.4 增加前端测试，验证不同角色下的用户列表和新增用户权限

## 3. 联调与回归

- [ ] 3.1 手动测试系统管理员和管理员账号下的用户列表和新增用户功能
- [ ] 3.2 回归测试相关权限边界场景

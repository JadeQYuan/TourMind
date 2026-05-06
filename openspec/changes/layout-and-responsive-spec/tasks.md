## 1. 全局布局与组件规范

- [ ] 1.1 制定并发布统一页面主结构、侧边栏、顶部导航布局规范文档（docs/ 或 frontend/README.md）
- [ ] 1.2 在 frontend/src/components/ 新增或重构 Layout 相关通用组件，封装主结构（Layout/Sider/Header/Content）
- [ ] 1.3 统一 Drawer、操作栏等通用组件布局，调整宽度与 sticky footer 实现

## 2. 响应式逻辑与视图切换

- [ ] 2.1 在 frontend/src/composables/ 新增 useResponsive.ts，封装 768px 断点与 Table/Card 视图切换逻辑
- [ ] 2.2 所有列表页（frontend/src/views/*/）接入 useResponsive，实现 Table/Card 双视图自动切换
- [ ] 2.3 现有页面逐步迁移，优先订单、行程、合同、用户等核心模块

## 3. 测试与文档

- [ ] 3.1 编写/更新前端单元测试，覆盖布局组件与响应式逻辑（frontend/tests/）
- [ ] 3.2 补充/更新开发文档，说明新规范与迁移指引（docs/ 或 frontend/README.md）

## 4. 后端（如有接口变更）

- [ ] 4.1 如涉及布局相关 API 变更，更新 backend/app/routers/ 及相关 schema、model
- [ ] 4.2 补充后端接口文档，说明变更内容

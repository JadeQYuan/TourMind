## Why

当前系统的页面布局和响应式逻辑缺乏统一的规范，导致不同业务模块在桌面端与移动端的体验不一致，维护成本高。随着移动端访问比例提升，亟需明确布局和响应式设计标准，提升整体用户体验和开发一致性。

## What Changes

- 制定全局页面布局规范，包括主内容区、侧边栏、顶部导航等结构约定
- 明确桌面端与移动端的响应式断点、布局切换逻辑
- 规范各业务模块列表页的 Table/Card 双视图切换行为
- 统一 Drawer、Form、操作栏等通用组件的布局与交互规范
- **BREAKING**：部分现有页面布局将按新规范调整，可能影响前端样式和部分交互

## Capabilities

### New Capabilities
- `layout-spec`: 统一页面布局规范，定义主内容区、侧边栏、顶部导航等结构及适配要求
- `responsive-logic`: 响应式断点、布局切换、Table/Card 双视图等逻辑规范

### Modified Capabilities

（无）

## Impact

- frontend/src/views/ 及各业务模块页面
- frontend/src/components/ 通用组件
- frontend/src/api/ 相关接口（如有布局相关变更）
- 影响所有前端开发人员，需按新规范调整和开发页面
- 需补充相关文档，便于后续维护和协作

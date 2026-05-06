## ADDED Requirements

### Requirement: 响应式布局设备划分
系统 SHALL 将终端设备划分为 PC、PAD、Mobile 三类，分别适配不同布局和交互。

#### Scenario: 设备类型识别
- **WHEN** 页面宽度 ≥ 1200px
- **THEN** 识别为 PC 端
- **WHEN** 768px ≤ 页面宽度 < 1200px
- **THEN** 识别为 PAD 端
- **WHEN** 页面宽度 < 768px
- **THEN** 识别为 Mobile 端

### Requirement: 菜单栏响应式显示
系统 SHALL 根据设备类型自动控制菜单栏（侧边栏）显示/隐藏：
- PC 端菜单栏默认显示
- PAD 端菜单栏默认隐藏，可手动展开
- Mobile 端菜单栏默认隐藏，仅通过按钮弹出

#### Scenario: 菜单栏显示逻辑
- **WHEN** 设备为 PC
- **THEN** 菜单栏默认显示
- **WHEN** 设备为 PAD
- **THEN** 菜单栏默认隐藏，可手动展开
- **WHEN** 设备为 Mobile
- **THEN** 菜单栏默认隐藏，仅通过按钮弹出

### Requirement: 查询表单与列表响应式布局
系统 SHALL 在 Mobile 端将查询表单单独显示，表单一行仅显示一个字段，列表以卡片形式展示。

#### Scenario: 查询表单与列表布局
- **WHEN** 设备为 Mobile
- **THEN** 查询表单单独显示，表单一行一个字段，列表以卡片形式展示
- **WHEN** 设备为 PAD 或 PC
- **THEN** 查询表单与列表可并排显示，表单可多字段一行，列表为 Table 视图


### Requirement: 统一页面主结构
系统 SHALL 采用统一的主内容区、侧边栏、顶部导航布局，所有业务模块页面均需遵循该结构。

#### Scenario: 页面主结构渲染
- **WHEN** 用户访问任一业务模块页面
- **THEN** 页面应包含主内容区、侧边栏、顶部导航，结构一致

### Requirement: 统一布局组件选型
所有页面 SHALL 使用 Ant Design Vue 官方推荐的 Layout、Sider、Header、Content 组件实现主结构。

#### Scenario: 组件一致性
- **WHEN** 新页面开发或旧页面迁移
- **THEN** 主结构组件选型与规范一致，无自定义实现

### Requirement: 表单使用抽屉组件
所有详情/编辑 Drawer SHALL 采用统一宽度（桌面端 480px，移动端全屏），底部操作栏使用 sticky 定位。

#### Scenario: Drawer 布局一致性
- **WHEN** 打开详情/编辑 Drawer
- **THEN** 宽度与操作栏布局符合规范

### Requirement: 响应式断点与视图切换
系统 SHALL 统一采用 768px 作为桌面端与移动端的响应式断点，断点切换时自动切换布局和视图。

#### Scenario: 断点切换行为
- **WHEN** 页面宽度小于 768px
- **THEN** 自动切换为移动端布局（Card 视图）
- **WHEN** 页面宽度大于等于 768px
- **THEN** 自动切换为桌面端布局（Table 视图）

### Requirement: Table/Card 双视图规范
所有列表页 SHALL 实现 Table（桌面端）与 Card（移动端）双视图，交互一致。

#### Scenario: 列表页视图切换
- **WHEN** 用户在不同终端访问列表页
- **THEN** 视图自动切换且功能一致

### Requirement: 响应式逻辑全局复用
响应式断点与视图切换逻辑 SHALL 封装为全局 composable，供各页面复用，避免重复实现。

#### Scenario: 复用响应式逻辑
- **WHEN** 新页面开发或旧页面迁移
- **THEN** 直接复用全局 composable 实现断点与视图切换

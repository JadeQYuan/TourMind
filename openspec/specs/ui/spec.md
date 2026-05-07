## Purpose
整理所有与前端布局、交互、UI 组件通用规范相关的需求，供各业务模块复用，覆盖 Mobile、PAD、PC 三端响应式。

## Requirements

### Requirement: 统一 useBreakpoint 响应式断点
系统 SHALL 提供 `useBreakpoint` composable（位于 `src/composables/useBreakpoint.ts`），导出以下响应式变量：
- `isMobile`：视口宽度 < 768px
- `isPad`：768px ≤ 视口宽度 < 1200px
- `isPC`：视口宽度 ≥ 1200px
所有视图、组件均应基于上述断点判断布局与交互。

#### Scenario: 响应式变量正确反映断点
- **WHEN** 视口宽度缩小至 767px
- **THEN** `isMobile` 为 true，`isPad` 和 `isPC` 为 false
- **WHEN** 视口宽度调整至 900px
- **THEN** `isPad` 为 true，其余为 false
- **WHEN** 视口宽度调整至 1200px 及以上
- **THEN** `isPC` 为 true，其余为 false

#### Scenario: 不重复注册 resize 事件
- **WHEN** 任意视图/组件使用 useBreakpoint
- **THEN** 仅全局注册一次 resize 监听，避免重复

### Requirement: 列表页三端渲染规范
所有列表页（订单、产品、行程、合同、供应商、账单、账户、用户、审计日志）应根据断点渲染不同布局：
- Mobile（<768px）：以 `<a-card>` 卡片列表方式渲染数据，表格不显示
- PAD（768px~1199px）：以紧凑型 `<a-table>` 表格渲染，支持横向滚动，卡片可选，默认隐藏侧边菜单，仅顶部菜单可见
- PC（≥1200px）：以标准 `<a-table>` 表格渲染，完整列宽，支持横向滚动，左侧菜单与列表同时显示

#### Scenario: Mobile 隐藏表格
- **WHEN** 用户在 isMobile 视口访问任意列表页
- **THEN** `<a-table>` 组件不渲染，显示卡片列表

#### Scenario: PAD 默认隐藏菜单
- **WHEN** 用户在 isPad 视口访问列表页
- **THEN** 侧边菜单默认隐藏，仅顶部菜单可见，主区域显示表格

#### Scenario: PC 显示菜单加列表
- **WHEN** 用户在 isPC 视口访问列表页
- **THEN** 左侧菜单与主区域列表同时显示，菜单始终可见

#### Scenario: PAD/PC 显示表格
- **WHEN** 用户在 isPad 或 isPC 视口访问列表页
- **THEN** 显示 `<a-table>` 表格，Mobile 卡片不渲染

### Requirement: 卡片/表格分页同步
所有端的卡片/表格视图 SHALL 共用同一分页组件，分页状态保持同步。

#### Scenario: 各端分页一致
- **WHEN** 用户在任意端滚动至列表底部
- **THEN** 显示与其它端一致的 `<a-pagination>` 分页控件

### Requirement: 列表筛选三端交互
- Mobile：筛选条件以顶部“筛选”按钮+底部 Drawer（placement="bottom"，高度约 60vh）展示
- PAD/PC：筛选条件以内联表单展示，始终可见

#### Scenario: Mobile 隐藏内联筛选表单
- **WHEN** 用户在 isMobile 端访问含筛选条件的列表页
- **THEN** 仅显示“筛选”按钮，点击后弹出 Drawer

#### Scenario: PAD/PC 内联筛选
- **WHEN** 用户在 isPad 或 isPC 端访问列表页
- **THEN** 筛选表单始终内联展示

#### Scenario: 筛选抽屉需确认后生效
- **WHEN** 用户在 Mobile 端 Drawer 中修改筛选字段
- **THEN** 列表数据不立即变化，等待点击“确认”按钮

#### Scenario: 筛选按钮显示已选数量
- **WHEN** 用户已应用至少一个非默认筛选条件
- **THEN** “筛选”按钮上显示对应数字徽标

### Requirement: 新建/编辑表单三端抽屉规范
所有新建/编辑表单建议采用 Drawer（抽屉）模式：
- Mobile：全屏抽屉（宽度 100%）
- PAD：宽度 600px
- PC：宽度 480px
如需特殊页面跳转或弹窗实现，须在模块规范中单独说明。

#### Scenario: 默认以抽屉编辑
- **WHEN** 用户点击“编辑”按钮
- **THEN** 默认以 Drawer 形式打开编辑表单，宽度随端自适应

### Requirement: 表单三端布局规范
- Mobile：所有字段单列全宽（span=24）
- PAD/PC：可多列网格布局

#### Scenario: Mobile 表单全宽单列
- **WHEN** 用户在 isMobile 端打开新建/编辑 Drawer
- **THEN** 表单所有字段单列全宽

#### Scenario: PAD/PC 表单多列
- **WHEN** 用户在 isPad 或 isPC 端打开新建/编辑 Drawer
- **THEN** 表单可多列网格布局

### Requirement: 抽屉表单底部操作栏固定
所有端新建/编辑 Drawer 的操作按钮（取消/保存）SHALL 使用 `<template #footer>` 插槽固定在抽屉底部，不随内容滚动。

#### Scenario: 抽屉表单按钮固定底部
- **WHEN** 用户在任意 Drawer 表单中查看内容超过视口高度时
- **THEN** 取消/保存按钮始终固定在 Drawer 底部，不随内容滚动

#### Scenario: 独立路由页面按钮正常显示
- **WHEN** 用户通过独立路由访问表单页面
- **THEN** 按钮正常显示在表单内容底部，行为由 `showFooter` prop 控制

### Requirement: 表格横向滚动三端规范
- PAD/PC 端 `<a-table>` SHALL 设置 `:scroll="{ x: N }"`，N 为所有列 width 之和，使表格可横向滚动。

#### Scenario: PAD/PC 表格横向滚动
- **WHEN** 用户在 isPad 或 isPC 端打开列表页且窗口宽度小于表格 scrollX
- **THEN** 表格下方出现横向滚动条，列内容不被压缩

### Requirement: 操作列横向滚动时固定右侧
含操作列（`key: 'action'`）的 PAD/PC 端表格 SHALL 为该列设置 `fixed: 'right'`。

#### Scenario: 操作列横向滚动时固定
- **WHEN** 用户在 isPad 或 isPC 端横向滚动宽表格
- **THEN** 「操作」列始终显示在表格最右侧，不随滚动消失

### Requirement: 启用横向滚动的表格所有列需显式宽度
所有 PAD/PC 端启用 `:scroll="{ x: N }"` 的表格，其 columns 定义中每列 SHALL 有显式的 `width` 值（整数，单位 px）。

#### Scenario: 所有列均有宽度
- **WHEN** PAD/PC 端开启横向滚动的表格渲染
- **THEN** 所有列均有明确的 width 值，不留空

## 1. 行程管理 — 列表与状态

- [x] 1.1 在 `frontend/src/views/itinerary/` 列表组件（桌面端 Table 列定义 + 移动端 Card 模板）中，将目的地字段单元格的状态标签移除，仅保留目的地文本
- [x] 1.2 在行程列表操作栏中，删除原"撤销完成"按钮（`completed` 状态显示，回退到 `in_progress`）及其处理函数；新增"撤销"按钮仅对 `not_started` 状态显示，点击弹出确认对话框，确认后调用 `PATCH /itineraries/{id}/status` 将状态置为 `cancelled`（桌面端 Table 操作列 + 移动端 Card 操作区两处）
- [x] 1.3 在 `backend/app/routers/itineraries.py`（或等效文件）中，在 `VALID_TRANSITIONS` 中移除 `completed → in_progress` 条目，新增 `not_started → cancelled` 条目

## 2. 行程管理 — 表单

- [x] 2.1 在 `frontend/src/views/itinerary/` 行程表单组件中，将每日行程明细区块的展开状态默认值改为全部展开（新建和编辑模式均生效）
- [x] 2.2 在行程新增/编辑表单中，删除表单底部所有提示语文本（静态说明文字、`<a-alert>` 或类似提示组件）

## 3. 合同管理 — 列表操作

- [x] 3.1 在 `frontend/src/views/contract/` 列表组件（桌面端 Table 操作列 + 移动端 Card 操作区）中，将"复制链接"按钮文案改为"分享"
- [x] 3.2 在同一列表组件的 `pending_sign` 操作区新增"编辑"按钮，点击后跳转至合同编辑页 `/contracts/:id/edit`；`signed` 和 `revoked` 状态不显示该按钮

## 4. 合同管理 — 表单
- [x] 4.1 在 `frontend/src/views/contract/` 合同新增/编辑表单组件中，删除表单底部所有提示语文本（静态说明文字、`<a-alert>` 或类似提示组件，包含创建成功后的分享引导 Modal)

# Design: 通用多文件上传组件

## 组件结构
- 基于 Ant Design Vue `<a-upload>`，`multiple` 模式，`max-count=20`，`accept="image/*"`，`list-type="picture-card"`
- Props：
  - `modelValue: string[]`（图片URL数组，v-model）
  - `maxCount?: number`（默认20）
  - `maxSizeMB?: number`（默认10）
- Emits：
  - `update:modelValue`（图片URL数组变化时触发）
- 支持移动端适配（参考 global/spec.md 响应式规范）、图片预览、删除

## 页面集成
- 合同签署等页面直接引入该组件，移除证件类型、正反面等字段，仅保留图片上传入口
- 上传成功后将图片URL加入数组，删除时移除
- 组件样式与表单/Drawer/卡片等全局 UI 规范一致

## 后端接口
- 复用 `/api/v1/files/upload`，参数增加 `scene` 区分业务，后端按业务场景存储

## 兼容性与扩展
- 组件可复用于其他需要多图片上传的场景
- 后续如需支持视频、文档等类型，可通过 `accept` 参数扩展

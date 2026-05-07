# ImageMultiUpload 组件文档

## 组件说明
通用多图片上传组件，基于 Ant Design Vue `<a-upload>` 封装，支持移动端和桌面端，图片预览、删除。

## Props
- `modelValue: string[]`  图片 URL 数组，v-model 绑定
- `maxCount: number`      最多上传图片数量，默认 20
- `maxSizeMB: number`     单张图片最大体积（MB），默认 10
- `accept: string`        接受的文件类型，默认 'image/*'
- `uploadUrl: string`     上传接口地址，默认 '/api/v1/files/upload'
- `data: object`          额外上传参数，如 `{ scene: 'contract' }`

## 用法示例
```vue
<ImageMultiUpload v-model="images" :max-count="20" :max-size-m-b="10" :data="{ scene: 'contract' }" />
```

## 业务集成建议
- 合同签署、产品、行程等业务场景均可直接复用
- 后端接口需支持 `scene` 参数，按业务分目录存储

## 注意事项
- 仅支持图片类型（jpg/png/webp）
- 单张图片最大 10MB，最多 20 张
- 支持移动端自适应

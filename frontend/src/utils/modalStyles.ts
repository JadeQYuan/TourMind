/** 全高度弹窗样式 — 应用于 a-modal 的 :styles 和 :style 属性 */
export const fullHeightModalStyles = {
  content: {
    height: '100dvh',
    display: 'flex',
    flexDirection: 'column' as const,
    borderRadius: '0',
    padding: '0',
  },
  header: {
    padding: '16px 24px',
    borderBottom: '1px solid #f0f0f0',
    flexShrink: 0,
    marginBottom: '0',
  },
  body: {
    flex: 1,
    overflow: 'auto',
    padding: '24px',
    minHeight: 0,
  },
  footer: {
    borderTop: '1px solid #f0f0f0',
    padding: '12px 24px',
    margin: '0',
    flexShrink: 0,
  },
}

export const fullHeightModalStyle = {
  marginBottom: '0',
  paddingBottom: '0',
}

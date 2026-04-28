import type { MockMethod } from 'vite-plugin-mock'
import { ok, MOCK_USERS } from './_data'

const ACTIONS = [
  '用户登录', '用户登出', '创建订单', '修改订单', '删除订单',
  '创建行程', '修改行程', '创建合同', '签署合同',
  '创建账单', '修改账单', '创建用户', '修改用户', '重置密码',
  '修改产品', '删除产品', '添加供应商', '修改供应商',
]

const RESOURCES = [
  'order:ORD-20260315-001', 'order:ORD-20260410-002', 'itinerary:1',
  'contract:CON-20260301-001', 'bill:1', 'bill:2', 'user:3', 'user:4',
  'product:1', 'product:2', 'supplier:1', 'auth',
]

const IPS = ['192.168.1.10', '192.168.1.15', '10.0.0.5', '10.0.0.12', '172.16.0.1']

function randomItem<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

// 生成200条审计日志
const BASE_LOGS = Array.from({ length: 200 }, (_, i) => {
  const user = MOCK_USERS[i % MOCK_USERS.length]
  const d = new Date('2026-04-17T18:00:00')
  d.setMinutes(d.getMinutes() - i * 37)
  return {
    id: i + 1,
    user_id: user.id,
    user_name: user.full_name,
    action: randomItem(ACTIONS),
    resource: randomItem(RESOURCES),
    ip: randomItem(IPS),
    result: i % 12 === 0 ? 'failure' : 'success',
    detail: i % 12 === 0 ? '权限不足或参数错误' : null,
    created_at: d.toISOString(),
  }
})

let logs = [...BASE_LOGS]

export default [
  {
    url: '/api/v1/audit-logs',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...logs]
      if (query.keyword) {
        list = list.filter(l =>
          l.user_name.includes(query.keyword) ||
          l.action.includes(query.keyword) ||
          l.resource.includes(query.keyword) ||
          l.ip.includes(query.keyword),
        )
      }
      if (query.result) list = list.filter(l => l.result === query.result)
      if (query.user_id) list = list.filter(l => l.user_id === Number(query.user_id))
      const page = Number(query.page) || 1
      const pageSize = Number(query.page_size) || 20
      const total = list.length
      const items = list.slice((page - 1) * pageSize, page * pageSize)
      return ok({ items, total, page, page_size: pageSize })
    },
  },
] as MockMethod[]

import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_USERS } from './_data'

let users = [...MOCK_USERS]
let nextId = 10

function genPassword() {
  const upper = 'ABCDEFGHJKMNPQRSTUVWXYZ'
  const lower = 'abcdefghjkmnpqrstuvwxyz'
  const digits = '23456789'
  const special = '!@#$%^&*'
  const all = upper + lower + digits + special
  const parts = [
    upper[Math.floor(Math.random() * upper.length)],
    lower[Math.floor(Math.random() * lower.length)],
    digits[Math.floor(Math.random() * digits.length)],
    special[Math.floor(Math.random() * special.length)],
    ...Array.from({ length: 8 }, () => all[Math.floor(Math.random() * all.length)]),
  ]
  return parts.sort(() => Math.random() - 0.5).join('')
}

export default [
  {
    url: '/api/v1/users',
    method: 'get',
    response: ({ query, headers }: any) => {
      const uidMatch = headers?.authorization?.match(/mock-jwt-token-uid-(\d+)/)
      const callerId = uidMatch ? Number(uidMatch[1]) : null
      const caller = callerId ? users.find(u => u.id === callerId) : null
      let list = [...users]
      if (!caller || caller.role !== 'system_admin') {
        list = list.filter(u => u.role !== 'system_admin')
      }
      if (query.role) list = list.filter(u => u.role === query.role)
      if (query.keyword) list = list.filter(u =>
        u.full_name.includes(query.keyword) ||
        (u.phone && u.phone.includes(query.keyword)) ||
        (u.employee_id && u.employee_id.includes(query.keyword))
      )
      if (query.is_active !== undefined) list = list.filter(u => String(u.is_active) === query.is_active)
      return paged(list)
    },
  },
  {
    url: '/api/v1/users/:id',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const item = users.find(u => u.id === Number(params.id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  {
    url: '/api/v1/users',
    method: 'post',
    response: ({ body }: any) => {
      const password = genPassword()
      const item = {
        ...body,
        id: nextId++,
        username: body.employee_id || body.phone || `user${nextId}`,
        full_name: body.full_name,
        is_active: true,
        must_change_password: true,
        last_login_at: null,
        created_at: new Date().toISOString(),
      }
      users.push(item)
      return ok({ ...item, generated_password: password })
    },
  },
  {
    url: '/api/v1/users/:id',
    method: 'put',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = users.findIndex(u => u.id === Number(params.id))
      if (idx !== -1) users[idx] = { ...users[idx], ...body }
      return ok(users[idx])
    },
  },
  {
    url: '/api/v1/users/:id/status',
    method: 'patch',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = users.findIndex(u => u.id === Number(params.id))
      if (idx !== -1) users[idx] = { ...users[idx], is_active: !users[idx].is_active }
      return ok(users[idx])
    },
  },
  {
    url: '/api/v1/users/:id/reset-password',
    method: 'post',
    response: () => ok({ generated_password: genPassword() }),
  },
] as MockMethod[]

import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_ACCOUNTS } from './_data'

let accounts = [...MOCK_ACCOUNTS]
let nextId = 20

export default [
  {
    url: '/api/v1/accounts',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...accounts]
      if (query.keyword) list = list.filter(a => a.name.includes(query.keyword))
      if (query.account_type) list = list.filter(a => a.account_type === query.account_type)
      if (query.user_id) list = list.filter(a => a.user_id === Number(query.user_id))
      if (query.is_active !== undefined) list = list.filter(a => String(a.is_active) === query.is_active)
      return paged(list)
    },
  },
  {
    url: '/api/v1/accounts/:id',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const item = accounts.find(a => a.id === Number(params.id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  {
    url: '/api/v1/accounts',
    method: 'post',
    response: ({ body }: any) => {
      const item = { ...body, id: nextId++, is_active: true, created_at: new Date().toISOString() }
      accounts.push(item)
      return ok(item)
    },
  },
  {
    url: '/api/v1/accounts/:id',
    method: 'put',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = accounts.findIndex(a => a.id === Number(params.id))
      if (idx !== -1) accounts[idx] = { ...accounts[idx], ...body }
      return ok(accounts[idx])
    },
  },
  {
    url: '/api/v1/accounts/:id',
    method: 'delete',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      accounts = accounts.filter(a => a.id !== Number(params.id))
      return ok(null)
    },
  },
] as MockMethod[]

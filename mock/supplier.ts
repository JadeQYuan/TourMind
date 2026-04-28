import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_SUPPLIERS } from './_data'

let suppliers = [...MOCK_SUPPLIERS]
let nextId = 20

export default [
  {
    url: '/api/v1/suppliers',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...suppliers]
      if (query.keyword) list = list.filter(s => s.name.includes(query.keyword))
      if (query.is_active !== undefined) list = list.filter(s => String(s.is_active) === query.is_active)
      return paged(list)
    },
  },
  {
    url: '/api/v1/suppliers/:id',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const item = suppliers.find(s => s.id === Number(params.id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  {
    url: '/api/v1/suppliers',
    method: 'post',
    response: ({ body }: any) => {
      const item = { ...body, id: nextId++, is_active: true, created_at: new Date().toISOString() }
      suppliers.push(item)
      return ok(item)
    },
  },
  {
    url: '/api/v1/suppliers/:id',
    method: 'put',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = suppliers.findIndex(s => s.id === Number(params.id))
      if (idx !== -1) suppliers[idx] = { ...suppliers[idx], ...body }
      return ok(suppliers[idx])
    },
  },
  {
    url: '/api/v1/suppliers/:id',
    method: 'delete',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      suppliers = suppliers.filter(s => s.id !== Number(params.id))
      return ok(null)
    },
  },
] as MockMethod[]

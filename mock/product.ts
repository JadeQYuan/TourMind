import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_PRODUCTS } from './_data'

let products = [...MOCK_PRODUCTS]
let nextId = 10

export default [
  {
    url: '/api/v1/products/:id/copy',
    method: 'post',
    response: ({ query: params }: any) => {
      const id = params?.id
      if (!id) return { code: 400, message: '参数错误' }
      const src = products.find(p => p.id === Number(id))
      if (!src) return { code: 404, message: '不存在' }
      const copy = { ...src, id: nextId++, name: src.name + '（副本）', created_at: new Date().toISOString() }
      products.push(copy)
      return ok(copy)
    },
  },
  {
    url: '/api/v1/products/:id',
    method: 'get',
    response: ({ query: params }: any) => {
      const id = params?.id
      if (!id) return { code: 400, message: '参数错误' }
      const item = products.find(p => p.id === Number(id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  {
    url: '/api/v1/products/:id',
    method: 'put',
    response: ({ query: params, body }: any) => {
      const id = params?.id
      if (!id) return { code: 400, message: '参数错误' }
      const idx = products.findIndex(p => p.id === Number(id))
      if (idx === -1) return { code: 404, message: '不存在' }
      products[idx] = { ...products[idx], ...body }
      return ok(products[idx])
    },
  },
  {
    url: '/api/v1/products/:id',
    method: 'delete',
    response: ({ query: params }: any) => {
      const id = params?.id
      if (!id) return { code: 400, message: '参数错误' }
      products = products.filter(p => p.id !== Number(id))
      return ok(null)
    },
  },
  {
    url: '/api/v1/products',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...products]
      if (query.keyword) list = list.filter(p => p.name.includes(query.keyword) || (p.destination && p.destination.includes(query.keyword)))
      if (query.status) list = list.filter(p => p.status === query.status)
      const page = Number(query.page ?? 1)
      const pageSize = Number(query.page_size ?? 10)
      const total = list.length
      const items = list.slice((page - 1) * pageSize, page * pageSize)
      return paged(items, total)
    },
  },
  {
    url: '/api/v1/products',
    method: 'post',
    response: ({ body }: any) => {
      const item = { ...body, id: nextId++, status: body.status ?? 'active', created_at: new Date().toISOString() }
      products.push(item)
      return ok(item)
    },
  },
] as MockMethod[]

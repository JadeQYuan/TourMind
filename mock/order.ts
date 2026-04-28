import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_ORDERS } from './_data'

let orders = [...MOCK_ORDERS]
let nextId = 10

function genOrderNo() {
  const d = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  return `ORD-${d}-${String(nextId).padStart(3, '0')}`
}

export default [
  {
    url: '/api/v1/orders',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...orders]
      if (query.status) list = list.filter(o => o.status === query.status)
      if (query.keyword) list = list.filter(o =>
        o.customer_name.includes(query.keyword) ||
        o.customer_phone.includes(query.keyword) ||
        o.order_no.includes(query.keyword)
      )
      if (query.product_id) list = list.filter(o => o.product_id === Number(query.product_id))
      if (query.supplier_id) list = list.filter(o => o.supplier_id === Number(query.supplier_id))
      return paged(list)
    },
  },
  {
    url: '/api/v1/orders/:id',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const item = orders.find(o => o.id === Number(params.id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  {
    url: '/api/v1/orders',
    method: 'post',
    response: ({ body }: any) => {
      const item = {
        ...body,
        id: nextId++,
        order_no: genOrderNo(),
        profit: body.price && body.cost ? body.price - body.cost : null,
        status: 'pending_deposit',
        created_at: new Date().toISOString(),
      }
      orders.push(item)
      return ok(item)
    },
  },
  {
    url: '/api/v1/orders/:id',
    method: 'put',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = orders.findIndex(o => o.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      const updated = {
        ...orders[idx],
        ...body,
        profit: (body.price ?? orders[idx].price) && (body.cost ?? orders[idx].cost)
          ? (body.price ?? orders[idx].price) - (body.cost ?? orders[idx].cost)
          : null,
      }
      orders[idx] = updated
      return ok(orders[idx])
    },
  },
  {
    url: '/api/v1/orders/:id/status',
    method: 'patch',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = orders.findIndex(o => o.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      orders[idx] = { ...orders[idx], status: body.status }
      return ok(orders[idx])
    },
  },
] as MockMethod[]

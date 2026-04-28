import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_ITINERARIES, MOCK_ORDERS } from './_data'

let itineraries = [...MOCK_ITINERARIES]
let nextId = 10

// 行程内供应商子订单（用于行程详情页的服务安排）
let serviceOrders: any[] = []
let serviceOrderNextId = 100

function genShareToken(prefix: string) {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`
}

export default [
  // Public: get itinerary by share token (no auth)
  {
    url: '/api/v1/public/itineraries/:token',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.token) return { code: 400, message: '参数错误' }
      const item = itineraries.find(i => i.share_token === params.token)
      return item ? ok(item) : { code: 404, message: '分享链接无效或已撤销' }
    },
  },
  // Status update
  {
    url: '/api/v1/itineraries/:id/status',
    method: 'patch',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = itineraries.findIndex(i => i.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      itineraries[idx] = { ...itineraries[idx], status: body.status }
      return ok(itineraries[idx])
    },
  },
  // Copy
  {
    url: '/api/v1/itineraries/:id/copy',
    method: 'post',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const src = itineraries.find(i => i.id === Number(params.id))
      if (!src) return { code: 404, message: '不存在' }
      const copy = { ...src, id: nextId++, status: 'not_started', share_token: genShareToken('itin'), created_at: new Date().toISOString() }
      itineraries.push(copy)
      return ok(copy)
    },
  },
  // List service orders for itinerary
  {
    url: '/api/v1/itineraries/:id/orders',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const list = serviceOrders.filter(o => o.itinerary_id === Number(params.id))
      return ok(list)
    },
  },
  // Create service order
  {
    url: '/api/v1/itineraries/:id/orders',
    method: 'post',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const order = { ...body, id: serviceOrderNextId++, itinerary_id: Number(params.id), status: body.status ?? 'pending', created_at: new Date().toISOString() }
      serviceOrders.push(order)
      return ok(order)
    },
  },
  // Update service order
  {
    url: '/api/v1/itineraries/:id/orders/:orderId',
    method: 'put',
    response: ({ query: params, body }: any) => {
      if (!params?.id || !params?.orderId) return { code: 400, message: '参数错误' }
      const idx = serviceOrders.findIndex(o => o.id === Number(params.orderId) && o.itinerary_id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      serviceOrders[idx] = { ...serviceOrders[idx], ...body }
      return ok(serviceOrders[idx])
    },
  },
  // Delete service order
  {
    url: '/api/v1/itineraries/:id/orders/:orderId',
    method: 'delete',
    response: ({ query: params }: any) => {
      if (!params?.id || !params?.orderId) return { code: 400, message: '参数错误' }
      serviceOrders = serviceOrders.filter(o => !(o.id === Number(params.orderId) && o.itinerary_id === Number(params.id)))
      return ok(null)
    },
  },
  // Get by id
  {
    url: '/api/v1/itineraries/:id',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const item = itineraries.find(i => i.id === Number(params.id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  // Update
  {
    url: '/api/v1/itineraries/:id',
    method: 'put',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = itineraries.findIndex(i => i.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      itineraries[idx] = { ...itineraries[idx], ...body }
      return ok(itineraries[idx])
    },
  },
  // Delete
  {
    url: '/api/v1/itineraries/:id',
    method: 'delete',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      itineraries = itineraries.filter(i => i.id !== Number(params.id))
      return ok(null)
    },
  },
  // List
  {
    url: '/api/v1/itineraries',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...itineraries]
      if (query.status) list = list.filter(i => i.status === query.status)
      if (query.keyword) list = list.filter(i =>
        i.customer_name.includes(query.keyword) ||
        (i.customer_phone ?? '').includes(query.keyword) ||
        (i.order_no ?? '').includes(query.keyword)
      )
      if (query.customer_order_id) list = list.filter(i => i.customer_order_id === Number(query.customer_order_id))
      return paged(list)
    },
  },
  // Create
  {
    url: '/api/v1/itineraries',
    method: 'post',
    response: ({ body }: any) => {
      const order = MOCK_ORDERS.find(o => o.id === (body.customer_order_id ?? body.order_id))
      const item = {
        ...body,
        id: nextId++,
        order_no: order?.order_no ?? '',
        product_name: order?.product_name ?? '',
        customer_name: order?.customer_name ?? '',
        customer_phone: order?.customer_phone ?? '',
        status: 'not_started',
        share_token: genShareToken('itin'),
        created_at: new Date().toISOString(),
      }
      itineraries.push(item)
      return ok(item)
    },
  },
] as MockMethod[]

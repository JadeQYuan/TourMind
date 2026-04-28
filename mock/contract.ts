import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_CONTRACTS, MOCK_ORDERS } from './_data'

let contracts = [...MOCK_CONTRACTS]
let nextId = 10

function genContractNo() {
  const d = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  return `CT-${d}-${String(nextId).padStart(3, '0')}`
}

function genShareToken(prefix: string) {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`
}

export default [
  // Public: get contract by share token
  {
    url: '/api/v1/public/contracts/:token',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.token) return { code: 400, message: '参数错误' }
      const item = contracts.find(c => c.share_token === params.token && c.status === 'pending_sign')
      return item ? ok(item) : { code: 404, message: '签署链接无效或已过期' }
    },
  },
  // Public: verify phone
  {
    url: '/api/v1/public/contracts/:token/verify-phone',
    method: 'post',
    response: ({ query: params, body }: any) => {
      if (!params?.token) return { code: 400, message: '参数错误' }
      const item = contracts.find(c => c.share_token === params.token)
      if (!item) return { code: 404, message: '链接无效' }
      if (item.customer_phone !== body.phone) return { code: 400, message: '手机号与预留信息不符' }
      return ok({ verified: true })
    },
  },
  // Public: sign contract
  {
    url: '/api/v1/public/contracts/:token/sign',
    method: 'post',
    response: ({ query: params, body }: any) => {
      if (!params?.token) return { code: 400, message: '参数错误' }
      const idx = contracts.findIndex(c => c.share_token === params.token && c.status === 'pending_sign')
      if (idx === -1) return { code: 404, message: '链接无效或已过期' }
      contracts[idx] = {
        ...contracts[idx],
        status: 'signed',
        signature_url: body.signature_image_url,
        signed_at: new Date().toISOString(),
      }
      return ok({ message: '签署成功' })
    },
  },
  // Share: set status to pending_sign
  {
    url: '/api/v1/contracts/:id/share',
    method: 'post',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = contracts.findIndex(c => c.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      contracts[idx] = { ...contracts[idx], status: 'pending_sign' }
      return ok({ message: 'ok' })
    },
  },
  // Share: revoke share token
  {
    url: '/api/v1/contracts/:id/share',
    method: 'delete',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = contracts.findIndex(c => c.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      contracts[idx] = { ...contracts[idx], status: 'pending_sign', share_token: null }
      return ok(null)
    },
  },
  // Status update
  {
    url: '/api/v1/contracts/:id/status',
    method: 'patch',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = contracts.findIndex(c => c.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      contracts[idx] = { ...contracts[idx], status: body.status, cancel_reason: body.cancel_reason ?? null }
      return ok({ status: contracts[idx].status })
    },
  },
  // List
  {
    url: '/api/v1/contracts',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...contracts]
      if (query.status) list = list.filter(c => c.status === query.status)
      if (query.customer_name) list = list.filter(c => c.customer_name.includes(query.customer_name))
      return paged(list)
    },
  },
  // Get by id
  {
    url: '/api/v1/contracts/:id',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const item = contracts.find(c => c.id === Number(params.id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  // Create
  {
    url: '/api/v1/contracts',
    method: 'post',
    response: ({ body }: any) => {
      // 参数校验
      if (!body?.customer_order_id || !body?.party_a || !body?.party_a_phone || !body?.party_b || !body?.party_b_phone) {
        return { code: 400, message: '缺少必填字段' }
      }
      const order = MOCK_ORDERS.find(o => o.id === (body.customer_order_id ?? body.order_id))
      const contract = {
        ...body,
        id: nextId++,
        contract_no: genContractNo(),
        order_no: order?.order_no ?? '',
        customer_name: order?.customer_name ?? '',
        customer_phone: order?.customer_phone ?? '',
        party_a: body.party_a ?? order?.customer_name ?? '',
        party_a_phone: body.party_a_phone ?? order?.customer_phone ?? '',
        party_b: body.party_b ?? '旅行社',
        party_b_phone: body.party_b_phone ?? '0755-12345678',
        status: 'pending_sign',
        share_token: genShareToken('ct'),
        travel_notice: body.travel_notice ?? null,
        signature_url: null,
        signed_at: null,
        created_at: new Date().toISOString(),
      }
      contracts.push(contract)
      return ok(contract)
    },
  },
  // Update
  {
    url: '/api/v1/contracts/:id',
    method: 'put',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      // 参数校验
      if (!body?.customer_order_id || !body?.party_a || !body?.party_a_phone || !body?.party_b || !body?.party_b_phone) {
        return { code: 400, message: '缺少必填字段' }
      }
      const idx = contracts.findIndex(c => c.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      contracts[idx] = { ...contracts[idx], ...body }
      return ok(contracts[idx])
    },
  },
  // Delete
  {
    url: '/api/v1/contracts/:id',
    method: 'delete',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      contracts = contracts.filter(c => c.id !== Number(params.id))
      return ok(null)
    },
  },
] as MockMethod[]

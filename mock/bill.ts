import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_BILLS } from './_data'

let bills = [...MOCK_BILLS]
let nextId = 20

export default [
  {
    url: '/api/v1/bills/summary',
    method: 'get',
    response: () => {
      const income = bills.filter(b => b.bill_type === 'income').reduce((s, b) => s + b.amount, 0)
      const expense = bills.filter(b => b.bill_type === 'expense').reduce((s, b) => s + b.amount, 0)
      return ok({
        total_income: income,
        total_expense: expense,
        total_profit: income - expense,
      })
    },
  },
  {
    url: '/api/v1/bills',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...bills]
      if (query.bill_type) list = list.filter(b => b.bill_type === query.bill_type)
      if (query.order_id) list = list.filter(b => b.order_id === Number(query.order_id))
      if (query.customer_order_id) list = list.filter(b => b.customer_order_id === Number(query.customer_order_id))
      if (query.account_id) list = list.filter(b => b.account_id === Number(query.account_id))
      if (query.start_date) list = list.filter(b => b.bill_date >= query.start_date)
      if (query.end_date) list = list.filter(b => b.bill_date <= query.end_date)
      return paged(list)
    },
  },
  {
    url: '/api/v1/bills/:id',
    method: 'get',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const item = bills.find(b => b.id === Number(params.id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  {
    url: '/api/v1/bills',
    method: 'post',
    response: ({ body }: any) => {
      const bill = { ...body, id: nextId++, created_at: new Date().toISOString() }
      bills.push(bill)
      return ok(bill)
    },
  },
  {
    url: '/api/v1/bills/:id',
    method: 'put',
    response: ({ query: params, body }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      const idx = bills.findIndex(b => b.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      bills[idx] = { ...bills[idx], ...body }
      return ok(bills[idx])
    },
  },
  {
    url: '/api/v1/bills/:id',
    method: 'delete',
    response: ({ query: params }: any) => {
      if (!params?.id) return { code: 400, message: '参数错误' }
      bills = bills.filter(b => b.id !== Number(params.id))
      return ok(null)
    },
  },
] as MockMethod[]

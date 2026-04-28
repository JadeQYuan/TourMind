import { writeFileSync } from 'fs'

// order.ts
writeFileSync('e:/Code/TourMind/mock/order.ts', `import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_ORDERS } from './_data'

let orders = [...MOCK_ORDERS]
let nextId = 10

function genOrderNo() {
  const d = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  return \`ORD-\${d}-\${String(nextId).padStart(3, '0')}\`
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
    response: ({ params }: any) => {
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
    response: ({ params, body }: any) => {
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
    response: ({ params, body }: any) => {
      const idx = orders.findIndex(o => o.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      orders[idx] = { ...orders[idx], status: body.status }
      return ok(orders[idx])
    },
  },
] as MockMethod[]
`, 'utf8')
console.log('order.ts written')

// itinerary.ts
writeFileSync('e:/Code/TourMind/mock/itinerary.ts', `import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_ITINERARIES, MOCK_ORDERS } from './_data'

let itineraries = [...MOCK_ITINERARIES]
let nextId = 10

export default [
  {
    url: '/api/v1/itineraries',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...itineraries]
      if (query.status) list = list.filter(i => i.status === query.status)
      if (query.keyword) list = list.filter(i =>
        i.customer_name.includes(query.keyword) ||
        i.customer_phone?.includes(query.keyword) ||
        i.order_no.includes(query.keyword)
      )
      if (query.order_id) list = list.filter(i => i.order_id === Number(query.order_id))
      return paged(list)
    },
  },
  {
    url: '/api/v1/itineraries/:id',
    method: 'get',
    response: ({ params }: any) => {
      const item = itineraries.find(i => i.id === Number(params.id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  {
    url: '/api/v1/itineraries',
    method: 'post',
    response: ({ body }: any) => {
      const order = MOCK_ORDERS.find(o => o.id === body.order_id)
      const item = {
        ...body,
        id: nextId++,
        order_no: order?.order_no ?? '',
        product_name: order?.product_name ?? '',
        customer_name: order?.customer_name ?? '',
        customer_phone: order?.customer_phone ?? '',
        status: 'active',
        created_at: new Date().toISOString(),
        days_detail: body.days_detail ?? [],
      }
      itineraries.push(item)
      return ok(item)
    },
  },
  {
    url: '/api/v1/itineraries/:id',
    method: 'put',
    response: ({ params, body }: any) => {
      const idx = itineraries.findIndex(i => i.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      itineraries[idx] = { ...itineraries[idx], ...body }
      return ok(itineraries[idx])
    },
  },
  {
    url: '/api/v1/itineraries/:id',
    method: 'delete',
    response: ({ params }: any) => {
      itineraries = itineraries.filter(i => i.id !== Number(params.id))
      return ok(null)
    },
  },
  {
    url: '/api/v1/itineraries/:id/share',
    method: 'post',
    response: ({ params }: any) => ok({ share_url: \`/preview/itinerary/mock-token-\${params.id}\` }),
  },
] as MockMethod[]
`, 'utf8')
console.log('itinerary.ts written')

// contract.ts
writeFileSync('e:/Code/TourMind/mock/contract.ts', `import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_CONTRACTS, MOCK_ORDERS } from './_data'

let contracts = [...MOCK_CONTRACTS]
let nextId = 10

function genContractNo() {
  const d = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  return \`CT-\${d}-\${String(nextId).padStart(3, '0')}\`
}

export default [
  {
    url: '/api/v1/contracts',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...contracts]
      if (query.status) list = list.filter(c => c.status === query.status)
      if (query.order_no) list = list.filter(c => c.order_no.includes(query.order_no))
      return paged(list)
    },
  },
  {
    url: '/api/v1/contracts/:id',
    method: 'get',
    response: ({ params }: any) => {
      const item = contracts.find(c => c.id === Number(params.id))
      return item ? ok(item) : { code: 404, message: '不存在' }
    },
  },
  {
    url: '/api/v1/contracts',
    method: 'post',
    response: ({ body }: any) => {
      const order = MOCK_ORDERS.find(o => o.id === body.order_id)
      const contract = {
        ...body,
        id: nextId++,
        contract_no: genContractNo(),
        order_no: order?.order_no ?? '',
        customer_name: order?.customer_name ?? '',
        customer_phone: order?.customer_phone ?? '',
        status: 'pending_sign',
        share_token: \`mock-share-token-\${nextId}\`,
        signature_url: null,
        signed_at: null,
        created_at: new Date().toISOString(),
      }
      contracts.push(contract)
      return ok(contract)
    },
  },
  // 客户端签署（外部访问，通过 share_token）
  {
    url: '/api/v1/contracts/sign/:token',
    method: 'get',
    response: ({ params }: any) => {
      const item = contracts.find(c => c.share_token === params.token)
      return item ? ok(item) : { code: 404, message: '链接无效或已过期' }
    },
  },
  {
    url: '/api/v1/contracts/sign/:token',
    method: 'post',
    response: ({ params }: any) => {
      const idx = contracts.findIndex(c => c.share_token === params.token)
      if (idx === -1) return { code: 404, message: '链接无效' }
      contracts[idx] = {
        ...contracts[idx],
        status: 'completed',
        signed_at: new Date().toISOString(),
        share_token: null,
      }
      return ok(contracts[idx])
    },
  },
  {
    url: '/api/v1/contracts/:id',
    method: 'delete',
    response: ({ params }: any) => {
      contracts = contracts.filter(c => c.id !== Number(params.id))
      return ok(null)
    },
  },
] as MockMethod[]
`, 'utf8')
console.log('contract.ts written')

// bill.ts
writeFileSync('e:/Code/TourMind/mock/bill.ts', `import type { MockMethod } from 'vite-plugin-mock'
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
      if (query.account_id) list = list.filter(b => b.account_id === Number(query.account_id))
      return paged(list)
    },
  },
  {
    url: '/api/v1/bills/:id',
    method: 'get',
    response: ({ params }: any) => {
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
    response: ({ params, body }: any) => {
      const idx = bills.findIndex(b => b.id === Number(params.id))
      if (idx === -1) return { code: 404, message: '不存在' }
      bills[idx] = { ...bills[idx], ...body }
      return ok(bills[idx])
    },
  },
  {
    url: '/api/v1/bills/:id',
    method: 'delete',
    response: ({ params }: any) => {
      bills = bills.filter(b => b.id !== Number(params.id))
      return ok(null)
    },
  },
] as MockMethod[]
`, 'utf8')
console.log('bill.ts written')

// user.ts
writeFileSync('e:/Code/TourMind/mock/user.ts', `import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_USERS } from './_data'

let users = [...MOCK_USERS]
let nextId = 10

function genPassword() {
  const chars = 'ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789!@#$%'
  return Array.from({ length: 12 }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
}

export default [
  {
    url: '/api/v1/users',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...users]
      if (query.role) list = list.filter(u => u.role === query.role)
      if (query.keyword) list = list.filter(u =>
        u.name.includes(query.keyword) ||
        (u.phone && u.phone.includes(query.keyword)) ||
        (u.employee_id && u.employee_id.includes(query.keyword))
      )
      return paged(list)
    },
  },
  {
    url: '/api/v1/users/:id',
    method: 'get',
    response: ({ params }: any) => ok(users.find(u => u.id === Number(params.id))),
  },
  {
    url: '/api/v1/users',
    method: 'post',
    response: ({ body }: any) => {
      const password = genPassword()
      const item = { ...body, id: nextId++, is_active: true, last_login_at: null, created_at: new Date().toISOString() }
      users.push(item)
      return ok({ ...item, generated_password: password })
    },
  },
  {
    url: '/api/v1/users/:id',
    method: 'put',
    response: ({ params, body }: any) => {
      const idx = users.findIndex(u => u.id === Number(params.id))
      if (idx !== -1) users[idx] = { ...users[idx], ...body }
      return ok(users[idx])
    },
  },
  {
    url: '/api/v1/users/:id/reset-password',
    method: 'post',
    response: () => ok({ generated_password: genPassword() }),
  },
] as MockMethod[]
`, 'utf8')
console.log('user.ts written')

// product.ts (update filter)
writeFileSync('e:/Code/TourMind/mock/product.ts', `import type { MockMethod } from 'vite-plugin-mock'
import { ok, paged, MOCK_PRODUCTS } from './_data'

let products = [...MOCK_PRODUCTS]
let nextId = 10

export default [
  {
    url: '/api/v1/products',
    method: 'get',
    response: ({ query }: any) => {
      let list = [...products]
      if (query.keyword) list = list.filter(p => p.name.includes(query.keyword) || (p.destination && p.destination.includes(query.keyword)))
      if (query.status) list = list.filter(p => p.status === query.status)
      return paged(list)
    },
  },
  {
    url: '/api/v1/products/:id',
    method: 'get',
    response: ({ params }: any) => ok(products.find(p => p.id === Number(params.id))),
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
  {
    url: '/api/v1/products/:id',
    method: 'put',
    response: ({ params, body }: any) => {
      const idx = products.findIndex(p => p.id === Number(params.id))
      if (idx !== -1) products[idx] = { ...products[idx], ...body }
      return ok(products[idx] ?? null)
    },
  },
  {
    url: '/api/v1/products/:id',
    method: 'delete',
    response: ({ params }: any) => {
      products = products.filter(p => p.id !== Number(params.id))
      return ok(null)
    },
  },
] as MockMethod[]
`, 'utf8')
console.log('product.ts written')

// supplier.ts (add status filter)
writeFileSync('e:/Code/TourMind/mock/supplier.ts', `import type { MockMethod } from 'vite-plugin-mock'
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
    response: ({ params }: any) => ok(suppliers.find(s => s.id === Number(params.id))),
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
    response: ({ params, body }: any) => {
      const idx = suppliers.findIndex(s => s.id === Number(params.id))
      if (idx !== -1) suppliers[idx] = { ...suppliers[idx], ...body }
      return ok(suppliers[idx])
    },
  },
  {
    url: '/api/v1/suppliers/:id',
    method: 'delete',
    response: ({ params }: any) => {
      suppliers = suppliers.filter(s => s.id !== Number(params.id))
      return ok(null)
    },
  },
] as MockMethod[]
`, 'utf8')
console.log('supplier.ts written')

// account.ts (add user filter)
writeFileSync('e:/Code/TourMind/mock/account.ts', `import type { MockMethod } from 'vite-plugin-mock'
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
    response: ({ params }: any) => ok(accounts.find(a => a.id === Number(params.id))),
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
    response: ({ params, body }: any) => {
      const idx = accounts.findIndex(a => a.id === Number(params.id))
      if (idx !== -1) accounts[idx] = { ...accounts[idx], ...body }
      return ok(accounts[idx])
    },
  },
  {
    url: '/api/v1/accounts/:id',
    method: 'delete',
    response: ({ params }: any) => {
      accounts = accounts.filter(a => a.id !== Number(params.id))
      return ok(null)
    },
  },
] as MockMethod[]
`, 'utf8')
console.log('account.ts written')

console.log('All mock files written!')

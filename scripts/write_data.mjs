import { writeFileSync } from 'fs'

const content = `// ── 共享 Mock 数据 ─────────────────────────────────────────────────

export const MOCK_USERS = [
  {
    id: 1,
    name: 'Admin',
    phone: '13800000000',
    employee_id: 'Admin',
    role: 'system_admin',
    is_active: true,
    last_login_at: '2026-04-16T09:00:00',
    created_at: '2026-01-01T00:00:00',
  },
  {
    id: 2,
    name: '张经理',
    phone: '13900001111',
    employee_id: 'EMP001',
    role: 'admin',
    is_active: true,
    last_login_at: '2026-04-15T09:00:00',
    created_at: '2026-01-05T00:00:00',
  },
  {
    id: 3,
    name: '李助理',
    phone: '13900002222',
    employee_id: 'EMP002',
    role: 'assistant',
    is_active: true,
    last_login_at: '2026-04-14T10:00:00',
    created_at: '2026-01-05T00:00:00',
  },
  {
    id: 4,
    name: '王助理',
    phone: '13900003333',
    employee_id: 'EMP003',
    role: 'assistant',
    is_active: true,
    last_login_at: '2026-04-10T11:00:00',
    created_at: '2026-02-01T00:00:00',
  },
]

export const MOCK_USER = MOCK_USERS[0]

export const MOCK_PRODUCTS = [
  {
    id: 1,
    name: '桂林山水5日游',
    destination: '桂林',
    days: 5,
    reference_price: 2980,
    includes: '往返高铁票、4晚酒店、漓江竹筏、景区门票、全程地接',
    excludes: '个人消费、单房差、保险',
    cancellation_policy: '出发前7天取消退80%，出发前3天取消不退款',
    travel_notice: '请携带身份证原件，高铁站集合',
    important_tips: '建议购买旅游意外险',
    notes: '适合亲子家庭',
    status: 'active',
    itinerary_template: [
      { seq: 1, details: '广州南站出发，乘高铁抵桂林，接站入住，游览象鼻山', accommodation_area: '桂林市区', notes: null },
      { seq: 2, details: '漓江竹筏漂流，途经9马画山，抵达阳朔', accommodation_area: '阳朔西街', notes: '建议携带防晒霜' },
      { seq: 3, details: '骑行十里画廊，参观月亮山', accommodation_area: '阳朔西街', notes: null },
      { seq: 4, details: '遇龙河漂流，返回桂林，游览两江四湖', accommodation_area: '桂林市区', notes: null },
      { seq: 5, details: '自由活动，午后返程', accommodation_area: null, notes: null },
    ],
    created_at: '2026-01-15T00:00:00',
  },
  {
    id: 2,
    name: '云南大理丽江7日深度游',
    destination: '大理/丽江',
    days: 7,
    reference_price: 5800,
    includes: '往返机票、6晚精品民宿、全程包车、玉龙雪山门票',
    excludes: '餐费、保险、个人消费',
    cancellation_policy: '出发前14天取消退90%，7天内退50%，3天内不退款',
    travel_notice: '高原地区，注意防晒和保暖',
    important_tips: '玉龙雪山须提前预约，高原反应患者慎行',
    notes: '小团定制，最多6人',
    status: 'active',
    itinerary_template: [
      { seq: 1, details: '飞大理，接机入住，大理古城自由漫步', accommodation_area: '大理古城', notes: null },
      { seq: 2, details: '苍山洱海一日，环海骑行', accommodation_area: '大理古城', notes: null },
      { seq: 3, details: '喜洲古镇、蝴蝶泉', accommodation_area: '大理古城', notes: null },
      { seq: 4, details: '沙溪古镇，驱车前往丽江', accommodation_area: '丽江古城', notes: null },
      { seq: 5, details: '玉龙雪山、蓝月谷', accommodation_area: '丽江古城', notes: '高原反应注意事项' },
      { seq: 6, details: '束河古镇，纳西古乐表演', accommodation_area: '丽江古城', notes: null },
      { seq: 7, details: '自由购物，飞机返回深圳', accommodation_area: null, notes: null },
    ],
    created_at: '2026-01-20T00:00:00',
  },
  {
    id: 3,
    name: '北京文化3日游',
    destination: '北京',
    days: 3,
    reference_price: 1980,
    includes: '往返高铁票、2晚酒店',
    excludes: '餐费、景区门票、个人消费',
    cancellation_policy: '出发前3天取消退50%，出发当天不退款',
    travel_notice: '故宫需提前网上预约购票',
    important_tips: null,
    notes: null,
    status: 'active',
    itinerary_template: [
      { seq: 1, details: '高铁抵京，故宫、天安门广场', accommodation_area: '北京王府井', notes: null },
      { seq: 2, details: '颐和园、圆明园', accommodation_area: '北京王府井', notes: null },
      { seq: 3, details: '八达岭长城，下午返程', accommodation_area: null, notes: null },
    ],
    created_at: '2026-02-01T00:00:00',
  },
]

export const MOCK_SUPPLIERS = [
  { id: 1, name: '桂林山水地接社', contact_person: '陈伟', contact_phone: '0773-1234567', notes: '桂林本地优质地接', is_active: true, created_at: '2026-01-15T00:00:00' },
  { id: 2, name: '云南大理旅游有限公司', contact_person: '赵丽', contact_phone: '0872-9876543', notes: '大理丽江地接', is_active: true, created_at: '2026-01-20T00:00:00' },
  { id: 3, name: '携程航空服务', contact_person: '王明', contact_phone: '010-88888888', notes: '机票/高铁票预订', is_active: true, created_at: '2026-01-10T00:00:00' },
  { id: 4, name: '如家连锁酒店', contact_person: '李红', contact_phone: '021-66666666', notes: null, is_active: true, created_at: '2026-01-10T00:00:00' },
  { id: 5, name: '平安旅游保险', contact_person: '孙强', contact_phone: '400-888-0000', notes: null, is_active: true, created_at: '2026-02-01T00:00:00' },
]

export const MOCK_ACCOUNTS = [
  { id: 1, name: '招商银行对公账户', account_type: 'bank', description: '尾号8888，主要收款账户', user_id: 2, user_name: '张经理', is_active: true, created_at: '2026-01-01T00:00:00' },
  { id: 2, name: '公司微信收款', account_type: 'wechat', description: '微信商户号收款', user_id: 2, user_name: '张经理', is_active: true, created_at: '2026-01-01T00:00:00' },
  { id: 3, name: '支付宝企业账户', account_type: 'alipay', description: null, user_id: 3, user_name: '李助理', is_active: true, created_at: '2026-01-05T00:00:00' },
  { id: 4, name: '现金备用金', account_type: 'cash', description: '日常现金支出', user_id: null, user_name: null, is_active: true, created_at: '2026-01-01T00:00:00' },
]

// 订单是核心实体
export const MOCK_ORDERS = [
  {
    id: 1,
    order_no: 'ORD-20260315-001',
    product_id: 1,
    product_name: '桂林山水5日游',
    customer_name: '张三',
    customer_phone: '13912345678',
    travel_date: '2026-05-01',
    days: 5,
    price: 12800,
    deposit: 3000,
    supplier_id: 1,
    supplier_name: '桂林山水地接社',
    cost: 8400,
    profit: 4400,
    status: 'pending_payment',
    user_id: 3,
    user_name: '李助理',
    notes: '漓江精华游线路',
    created_at: '2026-03-15T10:00:00',
  },
  {
    id: 2,
    order_no: 'ORD-20260410-002',
    product_id: 2,
    product_name: '云南大理丽江7日深度游',
    customer_name: '王五',
    customer_phone: '13698765432',
    travel_date: '2026-06-10',
    days: 7,
    price: 11600,
    deposit: 3000,
    supplier_id: 2,
    supplier_name: '云南大理旅游有限公司',
    cost: null,
    profit: null,
    status: 'pending_deposit',
    user_id: 3,
    user_name: '李助理',
    notes: null,
    created_at: '2026-04-10T09:00:00',
  },
  {
    id: 3,
    order_no: 'ORD-20260201-003',
    product_id: 3,
    product_name: '北京文化3日游',
    customer_name: '李四',
    customer_phone: '13711223344',
    travel_date: '2026-03-20',
    days: 3,
    price: 7200,
    deposit: 2000,
    supplier_id: 3,
    supplier_name: '携程航空服务',
    cost: 4800,
    profit: 2400,
    status: 'completed',
    user_id: 4,
    user_name: '王助理',
    notes: null,
    created_at: '2026-02-01T09:00:00',
  },
]

// 行程关联订单
export const MOCK_ITINERARIES = [
  {
    id: 1,
    order_id: 1,
    order_no: 'ORD-20260315-001',
    product_name: '桂林山水5日游',
    customer_name: '张三',
    customer_phone: '13912345678',
    destination: '桂林',
    pax: 4,
    travelers: [
      { name: '张三', id_no: '440101199001011234' },
      { name: '李梅', id_no: '440101199203045678' },
      { name: '张小明', id_no: '' },
      { name: '张小红', id_no: '' },
    ],
    start_date: '2026-05-01',
    end_date: '2026-05-05',
    status: 'active',
    created_at: '2026-03-15T10:00:00',
    days_detail: [
      { id: 1, seq: 1, date: '2026-05-01', details: '广州南站出发，乘高铁抵桂林北站，接站后入住酒店，游览象鼻山', accommodation_area: '桂林市区', notes: null, attachments: [] },
      { id: 2, seq: 2, date: '2026-05-02', details: '漓江竹筏漂流全程，途经9马画山、黄布滩等核心景点，下午抵达阳朔', accommodation_area: '阳朔西街', notes: '建议携带防晒霜', attachments: [] },
      { id: 3, seq: 3, date: '2026-05-03', details: '骑行十里画廊，参观月亮山，体验阳朔风情', accommodation_area: '阳朔西街', notes: null, attachments: [] },
      { id: 4, seq: 4, date: '2026-05-04', details: '遇龙河竹筏漂流，下午返回桂林，游览两江四湖', accommodation_area: '桂林市区', notes: null, attachments: [] },
      { id: 5, seq: 5, date: '2026-05-05', details: '自由活动，购物，午后乘高铁返回广州', accommodation_area: null, notes: null, attachments: [] },
    ],
  },
  {
    id: 2,
    order_id: 3,
    order_no: 'ORD-20260201-003',
    product_name: '北京文化3日游',
    customer_name: '李四',
    customer_phone: '13711223344',
    destination: '北京',
    pax: 3,
    travelers: [
      { name: '李四', id_no: '310101198712031234' },
      { name: '林美', id_no: '310101199003065678' },
      { name: '李小虎', id_no: '' },
    ],
    start_date: '2026-03-20',
    end_date: '2026-03-22',
    status: 'completed',
    created_at: '2026-02-01T09:00:00',
    days_detail: [
      { id: 6, seq: 1, date: '2026-03-20', details: '高铁抵达北京，天安门广场、故宫博物院参观', accommodation_area: '北京王府井', notes: null, attachments: [] },
      { id: 7, seq: 2, date: '2026-03-21', details: '颐和园、圆明园', accommodation_area: '北京王府井', notes: null, attachments: [] },
      { id: 8, seq: 3, date: '2026-03-22', details: '长城（八达岭），下午乘高铁返回上海', accommodation_area: null, notes: null, attachments: [] },
    ],
  },
]

// 合同关联订单，状态简化
export const MOCK_CONTRACTS = [
  {
    id: 1,
    contract_no: 'CT-20260315-001',
    order_id: 1,
    order_no: 'ORD-20260315-001',
    customer_name: '张三',
    customer_phone: '13912345678',
    status: 'pending_sign',
    share_token: 'mock-share-token-abc123',
    signature_url: null,
    signed_at: null,
    created_at: '2026-03-15T10:00:00',
  },
  {
    id: 2,
    contract_no: 'CT-20260201-002',
    order_id: 3,
    order_no: 'ORD-20260201-003',
    customer_name: '李四',
    customer_phone: '13711223344',
    status: 'completed',
    share_token: null,
    signature_url: '/mock/signature_liisi.png',
    signed_at: '2026-02-08T14:30:00',
    created_at: '2026-02-01T09:00:00',
  },
]

// 账单关联订单
export const MOCK_BILLS = [
  { id: 1, order_id: 3, order_no: 'ORD-20260201-003', bill_type: 'income', income_type: '定金', expense_type: null, supplier_id: null, amount: 2000, bill_date: '2026-02-08', account_id: 1, account_name: '招商银行对公账户', notes: '李四定金', attachment_url: null, created_at: '2026-02-08T15:00:00' },
  { id: 2, order_id: 3, order_no: 'ORD-20260201-003', bill_type: 'income', income_type: '尾款', expense_type: null, supplier_id: null, amount: 5200, bill_date: '2026-03-15', account_id: 1, account_name: '招商银行对公账户', notes: '李四尾款', attachment_url: null, created_at: '2026-03-15T10:00:00' },
  { id: 3, order_id: 3, order_no: 'ORD-20260201-003', bill_type: 'expense', income_type: null, expense_type: '供应商付款', supplier_id: 3, amount: 2400, bill_date: '2026-02-10', account_id: 1, account_name: '招商银行对公账户', notes: '高铁票3张', attachment_url: null, created_at: '2026-02-10T10:00:00' },
  { id: 4, order_id: 3, order_no: 'ORD-20260201-003', bill_type: 'expense', income_type: null, expense_type: '供应商付款', supplier_id: 4, amount: 1500, bill_date: '2026-02-10', account_id: 1, account_name: '招商银行对公账户', notes: '2晚酒店', attachment_url: null, created_at: '2026-02-10T10:30:00' },
  { id: 5, order_id: 1, order_no: 'ORD-20260315-001', bill_type: 'income', income_type: '定金', expense_type: null, supplier_id: null, amount: 3000, bill_date: '2026-03-25', account_id: 2, account_name: '公司微信收款', notes: '张三定金', attachment_url: null, created_at: '2026-03-25T09:00:00' },
  { id: 6, order_id: null, order_no: null, bill_type: 'expense', income_type: null, expense_type: '运营成本', supplier_id: null, amount: 900, bill_date: '2026-04-01', account_id: 4, account_name: '现金备用金', notes: '4月办公费用', attachment_url: null, created_at: '2026-04-01T09:00:00' },
]

export const ok = (data: unknown) => ({ code: 0, message: 'ok', data })
export const paged = (items: unknown[], total?: number) => ok({ items, total: total ?? items.length, page: 1, page_size: 20 })
`

writeFileSync('e:/Code/TourMind/mock/_data.ts', content, 'utf8')
console.log('_data.ts written')

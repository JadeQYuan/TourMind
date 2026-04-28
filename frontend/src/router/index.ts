import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/LoginView.vue'),
      meta: { public: true },
    },
    // 外部合同签署页（无需登录）
    {
      path: '/sign/:token',
      name: 'contract-sign',
      component: () => import('@/views/contract/ContractSignView.vue'),
      meta: { public: true },
    },
    // 公开行程分享页（无需登录）
    {
      path: '/public/itinerary/:token',
      name: 'public-itinerary',
      component: () => import('@/views/itinerary/ItineraryShareView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('@/views/layout/AppLayout.vue'),
      children: [
        { path: '', redirect: '/orders' },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
          meta: { roles: ['system_admin', 'admin'] },
        },
        // 产品
        {
          path: 'products',
          name: 'product-list',
          component: () => import('@/views/product/ProductListView.vue'),
        },
        // 行程
        {
          path: 'itineraries',
          name: 'itinerary-list',
          component: () => import('@/views/itinerary/ItineraryListView.vue'),
        },
        {
          path: 'itineraries/create',
          name: 'itinerary-create',
          component: () => import('@/views/itinerary/ItineraryFormView.vue'),
        },
        {
          path: 'itineraries/:id/edit',
          name: 'itinerary-edit',
          component: () => import('@/views/itinerary/ItineraryFormView.vue'),
        },
        {
          path: 'itineraries/:id',
          name: 'itinerary-detail',
          component: () => import('@/views/itinerary/ItineraryDetailView.vue'),
        },
        // 订单
        {
          path: 'orders',
          name: 'order-list',
          component: () => import('@/views/order/OrderListView.vue'),
        },
        // 合同
        {
          path: 'contracts',
          name: 'contract-list',
          component: () => import('@/views/contract/ContractListView.vue'),
        },
        {
          path: 'contracts/create',
          name: 'contract-create',
          component: () => import('@/views/contract/ContractFormView.vue'),
        },
        {
          path: 'contracts/:id/edit',
          name: 'contract-edit',
          component: () => import('@/views/contract/ContractFormView.vue'),
          props: (route: any) => ({ editId: Number(route.params.id) }),
        },
        {
          path: 'contracts/:id',
          name: 'contract-detail',
          component: () => import('@/views/contract/ContractDetailView.vue'),
        },
        // 账单
        {
          path: 'bills',
          name: 'bill-list',
          component: () => import('@/views/bill/BillListView.vue'),
        },
        // 供应商
        {
          path: 'suppliers',
          name: 'supplier-list',
          component: () => import('@/views/supplier/SupplierListView.vue'),
        },
        // 账户
        {
          path: 'accounts',
          name: 'account-list',
          component: () => import('@/views/account/AccountListView.vue'),
          meta: { roles: ['system_admin', 'admin'] },
        },
        // 用户管理
        {
          path: 'users',
          name: 'user-list',
          component: () => import('@/views/user/UserListView.vue'),
          meta: { roles: ['system_admin', 'admin'] },
        },
        // 运维审计
        {
          path: 'audit-logs',
          name: 'audit-logs',
          component: () => import('@/views/audit/AuditLogView.vue'),
          meta: { roles: ['system_admin'] },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.public) return true
  const auth = useAuthStore()
  if (!auth.token) return { name: 'login', query: { redirect: to.fullPath } }
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }
  // Role-based route guard
  const roles = to.meta.roles as string[] | undefined
  if (roles && auth.user && !roles.includes(auth.user.role)) {
    return { path: '/orders' }
  }
  return true
})

export default router

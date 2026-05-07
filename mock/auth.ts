import type { MockMethod } from 'vite-plugin-mock'
import { ok, MOCK_USERS } from './_data'

// Credentials: username 仅允许手机号
const CREDENTIALS: { id: number; phone: string; password: string }[] = [
  { id: 1, phone: '13800000000', password: 'Admind0Tour@1' },
  { id: 2, phone: '13900001111', password: 'Admin1234@56' },
  { id: 3, phone: '13900002222', password: 'Admin1234@56' },
  { id: 4, phone: '13900003333', password: 'Admin1234@56' },
]

export default [
  {
    url: '/api/v1/auth/login',
    method: 'post',
    response: ({ body }: any) => {
      const { username = '', password = '' } = body ?? {}
      if (!username || !password) {
        return { code: 400, message: '账号和密码不能为空' }
      }
      // 仅允许手机号登录
      const matched = CREDENTIALS.find(c => c.phone === username && c.password === password)
      if (!matched) {
        return { code: 401, message: '仅支持手机号登录，或账号/密码错误' }
      }
      const user = MOCK_USERS.find(u => u.id === matched.id)!
      return ok({
        access_token: `mock-jwt-token-uid-${matched.id}`,
        token_type: 'bearer',
        user: {
          id: user.id,
          full_name: user.full_name,
          role: user.role,
          must_change_password: user.must_change_password ?? false,
        },
      })
    },
  },
  {
    url: '/api/v1/auth/me',
    method: 'get',
    response: ({ headers }: any) => {
      const auth = headers?.authorization ?? ''
      const match = auth.match(/mock-jwt-token-uid-(\d+)/)
      const uid = match ? Number(match[1]) : 1
      const user = MOCK_USERS.find(u => u.id === uid) ?? MOCK_USERS[0]
      return ok(user)
    },
  },
  {
    url: '/api/v1/auth/change-password',
    method: 'post',
    response: () => ok({ message: '密码修改成功' }),
  },
  {
    url: '/api/v1/auth/logout',
    method: 'post',
    response: () => ({ code: 0 }),
  },
] as MockMethod[]

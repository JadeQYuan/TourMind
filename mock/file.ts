import type { MockMethod } from 'vite-plugin-mock'
import { ok } from './_data'

export default [
  {
    url: '/api/v1/files/upload',
    method: 'post',
    response: () => ok({
      file_url: '/uploads/mock/placeholder.jpg',
      file_key: 'mock/' + Math.random().toString(36).slice(2) + '.jpg',
    }),
  },
] as MockMethod[]

import { adminRequest } from '../../../adminApi'

export async function signIn(identifier, password) {
  return adminRequest('/users/login', null, {
    method: 'POST',
    body: { identifier, password },
  })
}

export function getCurrentAdmin(token) {
  return adminRequest('/admin/auth/me', token)
}

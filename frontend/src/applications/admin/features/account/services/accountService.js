import { adminRequest } from '../../../adminApi'

export function getAdminProfile(token) {
  return adminRequest('/admin/auth/me', token)
}

export function changeAdminPassword(token, currentPassword, newPassword) {
  return adminRequest('/admin/auth/change-password', token, {
    method: 'POST',
    body: {
      current_password: currentPassword,
      new_password: newPassword,
    },
  })
}

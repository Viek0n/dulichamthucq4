const configuredBase = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
const API_BASE = configuredBase.endsWith('/api')
  ? configuredBase
  : `${configuredBase}/api`

export async function adminRequest(path, token, options = {}) {
  const headers = new Headers(options.headers)
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (options.body !== undefined) headers.set('Content-Type', 'application/json')

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  })

  if (response.status === 204) return null

  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const detail =
      typeof payload === 'object' && payload !== null
        ? payload.detail || payload.message
        : payload
    throw new Error(detail || `Request failed (${response.status})`)
  }

  return payload
}

export function apiErrorMessage(error) {
  if (Array.isArray(error?.message)) {
    return error.message
      .map((item) => item.msg || JSON.stringify(item))
      .join(', ')
  }
  return error?.message || 'Something went wrong. Please try again.'
}

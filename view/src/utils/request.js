import { getToken, removeToken } from './auth'

/**
 * 统一处理响应
 * @param {Response} response
 * @param {{ skipAuth?: boolean }} options — skipAuth 时 401 视为正常业务错误，不跳转
 */
async function handleResponse(response, options = {}) {
  if ((response.status === 401 || response.status === 403) && !options.skipAuth) {
    removeToken()
    window.location.href = '/login'
    throw new Error('登录已过期，请重新登录')
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    const msg = body.message || body.response?.message || `请求失败 (${response.status})`
    throw new Error(msg)
  }
  return response
}

/**
 * POST JSON 请求
 */
export async function post(url, data, options = {}) {
  const { skipAuth, headers: extraHeaders } = options
  const headers = skipAuth
    ? { 'Content-Type': 'application/json', ...extraHeaders }
    : authHeaders(extraHeaders)

  const res = await fetch(url, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })
  await handleResponse(res, { skipAuth })
  return res.json()
}

/**
 * 上传文件（FormData）
 */
export async function upload(url, formData) {
  const token = getToken()
  const headers = {}
  if (token) headers['Authorization'] = 'Bearer ' + token

  const res = await fetch(url, { method: 'POST', headers, body: formData })
  await handleResponse(res)
  return res.json()
}

/**
 * SSE 流式请求 — 返回原生 Response（调用方自行读取 body stream）
 */
export function sseRequest(url, data) {
  const token = getToken()
  if (!token) {
    removeToken()
    window.location.href = '/login'
    throw new Error('未登录')
  }

  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
      'Authorization': 'Bearer ' + token,
    },
    body: JSON.stringify(data),
  })
}

// ---- 内部工具 ----

function authHeaders(extra = {}) {
  const token = getToken()
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: 'Bearer ' + token } : {}),
    ...extra,
  }
}

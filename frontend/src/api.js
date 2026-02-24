const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('antiswipe_token')
}

async function request(path, options = {}) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers })
  if (res.status === 401) {
    localStorage.removeItem('antiswipe_token')
    localStorage.removeItem('antiswipe_user')
    window.location.reload()
    return
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `API error: ${res.status}`)
  }
  return res.json()
}

export const api = {
  register:      (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login:         (data) => request('/auth/login',    { method: 'POST', body: JSON.stringify(data) }),
  me:            ()     => request('/auth/me'),
  getTasks:      ()     => request('/tasks/'),
  createTask:    (data) => request('/tasks/',               { method: 'POST',   body: JSON.stringify(data) }),
  updateTask:    (id, data) => request(`/tasks/${id}`,      { method: 'PATCH',  body: JSON.stringify(data) }),
  completeTask:  (id)   => request(`/tasks/${id}/complete`, { method: 'PATCH' }),
  registerSwipe: (id)   => request(`/tasks/${id}/swipe`,    { method: 'PATCH' }),
  deleteTask:    (id)   => request(`/tasks/${id}`,          { method: 'DELETE' }),
  getStats:      ()     => request('/tasks/stats/summary'),
  savePushSub:   (sub)  => request('/push/subscribe',       { method: 'POST',   body: JSON.stringify(sub) }),
}

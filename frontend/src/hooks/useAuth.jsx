import { createContext, useContext, useState } from 'react'
import { api } from '../api'

const AuthContext = createContext(null)
const STORAGE_KEY_TOKEN = 'antiswipe_token'
const STORAGE_KEY_USER  = 'antiswipe_user'

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY_USER)
      return stored ? JSON.parse(stored) : null
    } catch { return null }
  })

  const _save = (token, user) => {
    localStorage.setItem(STORAGE_KEY_TOKEN, token)
    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(user))
    setUser(user)
  }

  const login = async (email, password) => {
    const res = await api.login({ email, password })
    _save(res.access_token, res.user)
    return res.user
  }

  const register = async (email, name, password) => {
    const res = await api.register({ email, name, password })
    _save(res.access_token, res.user)
    return res.user
  }

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY_TOKEN)
    localStorage.removeItem(STORAGE_KEY_USER)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)

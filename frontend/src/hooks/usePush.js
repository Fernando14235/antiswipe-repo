import { useEffect, useState } from 'react'
import { api } from '../api'

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = atob(base64)
  return Uint8Array.from([...rawData].map(c => c.charCodeAt(0)))
}

export function usePush() {
  const [permission, setPermission] = useState(Notification.permission)
  const [subscribed, setSubscribed] = useState(false)

  const subscribe = async () => {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
      alert('Push notifications are not supported in this browser.')
      return
    }
    const perm = await Notification.requestPermission()
    setPermission(perm)
    if (perm !== 'granted') return
    try {
      const { public_key } = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/push/vapid-public-key`).then(r => r.json())
      const reg = await navigator.serviceWorker.ready
      const sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(public_key),
      })
      const subJson = sub.toJSON()
      await api.savePushSub({ endpoint: subJson.endpoint, keys: subJson.keys })
      setSubscribed(true)
    } catch (e) {
      console.error('Push subscription failed:', e)
    }
  }

  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(console.error)
    }
  }, [])

  useEffect(() => {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      navigator.serviceWorker.ready.then(reg =>
        reg.pushManager.getSubscription().then(sub => setSubscribed(!!sub))
      )
    }
  }, [])

  return { permission, subscribed, subscribe }
}

import { useEffect } from 'react'
import './Toast.css'

interface ToastProps {
  message: string
  type: 'error' | 'success' | 'info'
  onClose: () => void
  duration?: number
}

export default function Toast({ message, type, onClose, duration = 4000 }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration)
    return () => clearTimeout(timer)
  }, [onClose, duration])

  return (
    <div className={`toast toast-${type}`}>
      <p>{message}</p>
      <button className="toast-close" onClick={onClose} title="Close notification">×</button>
    </div>
  )
}

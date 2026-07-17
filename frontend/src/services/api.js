import axios from 'axios'

/**
 * Axios instance pre-configured for CyberGuardian API.
 * Uses Vite proxy in development: /api → http://localhost:8000
 */
const api = axios.create({
  baseURL: '/api',
  timeout: 60000, // 60s – agents need time
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// Request interceptor – log in development
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.debug(`[CG API] ${config.method?.toUpperCase()} ${config.url}`)
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor – normalize errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'Error de conexión con el servidor'
    return Promise.reject({ ...error, userMessage: message })
  }
)

export default api

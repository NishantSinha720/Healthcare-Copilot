import axios from 'axios'
import type {
  AxiosInstance,
  InternalAxiosRequestConfig,
} from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000/api'

const ACCESS_TOKEN_KEY = 'healthcare_access_token'
const REFRESH_TOKEN_KEY = 'healthcare_refresh_token'

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setTokens(
  access: string,
  refresh: string,
): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, access)
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (
    config: InternalAxiosRequestConfig,
  ): InternalAxiosRequestConfig => {
    const token = getAccessToken()

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
)

let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken()

  if (!refreshToken) {
    return null
  }

  try {
    const response = await axios.post(
      `${API_BASE_URL}/auth/token/refresh/`,
      {
        refresh: refreshToken,
      },
    )

    const newAccessToken = response.data?.access

    if (!newAccessToken) {
      clearTokens()
      return null
    }

    localStorage.setItem(
      ACCESS_TOKEN_KEY,
      newAccessToken,
    )

    return newAccessToken
  } catch {
    clearTokens()
    window.dispatchEvent(new Event('auth:logout'))
    return null
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry
    ) {
      return Promise.reject(error)
    }

    const requestUrl = String(originalRequest.url || '')

    if (requestUrl.includes('/auth/token/refresh/')) {
      clearTokens()
      window.dispatchEvent(new Event('auth:logout'))
      return Promise.reject(error)
    }

    originalRequest._retry = true

    if (!refreshPromise) {
      refreshPromise = refreshAccessToken().finally(() => {
        refreshPromise = null
      })
    }

    const newAccessToken = await refreshPromise

    if (!newAccessToken) {
      return Promise.reject(error)
    }

    originalRequest.headers.Authorization =
      `Bearer ${newAccessToken}`

    return api(originalRequest)
  },
)

export default api

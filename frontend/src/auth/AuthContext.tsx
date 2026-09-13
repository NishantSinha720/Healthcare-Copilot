import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import type {
  ReactNode,
} from 'react'

import api, {
  clearTokens,
  getAccessToken,
  setTokens,
} from '../api/client'

export type UserRole =
  | 'PATIENT'
  | 'DOCTOR'
  | 'ADMIN'

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  phone_number: string
  date_of_birth: string | null
  is_email_verified: boolean
  created_at: string
  updated_at: string
}

interface LoginResponse {
  user: User
  tokens: {
    access: string
    refresh: string
  }
}

interface RegisterResponse {
  user: User
}

export interface RegisterData {
  username: string
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  phone_number: string
  date_of_birth: string
}

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (
    username: string,
    password: string,
  ) => Promise<User>
  register: (
    data: RegisterData,
  ) => Promise<User>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext =
  createContext<AuthContextValue | undefined>(
    undefined,
  )

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = getAccessToken()

    if (!token) {
      setUser(null)
      return
    }

    try {
      const response = await api.get<User>(
        '/auth/me/',
      )

      setUser(response.data)
    } catch {
      clearTokens()
      setUser(null)
    }
  }, [])

  useEffect(() => {
    let mounted = true

    const initializeAuth = async () => {
      const token = getAccessToken()

      if (!token) {
        if (mounted) {
          setIsLoading(false)
        }
        return
      }

      try {
        const response = await api.get<User>(
          '/auth/me/',
        )

        if (mounted) {
          setUser(response.data)
        }
      } catch {
        clearTokens()

        if (mounted) {
          setUser(null)
        }
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    void initializeAuth()

    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    const handleLogout = () => {
      setUser(null)
    }

    window.addEventListener(
      'auth:logout',
      handleLogout,
    )

    return () => {
      window.removeEventListener(
        'auth:logout',
        handleLogout,
      )
    }
  }, [])

  const login = useCallback(
    async (
      username: string,
      password: string,
    ): Promise<User> => {
      const response =
        await api.post<LoginResponse>(
          '/auth/login/',
          {
            username,
            password,
          },
        )

      setTokens(
        response.data.tokens.access,
        response.data.tokens.refresh,
      )

      setUser(response.data.user)

      return response.data.user
    },
    [],
  )

  const register = useCallback(
    async (
      data: RegisterData,
    ): Promise<User> => {
      const response =
        await api.post<RegisterResponse>(
          '/auth/register/',
          data,
        )

      const registeredUser =
        response.data.user

      await login(
        registeredUser.username,
        data.password,
      )

      return registeredUser
    },
    [login],
  )

  const logout = useCallback(() => {
    clearTokens()
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [
      user,
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    ],
  )

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error(
      'useAuth must be used inside an AuthProvider',
    )
  }

  return context
}

import { useState } from 'react'
import type { FormEvent } from 'react'
import {
  AlertCircle,
  ArrowRight,
  HeartPulse,
  LockKeyhole,
  UserRound,
} from 'lucide-react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import doctorPhoto from '../assets/doctor-profile.jpeg'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const from =
    (location.state as { from?: string } | null)?.from || '/'

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()
    setError('')

    if (!username.trim() || !password) {
      setError('Please enter your username and password.')
      return
    }

    try {
      setIsSubmitting(true)

      await login(username.trim(), password)

      navigate(from, { replace: true })
    } catch (requestError: any) {
      const message =
        requestError?.response?.data?.detail ||
        requestError?.response?.data?.non_field_errors?.[0] ||
        requestError?.response?.data?.message ||
        'Unable to sign in. Please check your credentials.'

      setError(
        Array.isArray(message) ? message[0] : String(message),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div
      className="auth-page"
      style={{ backgroundImage: `url(${doctorPhoto})` }}
    >
      <div className="auth-page-overlay" />

      <div className="auth-brand">
        <div className="auth-brand-mark">
          <HeartPulse size={25} strokeWidth={2.5} />
        </div>

        <div>
          <strong>HealthCopilot</strong>
          <span>Healthcare platform</span>
        </div>
      </div>

      <div className="auth-doctor-tag">
        <span className="auth-doctor-name">Dr. Nishant</span>
        <span className="auth-doctor-role">General Physician</span>
      </div>

      <main className="auth-card">
        <div className="auth-card-header">
          <span className="eyebrow">
            Secure healthcare access
          </span>

          <h1>Welcome back</h1>

          <p>
            Sign in to access your appointments, medical records,
            prescriptions, documents, and AI Copilot.
          </p>
        </div>

        {error && (
          <div className="auth-error">
            <AlertCircle size={17} />
            <span>{error}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Username

            <div className="input-wrapper">
              <UserRound size={18} />

              <input
                type="text"
                value={username}
                onChange={(event) =>
                  setUsername(event.target.value)
                }
                placeholder="Enter your username"
                autoComplete="username"
                disabled={isSubmitting}
              />
            </div>
          </label>

          <label>
            Password

            <div className="input-wrapper">
              <LockKeyhole size={18} />

              <input
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Enter your password"
                autoComplete="current-password"
                disabled={isSubmitting}
              />
            </div>
          </label>

          <button
            type="submit"
            className="auth-submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="button-spinner" />
                Signing in...
              </>
            ) : (
              <>
                Sign in
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <span>Don&apos;t have an account?</span>
          <Link to="/register">Create an account</Link>
        </div>
      </main>

      <p className="auth-security-note">
        Your healthcare data is protected by authenticated API
        access.
      </p>
    </div>
  )
}
import {
  CheckCircle2,
  LoaderCircle,
  Save,
  UserRound,
} from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import apiClient from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()

  const [firstName, setFirstName] = useState(user?.first_name ?? '')
  const [lastName, setLastName] = useState(user?.last_name ?? '')
  const [email, setEmail] = useState(user?.email ?? '')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    setFirstName(user?.first_name ?? '')
    setLastName(user?.last_name ?? '')
    setEmail(user?.email ?? '')
  }, [user])

  const save = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setMessage('')
    setError('')

    try {
      await apiClient.patch('/auth/me/', {
        first_name: firstName,
        last_name: lastName,
        email,
      })

      await refreshUser()
      setMessage('Profile updated successfully.')
    } catch (requestError) {
      console.error(requestError)
      setError(
        'Unable to update your profile. The backend may require different profile fields.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <div className="eyebrow">Account</div>
          <h1>Profile</h1>
          <p>Manage your personal account information.</p>
        </div>
      </div>

      {error && (
        <div className="alert-card error-alert">
          <UserRound size={19} />
          <span>{error}</span>
        </div>
      )}

      {message && (
        <div className="alert-card success-alert">
          <CheckCircle2 size={19} />
          <span>{message}</span>
        </div>
      )}

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Personal information</span>
            <h2>Account profile</h2>
          </div>
        </div>

        <form className="appointment-form" onSubmit={save}>
          <label className="form-field">
            <span>Username</span>
            <input value={user?.username ?? ''} disabled />
          </label>

          <label className="form-field">
            <span>Role</span>
            <input value={user?.role ?? ''} disabled />
          </label>

          <label className="form-field">
            <span>First name</span>
            <input
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
            />
          </label>

          <label className="form-field">
            <span>Last name</span>
            <input
              value={lastName}
              onChange={(event) => setLastName(event.target.value)}
            />
          </label>

          <label className="form-field form-field-wide">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>

          <div className="form-actions">
            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading ? (
                <LoaderCircle className="spin" size={18} />
              ) : (
                <Save size={18} />
              )}
              Save profile
            </button>
          </div>
        </form>
      </section>
    </section>
  )
}

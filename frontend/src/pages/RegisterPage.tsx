import {
  useState,
  type FormEvent,
} from 'react'
import {
  AlertCircle,
  ArrowRight,
  HeartPulse,
  LockKeyhole,
  Mail,
  Phone,
  UserRound,
} from 'lucide-react'
import {
  Link,
  useNavigate,
} from 'react-router-dom'

import {
  useAuth,
} from '../auth/AuthContext'

interface RegisterForm {
  first_name: string
  last_name: string
  username: string
  email: string
  phone_number: string
  date_of_birth: string
  password: string
  password_confirm: string
}

const initialForm: RegisterForm = {
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  phone_number: '',
  date_of_birth: '',
  password: '',
  password_confirm: '',
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register } = useAuth()

  const [form, setForm] =
    useState<RegisterForm>(initialForm)

  const [error, setError] =
    useState('')

  const [isSubmitting, setIsSubmitting] =
    useState(false)

  const updateField = (
    field: keyof RegisterForm,
    value: string,
  ) => {
    setForm(
      (
        current: RegisterForm,
      ): RegisterForm => ({
        ...current,
        [field]: value,
      }),
    )
  }

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()
    setError('')

    if (
      !form.username.trim() ||
      !form.email.trim() ||
      !form.password ||
      !form.password_confirm ||
      !form.first_name.trim() ||
      !form.last_name.trim()
    ) {
      setError(
        'Please complete all required fields.',
      )
      return
    }

    if (form.password.length < 8) {
      setError(
        'Password must contain at least 8 characters.',
      )
      return
    }

    if (
      form.password !==
      form.password_confirm
    ) {
      setError('Passwords do not match.')
      return
    }

    try {
      setIsSubmitting(true)

      await register({
        ...form,
        username: form.username.trim(),
        email: form.email
          .trim()
          .toLowerCase(),
        first_name:
          form.first_name.trim(),
        last_name:
          form.last_name.trim(),
        phone_number:
          form.phone_number.trim(),
      })

      navigate('/', {
        replace: true,
      })
    } catch (requestError: any) {
      const data =
        requestError?.response?.data

      if (
        data &&
        typeof data === 'object'
      ) {
        const messages =
          Object.entries(data)
            .flatMap(
              ([field, value]) => {
                if (Array.isArray(value)) {
                  return value.map(
                    (item) =>
                      `${field}: ${String(item)}`,
                  )
                }

                return [
                  `${field}: ${String(value)}`,
                ]
              },
            )
            .join(' ')

        setError(
          messages ||
            'Unable to create your account. Please check the form.',
        )
      } else {
        setError(
          'Unable to create your account. Please try again.',
        )
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <div className="auth-brand-mark">
          <HeartPulse
            size={25}
            strokeWidth={2.5}
          />
        </div>

        <div>
          <strong>HealthCopilot</strong>
          <span>Healthcare platform</span>
        </div>
      </div>

      <main className="auth-card auth-register-card">
        <div className="auth-card-header">
          <span className="eyebrow">
            Patient registration
          </span>

          <h1>Create your account</h1>

          <p>
            Create a secure patient account
            to manage your healthcare
            information.
          </p>
        </div>

        {error && (
          <div className="auth-error">
            <AlertCircle size={17} />
            <span>{error}</span>
          </div>
        )}

        <form
          className="auth-form"
          onSubmit={handleSubmit}
        >
          <div className="form-row">
            <label>
              First name

              <div className="input-wrapper">
                <UserRound size={18} />

                <input
                  type="text"
                  value={form.first_name}
                  onChange={(event) =>
                    updateField(
                      'first_name',
                      event.target.value,
                    )
                  }
                  placeholder="John"
                  autoComplete="given-name"
                  disabled={isSubmitting}
                />
              </div>
            </label>

            <label>
              Last name

              <div className="input-wrapper">
                <UserRound size={18} />

                <input
                  type="text"
                  value={form.last_name}
                  onChange={(event) =>
                    updateField(
                      'last_name',
                      event.target.value,
                    )
                  }
                  placeholder="Doe"
                  autoComplete="family-name"
                  disabled={isSubmitting}
                />
              </div>
            </label>
          </div>

          <label>
            Username

            <div className="input-wrapper">
              <UserRound size={18} />

              <input
                type="text"
                value={form.username}
                onChange={(event) =>
                  updateField(
                    'username',
                    event.target.value,
                  )
                }
                placeholder="Choose a username"
                autoComplete="username"
                disabled={isSubmitting}
              />
            </div>
          </label>

          <label>
            Email

            <div className="input-wrapper">
              <Mail size={18} />

              <input
                type="email"
                value={form.email}
                onChange={(event) =>
                  updateField(
                    'email',
                    event.target.value,
                  )
                }
                placeholder="you@example.com"
                autoComplete="email"
                disabled={isSubmitting}
              />
            </div>
          </label>

          <div className="form-row">
            <label>
              Phone number

              <div className="input-wrapper">
                <Phone size={18} />

                <input
                  type="tel"
                  value={form.phone_number}
                  onChange={(event) =>
                    updateField(
                      'phone_number',
                      event.target.value,
                    )
                  }
                  placeholder="+91..."
                  autoComplete="tel"
                  disabled={isSubmitting}
                />
              </div>
            </label>

            <label>
              Date of birth

              <div className="input-wrapper">
                <input
                  type="date"
                  value={
                    form.date_of_birth || ''
                  }
                  onChange={(event) =>
                    updateField(
                      'date_of_birth',
                      event.target.value,
                    )
                  }
                  autoComplete="bday"
                  disabled={isSubmitting}
                />
              </div>
            </label>
          </div>

          <div className="form-row">
            <label>
              Password

              <div className="input-wrapper">
                <LockKeyhole size={18} />

                <input
                  type="password"
                  value={form.password}
                  onChange={(event) =>
                    updateField(
                      'password',
                      event.target.value,
                    )
                  }
                  placeholder="Minimum 8 characters"
                  autoComplete="new-password"
                  disabled={isSubmitting}
                />
              </div>
            </label>

            <label>
              Confirm password

              <div className="input-wrapper">
                <LockKeyhole size={18} />

                <input
                  type="password"
                  value={
                    form.password_confirm
                  }
                  onChange={(event) =>
                    updateField(
                      'password_confirm',
                      event.target.value,
                    )
                  }
                  placeholder="Repeat password"
                  autoComplete="new-password"
                  disabled={isSubmitting}
                />
              </div>
            </label>
          </div>

          <button
            type="submit"
            className="auth-submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="button-spinner" />
                Creating account...
              </>
            ) : (
              <>
                Create account
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <span>
            Already have an account?
          </span>

          <Link to="/login">
            Sign in
          </Link>
        </div>
      </main>
    </div>
  )
}

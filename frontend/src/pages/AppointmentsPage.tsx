import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from 'react'
import {
  CalendarDays,
  CheckCircle2,
  Clock3,
  LoaderCircle,
  Plus,
  RefreshCw,
  Search,
  XCircle,
} from 'lucide-react'

import apiClient from '../api/client'
import { useAuth } from '../auth/AuthContext'

type AppointmentStatus =
  | 'SCHEDULED'
  | 'CONFIRMED'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'NO_SHOW'

type Appointment = {
  id: number
  patient?: number | null
  patient_name?: string | null
  doctor?: number | null
  doctor_name?: string | null
  appointment_date?: string
  date?: string
  time?: string
  reason?: string | null
  notes?: string | null
  status: AppointmentStatus | string
  created_at?: string
  updated_at?: string
}

type ApiListResponse<T> = {
  results?: T[]
  count?: number
  next?: string | null
  previous?: string | null
}

type DoctorOption = {
  id: number
  user?: number
  user_name?: string
  name?: string
  specialty?: string
}

type PatientOption = {
  id: number
  user?: number
  user_name?: string
  name?: string
}

type CreateForm = {
  doctor: string
  patient: string
  appointment_date: string
  time: string
  reason: string
  notes: string
}

type FilterValue = 'upcoming' | 'all' | 'completed' | 'cancelled'

function normalizeList<T>(payload: T[] | ApiListResponse<T>): T[] {
  if (Array.isArray(payload)) {
    return payload
  }

  return payload.results ?? []
}

function getAppointmentDate(appointment: Appointment) {
  return appointment.appointment_date ?? appointment.date ?? ''
}

function getAppointmentTime(appointment: Appointment) {
  return appointment.time ?? ''
}

function formatDate(value: string) {
  if (!value) {
    return 'Date not available'
  }

  const parsed = new Date(value)

  if (Number.isNaN(parsed.getTime())) {
    return value
  }

  return parsed.toLocaleDateString(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

function formatTime(value: string) {
  if (!value) {
    return ''
  }

  const parsed = new Date(`1970-01-01T${value}`)

  if (Number.isNaN(parsed.getTime())) {
    return value
  }

  return parsed.toLocaleTimeString(undefined, {
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatStatus(status: string) {
  return status
    .replaceAll('_', ' ')
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase())
}

function isFutureAppointment(appointment: Appointment) {
  const date = getAppointmentDate(appointment)
  const time = getAppointmentTime(appointment)

  if (!date) {
    return false
  }

  const value = new Date(`${date}T${time || '00:00:00'}`)

  if (Number.isNaN(value.getTime())) {
    return false
  }

  return value.getTime() >= Date.now()
}

export default function AppointmentsPage() {
  const { user } = useAuth()

  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [doctors, setDoctors] = useState<DoctorOption[]>([])
  const [patients, setPatients] = useState<PatientOption[]>([])

  const [filter, setFilter] = useState<FilterValue>('upcoming')
  const [searchTerm, setSearchTerm] = useState('')

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [cancellingId, setCancellingId] = useState<number | null>(null)

  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [showCreateForm, setShowCreateForm] = useState(false)

  const [form, setForm] = useState<CreateForm>({
    doctor: '',
    patient: '',
    appointment_date: '',
    time: '',
    reason: '',
    notes: '',
  })

  const canCreateAppointment =
    user?.role === 'DOCTOR' ||
    user?.role === 'ADMIN' ||
    user?.role === 'PATIENT'

  const loadAppointments = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const response = await apiClient.get<
        Appointment[] | ApiListResponse<Appointment>
      >('/healthcare/appointments/')

      setAppointments(normalizeList(response.data))
    } catch (requestError) {
      console.error(requestError)
      setError(
        'Unable to load appointments. Please check the backend and try again.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  const loadPeople = useCallback(async () => {
    try {
      if (user?.role === 'PATIENT') {
        const response = await apiClient.get<
          DoctorOption[] | ApiListResponse<DoctorOption>
        >('/healthcare/doctors/')

        setDoctors(normalizeList(response.data))
      } else {
        const response = await apiClient.get<
          PatientOption[] | ApiListResponse<PatientOption>
        >('/healthcare/patients/')

        setPatients(normalizeList(response.data))
      }
    } catch (requestError) {
      console.warn('Could not load appointment people:', requestError)
    }
  }, [user?.role])

  useEffect(() => {
    void loadAppointments()
  }, [loadAppointments])

  useEffect(() => {
    void loadPeople()
  }, [loadPeople])

  const filteredAppointments = useMemo(() => {
    const query = searchTerm.trim().toLowerCase()

    return appointments
      .filter((appointment) => {
        if (filter === 'upcoming') {
          return (
            appointment.status !== 'CANCELLED' &&
            appointment.status !== 'COMPLETED' &&
            isFutureAppointment(appointment)
          )
        }

        if (filter === 'completed') {
          return appointment.status === 'COMPLETED'
        }

        if (filter === 'cancelled') {
          return appointment.status === 'CANCELLED'
        }

        return true
      })
      .filter((appointment) => {
        if (!query) {
          return true
        }

        const searchable = [
          appointment.patient_name,
          appointment.doctor_name,
          appointment.reason,
          appointment.notes,
          appointment.status,
          getAppointmentDate(appointment),
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()

        return searchable.includes(query)
      })
      .sort((a, b) => {
        const aValue = `${getAppointmentDate(a)}T${getAppointmentTime(a)}`
        const bValue = `${getAppointmentDate(b)}T${getAppointmentTime(b)}`

        return aValue.localeCompare(bValue)
      })
  }, [appointments, filter, searchTerm])

  const stats = useMemo(() => {
    const upcoming = appointments.filter(
      (appointment) =>
        appointment.status !== 'CANCELLED' &&
        appointment.status !== 'COMPLETED' &&
        isFutureAppointment(appointment),
    ).length

    const completed = appointments.filter(
      (appointment) => appointment.status === 'COMPLETED',
    ).length

    const cancelled = appointments.filter(
      (appointment) => appointment.status === 'CANCELLED',
    ).length

    return {
      total: appointments.length,
      upcoming,
      completed,
      cancelled,
    }
  }, [appointments])

  const handleFormChange = (
    field: keyof CreateForm,
    value: string,
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }))
  }

  const handleCreate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const payload: Record<string, string | number> = {
        appointment_date: form.appointment_date,
        time: form.time,
      }

      if (form.doctor) {
        payload.doctor = Number(form.doctor)
      }

      if (form.patient) {
        payload.patient = Number(form.patient)
      }

      if (form.reason) {
        payload.reason = form.reason
      }

      if (form.notes) {
        payload.notes = form.notes
      }

      await apiClient.post('/healthcare/appointments/', payload)

      setForm({
        doctor: '',
        patient: '',
        appointment_date: '',
        time: '',
        reason: '',
        notes: '',
      })

      setShowCreateForm(false)
      setSuccess('Appointment created successfully.')
      await loadAppointments()
    } catch (requestError) {
      console.error(requestError)
      setError(
        'Unable to create the appointment. Please verify the entered details.',
      )
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = async (appointmentId: number) => {
    const confirmed = window.confirm(
      'Are you sure you want to cancel this appointment?',
    )

    if (!confirmed) {
      return
    }

    setCancellingId(appointmentId)
    setError('')
    setSuccess('')

    try {
      await apiClient.patch(`/healthcare/appointments/${appointmentId}/`, {
        status: 'CANCELLED',
      })

      setSuccess('Appointment cancelled successfully.')
      await loadAppointments()
    } catch (requestError) {
      console.error(requestError)
      setError('Unable to cancel the appointment.')
    } finally {
      setCancellingId(null)
    }
  }

  const getPersonName = (
    appointment: Appointment,
    type: 'patient' | 'doctor',
  ) => {
    if (type === 'patient') {
      return appointment.patient_name || 'Patient'
    }

    return appointment.doctor_name || 'Doctor'
  }

  return (
    <section className="page-section">
      <div className="page-header appointments-page-header">
        <div>
          <div className="eyebrow">Healthcare workspace</div>
          <h1>Appointments</h1>
          <p>
            Schedule, review, and manage healthcare appointments.
          </p>
        </div>

        <div className="page-header-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={() => void loadAppointments()}
            disabled={loading}
          >
            <RefreshCw size={17} />
            Refresh
          </button>

          {canCreateAppointment && (
            <button
              type="button"
              className="primary-button"
              onClick={() => {
                setShowCreateForm((current) => !current)
                setError('')
                setSuccess('')
              }}
            >
              <Plus size={18} />
              New appointment
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="alert-card error-alert">
          <XCircle size={19} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="alert-card success-alert">
          <CheckCircle2 size={19} />
          <span>{success}</span>
        </div>
      )}

      <div className="stats-grid appointments-stats">
        <article className="stat-card">
          <div className="stat-icon">
            <CalendarDays size={22} />
          </div>
          <div className="stat-copy">
            <span>Total</span>
            <strong>{stats.total}</strong>
            <small>All appointments</small>
          </div>
        </article>

        <article className="stat-card">
          <div className="stat-icon">
            <Clock3 size={22} />
          </div>
          <div className="stat-copy">
            <span>Upcoming</span>
            <strong>{stats.upcoming}</strong>
            <small>Future appointments</small>
          </div>
        </article>

        <article className="stat-card">
          <div className="stat-icon">
            <CheckCircle2 size={22} />
          </div>
          <div className="stat-copy">
            <span>Completed</span>
            <strong>{stats.completed}</strong>
            <small>Completed visits</small>
          </div>
        </article>

        <article className="stat-card">
          <div className="stat-icon">
            <XCircle size={22} />
          </div>
          <div className="stat-copy">
            <span>Cancelled</span>
            <strong>{stats.cancelled}</strong>
            <small>Cancelled visits</small>
          </div>
        </article>
      </div>

      {showCreateForm && (
        <section className="panel appointment-form-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Schedule</span>
              <h2>Create appointment</h2>
            </div>
          </div>

          <form className="appointment-form" onSubmit={handleCreate}>
            {user?.role !== 'PATIENT' && (
              <label className="form-field">
                <span>Patient</span>
                <select
                  value={form.patient}
                  onChange={(event) =>
                    handleFormChange('patient', event.target.value)
                  }
                  required
                >
                  <option value="">Select patient</option>
                  {patients.map((patient) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.name ||
                        patient.user_name ||
                        `Patient #${patient.id}`}
                    </option>
                  ))}
                </select>
              </label>
            )}

            {user?.role === 'PATIENT' && (
              <label className="form-field">
                <span>Doctor</span>
                <select
                  value={form.doctor}
                  onChange={(event) =>
                    handleFormChange('doctor', event.target.value)
                  }
                  required
                >
                  <option value="">Select doctor</option>
                  {doctors.map((doctor) => (
                    <option key={doctor.id} value={doctor.id}>
                      {doctor.name ||
                        doctor.user_name ||
                        `Doctor #${doctor.id}`}
                      {doctor.specialty ? ` — ${doctor.specialty}` : ''}
                    </option>
                  ))}
                </select>
              </label>
            )}

            <label className="form-field">
              <span>Date</span>
              <input
                type="date"
                value={form.appointment_date}
                onChange={(event) =>
                  handleFormChange('appointment_date', event.target.value)
                }
                required
              />
            </label>

            <label className="form-field">
              <span>Time</span>
              <input
                type="time"
                value={form.time}
                onChange={(event) =>
                  handleFormChange('time', event.target.value)
                }
                required
              />
            </label>

            <label className="form-field">
              <span>Reason</span>
              <input
                type="text"
                value={form.reason}
                onChange={(event) =>
                  handleFormChange('reason', event.target.value)
                }
                placeholder="e.g. Follow-up consultation"
              />
            </label>

            <label className="form-field form-field-wide">
              <span>Notes</span>
              <textarea
                value={form.notes}
                onChange={(event) =>
                  handleFormChange('notes', event.target.value)
                }
                placeholder="Additional appointment notes..."
                rows={4}
              />
            </label>

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowCreateForm(false)}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="primary-button"
                disabled={saving}
              >
                {saving ? (
                  <>
                    <LoaderCircle className="spin" size={18} />
                    Creating...
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={18} />
                    Create appointment
                  </>
                )}
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="panel">
        <div className="panel-header appointments-toolbar">
          <div>
            <span className="eyebrow">Appointments</span>
            <h2>Appointment list</h2>
          </div>

          <div className="appointments-controls">
            <div className="appointment-search">
              <Search size={17} />
              <input
                type="search"
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Search appointments..."
              />
            </div>

            <select
              className="filter-select"
              value={filter}
              onChange={(event) =>
                setFilter(event.target.value as FilterValue)
              }
            >
              <option value="upcoming">Upcoming</option>
              <option value="all">All</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="state-card">
            <LoaderCircle className="spin" size={28} />
            <strong>Loading appointments...</strong>
            <span>Fetching your latest appointment information.</span>
          </div>
        ) : filteredAppointments.length === 0 ? (
          <div className="state-card">
            <CalendarDays size={30} />
            <strong>No appointments found</strong>
            <span>
              Try changing the filter or search term, or create a new
              appointment.
            </span>
          </div>
        ) : (
          <div className="appointment-table-wrap">
            <table className="data-table appointment-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Patient</th>
                  <th>Doctor</th>
                  <th>Reason</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {filteredAppointments.map((appointment) => (
                  <tr key={appointment.id}>
                    <td>{formatDate(getAppointmentDate(appointment))}</td>
                    <td>
                      {formatTime(getAppointmentTime(appointment)) || '—'}
                    </td>
                    <td>
                      <strong>
                        {getPersonName(appointment, 'patient')}
                      </strong>
                    </td>
                    <td>{getPersonName(appointment, 'doctor')}</td>
                    <td>{appointment.reason || '—'}</td>
                    <td>
                      <span
                        className={`table-status status-${String(
                          appointment.status,
                        )
                          .toLowerCase()
                          .replaceAll('_', '-')}`}
                      >
                        {formatStatus(String(appointment.status))}
                      </span>
                    </td>
                    <td>
                      {appointment.status !== 'CANCELLED' &&
                        appointment.status !== 'COMPLETED' && (
                          <button
                            type="button"
                            className="table-action danger-action"
                            onClick={() =>
                              void handleCancel(appointment.id)
                            }
                            disabled={cancellingId === appointment.id}
                          >
                            {cancellingId === appointment.id ? (
                              <LoaderCircle className="spin" size={16} />
                            ) : (
                              <XCircle size={16} />
                            )}
                            Cancel
                          </button>
                        )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  )
}

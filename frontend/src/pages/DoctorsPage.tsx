import { useEffect, useState } from 'react'
import { Stethoscope, Search, AlertCircle, Loader2 } from 'lucide-react'

import apiClient from '../api/client'

type Doctor = Record<string, unknown>

function getDisplayValue(
  doctor: Doctor,
  keys: string[],
  fallback = '—',
): string {
  for (const key of keys) {
    const value = doctor[key]

    if (value !== undefined && value !== null && String(value).trim()) {
      return String(value)
    }
  }

  return fallback
}

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function loadDoctors() {
    setLoading(true)
    setError('')

    try {
      const response = await apiClient.get('/healthcare/doctors/')
      const data = response.data

      if (Array.isArray(data)) {
        setDoctors(data)
      } else if (Array.isArray(data?.results)) {
        setDoctors(data.results)
      } else {
        setDoctors([])
      }
    } catch (requestError: unknown) {
      let message = 'Unable to load doctors.'

      if (
        typeof requestError === 'object' &&
        requestError !== null &&
        'response' in requestError
      ) {
        const response = (
          requestError as {
            response?: {
              data?: {
                detail?: string
              }
            }
          }
        ).response

        message = response?.data?.detail ?? message
      }

      setError(message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadDoctors()
  }, [])

  const filteredDoctors = doctors.filter((doctor) => {
    const text = JSON.stringify(doctor).toLowerCase()
    return text.includes(search.toLowerCase())
  })

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <h1>Doctors</h1>
          <p>View doctors available in the healthcare system.</p>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <h2>
              <Stethoscope size={20} />
              Doctor Directory
            </h2>
            <p>{doctors.length} doctor(s) available</p>
          </div>

          <div className="search-box">
            <Search size={17} />
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search doctors..."
              aria-label="Search doctors"
            />
          </div>
        </div>

        {loading && (
          <div className="loading-state">
            <Loader2 size={22} className="spin" />
            <span>Loading doctors...</span>
          </div>
        )}

        {!loading && error && (
          <div className="error-state" role="alert">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {!loading && !error && filteredDoctors.length === 0 && (
          <div className="empty-state">
            <Stethoscope size={32} />
            <h3>No doctors found</h3>
            <p>There are no doctors matching your search.</p>
          </div>
        )}

        {!loading && !error && filteredDoctors.length > 0 && (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Doctor</th>
                  <th>Specialization</th>
                  <th>License</th>
                  <th>Organization</th>
                </tr>
              </thead>

              <tbody>
                {filteredDoctors.map((doctor, index) => (
                  <tr key={String(doctor.id ?? index)}>
                    <td>
                      <strong>
                        {getDisplayValue(doctor, [
                          'full_name',
                          'name',
                          'doctor_name',
                          'username',
                        ])}
                      </strong>
                    </td>

                    <td>
                      {getDisplayValue(doctor, [
                        'specialization',
                        'speciality',
                        'department',
                      ])}
                    </td>

                    <td>
                      {getDisplayValue(doctor, [
                        'license_number',
                        'license',
                        'medical_license',
                      ])}
                    </td>

                    <td>
                      {getDisplayValue(doctor, [
                        'organization',
                        'organization_name',
                        'hospital',
                      ])}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="panel-footer">
          Doctor creation is restricted to authorized administrator users.
        </div>
      </div>
    </section>
  )
}

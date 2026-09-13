import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
  type ReactNode,
} from 'react'
import {
  AlertCircle,
  CheckCircle2,
  LoaderCircle,
  Plus,
  RefreshCw,
  Search,
  X,
} from 'lucide-react'

import apiClient from '../api/client'

export type ResourceRecord = Record<string, unknown>

type ResourcePageProps = {
  title: string
  description: string
  endpoint: string
  icon: ReactNode
  searchFields: string[]
  columns: Array<{
    key: string
    label: string
  }>
  createFields?: Array<{
    key: string
    label: string
    type?: 'text' | 'date' | 'datetime-local' | 'textarea' | 'select'
    required?: boolean
    options?: Array<{
      value: string
      label: string
    }>
  }>
  createPayload?: (values: Record<string, string>) => Record<string, unknown>
  formatValue?: (value: unknown, key: string, row: ResourceRecord) => string
  canCreate?: boolean
}

function normalizeList(payload: unknown): ResourceRecord[] {
  if (Array.isArray(payload)) {
    return payload as ResourceRecord[]
  }

  if (
    payload &&
    typeof payload === 'object' &&
    Array.isArray((payload as { results?: unknown[] }).results)
  ) {
    return (payload as { results: ResourceRecord[] }).results
  }

  return []
}

function valueToText(value: unknown): string {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  if (typeof value === 'object') {
    const object = value as Record<string, unknown>

    return String(
      object.name ??
        object.full_name ??
        object.username ??
        object.title ??
        object.id ??
        JSON.stringify(value),
    )
  }

  return String(value)
}

export default function ResourcePage({
  title,
  description,
  endpoint,
  icon,
  searchFields,
  columns,
  createFields = [],
  createPayload,
  formatValue,
  canCreate = true,
}: ResourcePageProps) {
  const [rows, setRows] = useState<ResourceRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [search, setSearch] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [selected, setSelected] = useState<ResourceRecord | null>(null)

  const [values, setValues] = useState<Record<string, string>>({})

  const load = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const response = await apiClient.get(endpoint)
      setRows(normalizeList(response.data))
    } catch (requestError) {
      console.error(requestError)
      setError(`Unable to load ${title.toLowerCase()}.`)
    } finally {
      setLoading(false)
    }
  }, [endpoint, title])

  useEffect(() => {
    void load()
  }, [load])

  const filteredRows = useMemo(() => {
    const query = search.trim().toLowerCase()

    if (!query) {
      return rows
    }

    return rows.filter((row) =>
      searchFields.some((field) =>
        valueToText(row[field]).toLowerCase().includes(query),
      ),
    )
  }, [rows, search, searchFields])

  const openCreate = () => {
    const initial: Record<string, string> = {}

    for (const field of createFields) {
      initial[field.key] = ''
    }

    setValues(initial)
    setError('')
    setSuccess('')
    setShowCreate(true)
  }

  const handleCreate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const payload = createPayload ? createPayload(values) : values

      await apiClient.post(endpoint, payload)

      setSuccess(`${title.slice(0, -1) || title} created successfully.`)
      setShowCreate(false)
      await load()
    } catch (requestError) {
      console.error(requestError)
      setError(`Unable to create ${title.toLowerCase().slice(0, -1)}.`)
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <div className="eyebrow">Healthcare workspace</div>
          <h1>{title}</h1>
          <p>{description}</p>
        </div>

        <div className="page-header-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={() => void load()}
            disabled={loading}
          >
            <RefreshCw size={17} />
            Refresh
          </button>

          {canCreate && createFields.length > 0 && (
            <button
              type="button"
              className="primary-button"
              onClick={openCreate}
            >
              <Plus size={18} />
              New
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="alert-card error-alert">
          <AlertCircle size={19} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="alert-card success-alert">
          <CheckCircle2 size={19} />
          <span>{success}</span>
        </div>
      )}

      {showCreate && (
        <section className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Create</span>
              <h2>New {title.replace(/s$/, '')}</h2>
            </div>

            <button
              type="button"
              className="icon-button"
              aria-label="Close"
              onClick={() => setShowCreate(false)}
            >
              <X size={19} />
            </button>
          </div>

          <form className="appointment-form" onSubmit={handleCreate}>
            {createFields.map((field) => (
              <label
                className={`form-field ${
                  field.type === 'textarea' ? 'form-field-wide' : ''
                }`}
                key={field.key}
              >
                <span>{field.label}</span>

                {field.type === 'textarea' ? (
                  <textarea
                    rows={4}
                    value={values[field.key] ?? ''}
                    required={field.required}
                    onChange={(event) =>
                      setValues((current) => ({
                        ...current,
                        [field.key]: event.target.value,
                      }))
                    }
                  />
                ) : field.type === 'select' ? (
                  <select
                    value={values[field.key] ?? ''}
                    required={field.required}
                    onChange={(event) =>
                      setValues((current) => ({
                        ...current,
                        [field.key]: event.target.value,
                      }))
                    }
                  >
                    <option value="">Select {field.label}</option>
                    {(field.options ?? []).map((option) => (
                      <option value={option.value} key={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={field.type ?? 'text'}
                    value={values[field.key] ?? ''}
                    required={field.required}
                    onChange={(event) =>
                      setValues((current) => ({
                        ...current,
                        [field.key]: event.target.value,
                      }))
                    }
                  />
                )}
              </label>
            ))}

            <div className="form-actions">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setShowCreate(false)}
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
                    Saving...
                  </>
                ) : (
                  <>
                    <CheckCircle2 size={18} />
                    Save
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
            <span className="eyebrow">Records</span>
            <h2>{title} list</h2>
          </div>

          <div className="appointments-controls">
            <div className="appointment-search">
              <Search size={17} />
              <input
                type="search"
                placeholder={`Search ${title.toLowerCase()}...`}
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </div>
          </div>
        </div>

        {loading ? (
          <div className="state-card">
            <LoaderCircle className="spin" size={28} />
            <strong>Loading {title.toLowerCase()}...</strong>
            <span>Fetching the latest healthcare information.</span>
          </div>
        ) : filteredRows.length === 0 ? (
          <div className="state-card">
            {icon}
            <strong>No {title.toLowerCase()} found</strong>
            <span>
              There are no matching records available for this account.
            </span>
          </div>
        ) : (
          <div className="appointment-table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  {columns.map((column) => (
                    <th key={column.key}>{column.label}</th>
                  ))}
                  <th>View</th>
                </tr>
              </thead>

              <tbody>
                {filteredRows.map((row, index) => (
                  <tr
                    key={
                      String(row.id ?? row.pk ?? `${title}-${index}`)
                    }
                  >
                    {columns.map((column) => (
                      <td key={column.key}>
                        {formatValue
                          ? formatValue(row[column.key], column.key, row)
                          : valueToText(row[column.key])}
                      </td>
                    ))}

                    <td>
                      <button
                        type="button"
                        className="table-action"
                        onClick={() => setSelected(row)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selected && (
        <section className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Details</span>
              <h2>Record details</h2>
            </div>

            <button
              type="button"
              className="icon-button"
              aria-label="Close details"
              onClick={() => setSelected(null)}
            >
              <X size={19} />
            </button>
          </div>

          <div className="detail-grid">
            {Object.entries(selected).map(([key, value]) => (
              <div className="detail-item" key={key}>
                <span>{key.replaceAll('_', ' ')}</span>
                <strong>{valueToText(value)}</strong>
              </div>
            ))}
          </div>
        </section>
      )}
    </section>
  )
}

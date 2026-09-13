import {
  FileText,
  LoaderCircle,
  Upload,
  RefreshCw,
} from 'lucide-react'
import {
  useCallback,
  useEffect,
  useState,
  type ChangeEvent,
} from 'react'
import apiClient from '../api/client'

type DocumentRecord = {
  id: number
  title?: string
  name?: string
  filename?: string
  file?: string
  status?: string
  processing_status?: string
  extraction_status?: string
  uploaded_at?: string
  created_at?: string
  document_type?: string
}

function normalize(payload: unknown): DocumentRecord[] {
  if (Array.isArray(payload)) {
    return payload as DocumentRecord[]
  }

  if (
    payload &&
    typeof payload === 'object' &&
    Array.isArray((payload as { results?: unknown[] }).results)
  ) {
    return (payload as { results: DocumentRecord[] }).results
  }

  return []
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const loadDocuments = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      const response = await apiClient.get('/documents/')
      setDocuments(normalize(response.data))
    } catch (requestError) {
      console.error(requestError)
      setError('Unable to load documents.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadDocuments()
  }, [loadDocuments])

  const handleUpload = async (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0]

    if (!file) {
      return
    }

    setUploading(true)
    setError('')
    setSuccess('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', file.name)

      await apiClient.post('/documents/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setSuccess('Document uploaded successfully.')
      await loadDocuments()
    } catch (requestError) {
      console.error(requestError)
      setError(
        'Document upload failed. Please verify the file type and backend document endpoint.',
      )
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <div className="eyebrow">Knowledge base</div>
          <h1>Documents</h1>
          <p>
            Upload healthcare documents and track extraction and processing.
          </p>
        </div>

        <div className="page-header-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={() => void loadDocuments()}
            disabled={loading}
          >
            <RefreshCw size={17} />
            Refresh
          </button>

          <label className="primary-button">
            {uploading ? (
              <LoaderCircle className="spin" size={18} />
            ) : (
              <Upload size={18} />
            )}
            {uploading ? 'Uploading...' : 'Upload document'}
            <input
              type="file"
              hidden
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>
        </div>
      </div>

      {error && (
        <div className="alert-card error-alert">
          <FileText size={19} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="alert-card success-alert">
          <FileText size={19} />
          <span>{success}</span>
        </div>
      )}

      {loading ? (
        <div className="state-card">
          <LoaderCircle className="spin" size={30} />
          <strong>Loading documents...</strong>
          <span>Fetching your document library.</span>
        </div>
      ) : documents.length === 0 ? (
        <div className="state-card">
          <FileText size={32} />
          <strong>No documents yet</strong>
          <span>Upload a PDF, DOCX, or text document to begin.</span>
        </div>
      ) : (
        <div className="stats-grid">
          {documents.map((document) => (
            <article className="stat-card" key={document.id}>
              <div className="stat-icon">
                <FileText size={22} />
              </div>
              <div className="stat-copy">
                <span>
                  {document.document_type ?? 'Healthcare document'}
                </span>
                <strong>
                  {document.title ??
                    document.name ??
                    document.filename ??
                    `Document #${document.id}`}
                </strong>
                <small>
                  {document.status ??
                    document.processing_status ??
                    document.extraction_status ??
                    'Uploaded'}
                </small>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}

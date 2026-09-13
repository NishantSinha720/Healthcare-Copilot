import { ShieldCheck } from 'lucide-react'
import ResourcePage from './ResourcePage'

export default function AuditPage() {
  return (
    <ResourcePage
      title="Audit Logs"
      description="Review security, authentication, healthcare, and AI activity."
      endpoint="/audit/"
      icon={<ShieldCheck size={30} />}
      searchFields={[
        'action',
        'event_type',
        'username',
        'user',
        'ip_address',
        'path',
        'method',
        'description',
      ]}
      columns={[
        { key: 'id', label: 'ID' },
        { key: 'action', label: 'Action' },
        { key: 'event_type', label: 'Event' },
        { key: 'username', label: 'User' },
        { key: 'method', label: 'Method' },
        { key: 'created_at', label: 'Created' },
      ]}
      canCreate={false}
    />
  )
}

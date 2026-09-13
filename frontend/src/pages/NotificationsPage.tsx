import { Bell } from 'lucide-react'
import ResourcePage from './ResourcePage'

export default function NotificationsPage() {
  return (
    <ResourcePage
      title="Notifications"
      description="View healthcare, system, appointment, and real-time notifications."
      endpoint="/notifications/"
      icon={<Bell size={30} />}
      searchFields={[
        'title',
        'message',
        'notification_type',
        'type',
        'status',
      ]}
      columns={[
        { key: 'id', label: 'ID' },
        { key: 'title', label: 'Title' },
        { key: 'message', label: 'Message' },
        { key: 'notification_type', label: 'Type' },
        { key: 'created_at', label: 'Created' },
        { key: 'is_read', label: 'Read' },
      ]}
      canCreate={false}
    />
  )
}

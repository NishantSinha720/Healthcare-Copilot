import { Users } from 'lucide-react'
import ResourcePage from './ResourcePage'

export default function PatientsPage() {
  return (
    <ResourcePage
      title="Patients"
      description="Manage patient profiles and healthcare relationships."
      endpoint="/healthcare/patients/"
      icon={<Users size={30} />}
      searchFields={[
        'name',
        'full_name',
        'user_name',
        'username',
        'email',
        'phone',
        'date_of_birth',
      ]}
      columns={[
        { key: 'id', label: 'ID' },
        { key: 'name', label: 'Name' },
        { key: 'user_name', label: 'Username' },
        { key: 'email', label: 'Email' },
        { key: 'phone', label: 'Phone' },
        { key: 'date_of_birth', label: 'DOB' },
      ]}
      createFields={[
        {
          key: 'user',
          label: 'User ID',
          type: 'text',
          required: true,
        },
        {
          key: 'phone',
          label: 'Phone',
          type: 'text',
        },
        {
          key: 'date_of_birth',
          label: 'Date of Birth',
          type: 'date',
        },
      ]}
      createPayload={(values) => ({
        ...values,
        user: Number(values.user),
      })}
    />
  )
}

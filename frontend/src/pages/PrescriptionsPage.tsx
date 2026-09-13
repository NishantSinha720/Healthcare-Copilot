import { Pill } from 'lucide-react'
import ResourcePage from './ResourcePage'

export default function PrescriptionsPage() {
  return (
    <ResourcePage
      title="Prescriptions"
      description="Review medications, dosage instructions, prescription status, and prescribing activity."
      endpoint="/healthcare/prescriptions/"
      icon={<Pill size={30} />}
      searchFields={[
        'patient_name',
        'doctor_name',
        'medication',
        'medicine',
        'name',
        'dosage',
        'instructions',
        'status',
      ]}
      columns={[
        { key: 'id', label: 'ID' },
        { key: 'patient_name', label: 'Patient' },
        { key: 'doctor_name', label: 'Doctor' },
        { key: 'medication', label: 'Medication' },
        { key: 'dosage', label: 'Dosage' },
        { key: 'status', label: 'Status' },
      ]}
      createFields={[
        {
          key: 'patient',
          label: 'Patient ID',
          type: 'text',
          required: true,
        },
        {
          key: 'medication',
          label: 'Medication',
          type: 'text',
          required: true,
        },
        {
          key: 'dosage',
          label: 'Dosage',
          type: 'text',
          required: true,
        },
        {
          key: 'instructions',
          label: 'Instructions',
          type: 'textarea',
        },
      ]}
      createPayload={(values) => ({
        ...values,
        patient: Number(values.patient),
      })}
    />
  )
}

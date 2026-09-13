import { ClipboardList } from 'lucide-react'
import ResourcePage from './ResourcePage'

export default function MedicalRecordsPage() {
  return (
    <ResourcePage
      title="Medical Records"
      description="Review diagnoses, clinical notes, treatments, and patient medical history."
      endpoint="/healthcare/medical-records/"
      icon={<ClipboardList size={30} />}
      searchFields={[
        'patient_name',
        'doctor_name',
        'diagnosis',
        'symptoms',
        'treatment',
        'notes',
        'record_type',
      ]}
      columns={[
        { key: 'id', label: 'ID' },
        { key: 'patient_name', label: 'Patient' },
        { key: 'doctor_name', label: 'Doctor' },
        { key: 'record_type', label: 'Type' },
        { key: 'diagnosis', label: 'Diagnosis' },
        { key: 'created_at', label: 'Created' },
      ]}
      createFields={[
        {
          key: 'patient',
          label: 'Patient ID',
          type: 'text',
          required: true,
        },
        {
          key: 'record_type',
          label: 'Record Type',
          type: 'text',
          required: true,
        },
        {
          key: 'diagnosis',
          label: 'Diagnosis',
          type: 'text',
          required: true,
        },
        {
          key: 'symptoms',
          label: 'Symptoms',
          type: 'textarea',
        },
        {
          key: 'treatment',
          label: 'Treatment',
          type: 'textarea',
        },
        {
          key: 'notes',
          label: 'Notes',
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

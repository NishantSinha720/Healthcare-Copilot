import { Bell, CheckCircle2, Settings } from 'lucide-react'
import { useState } from 'react'

export default function SettingsPage() {
  const [notifications, setNotifications] = useState(true)
  const [emailUpdates, setEmailUpdates] = useState(true)
  const [compactMode, setCompactMode] = useState(false)
  const [saved, setSaved] = useState(false)

  const save = () => {
    localStorage.setItem(
      'healthcare_copilot_settings',
      JSON.stringify({
        notifications,
        emailUpdates,
        compactMode,
      }),
    )

    setSaved(true)
    window.setTimeout(() => setSaved(false), 2500)
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <div className="eyebrow">Application</div>
          <h1>Settings</h1>
          <p>Configure account and application preferences.</p>
        </div>
      </div>

      {saved && (
        <div className="alert-card success-alert">
          <CheckCircle2 size={19} />
          <span>Settings saved.</span>
        </div>
      )}

      <section className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Preferences</span>
            <h2>Notification settings</h2>
          </div>
        </div>

        <div className="settings-list">
          <label className="settings-row">
            <div>
              <strong>
                <Bell size={18} />
                In-app notifications
              </strong>
              <span>Receive healthcare and system notifications.</span>
            </div>

            <input
              type="checkbox"
              checked={notifications}
              onChange={(event) => setNotifications(event.target.checked)}
            />
          </label>

          <label className="settings-row">
            <div>
              <strong>
                <Bell size={18} />
                Email updates
              </strong>
              <span>Receive important account updates by email.</span>
            </div>

            <input
              type="checkbox"
              checked={emailUpdates}
              onChange={(event) => setEmailUpdates(event.target.checked)}
            />
          </label>

          <label className="settings-row">
            <div>
              <strong>
                <Settings size={18} />
                Compact interface
              </strong>
              <span>Use a denser layout for healthcare data tables.</span>
            </div>

            <input
              type="checkbox"
              checked={compactMode}
              onChange={(event) => setCompactMode(event.target.checked)}
            />
          </label>
        </div>

        <div className="form-actions">
          <button type="button" className="primary-button" onClick={save}>
            <CheckCircle2 size={18} />
            Save settings
          </button>
        </div>
      </section>
    </section>
  )
}

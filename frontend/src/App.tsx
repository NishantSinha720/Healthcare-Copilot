import { useEffect, useMemo, useState, type ReactNode } from 'react'
import {
Bell,
  CalendarDays,
  ChevronDown,
  ClipboardList,
  FileText,
  HeartPulse,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageSquareText,
  Pill,
  Search,
  Settings,
  ShieldCheck,
  Stethoscope,
  UserRound,
  Users,
  X,
} from 'lucide-react'
import { NavLink, Outlet, Route, Routes } from 'react-router-dom'

import doctorPhoto from './assets/doctor-profile.jpeg'
import { useAuth } from './auth/AuthContext'
import ProtectedRoute from './auth/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import AppointmentsPage from './pages/AppointmentsPage'
import MedicalRecordsPage from './pages/MedicalRecordsPage'
import PrescriptionsPage from './pages/PrescriptionsPage'
import DocumentsPage from './pages/DocumentsPage'
import AICopilotPage from './pages/AICopilotPage'
import PatientsPage from './pages/PatientsPage'
import DoctorsPage from './pages/DoctorsPage'
import AuditPage from './pages/AuditPage'
import NotificationsPage from './pages/NotificationsPage'
import ProfilePage from './pages/ProfilePage'
import SettingsPage from './pages/SettingsPage'

type NavItem = {
  label: string
  path: string
  icon: ReactNode
}

function DashboardHome() {
  const { user } = useAuth()

  const displayName = user?.first_name?.trim()
    ? `${user.first_name} ${user.last_name ?? ''}`.trim()
    : user?.username ?? 'Doctor'

  const stats = [
    {
      label: 'Appointments',
      value: '24',
      detail: '+12% this month',
      icon: <CalendarDays size={22} />,
    },
    {
      label: 'Patients',
      value: '128',
      detail: '+8 new this week',
      icon: <Users size={22} />,
    },
    {
      label: 'Medical Records',
      value: '342',
      detail: '18 updated today',
      icon: <ClipboardList size={22} />,
    },
    {
      label: 'Prescriptions',
      value: '67',
      detail: '5 pending review',
      icon: <Pill size={22} />,
    },
  ]

  return (
    <section className="dashboard-home">
      <div className="welcome-section">
        <div>
          <div className="eyebrow">Healthcare Copilot</div>
          <h1>Good morning, {displayName.split(' ')[0]}.</h1>
          <p>
            Here&apos;s what&apos;s happening with your healthcare workspace
            today.
          </p>
        </div>

        <div className="welcome-profile">
          <div className="avatar avatar-photo">
            <img src={doctorPhoto} alt="Doctor profile" />
          </div>
          <div>
            <strong>{displayName}</strong>
            <span>{user?.role ?? 'USER'}</span>
          </div>
        </div>
      </div>

      <div className="doctor-highlight">
        <div className="doctor-highlight-photo">
          <img src={doctorPhoto} alt="Doctor profile" />
        </div>

        <div className="doctor-highlight-content">
          <div className="eyebrow">Healthcare Copilot</div>
          <h2>{displayName}</h2>
          <p>
            Manage appointments, records, prescriptions, documents, patients,
            doctors, notifications, and grounded AI assistance from one secure
            workspace.
          </p>

          <div className="doctor-highlight-meta">
            <span>
              <HeartPulse size={16} />
              Healthcare workspace
            </span>
            <span>
              <ShieldCheck size={16} />
              Authenticated
            </span>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        {stats.map((stat) => (
          <article className="stat-card" key={stat.label}>
            <div className="stat-icon">{stat.icon}</div>
            <div className="stat-copy">
              <span>{stat.label}</span>
              <strong>{stat.value}</strong>
              <small>{stat.detail}</small>
            </div>
          </article>
        ))}
      </div>

      <div className="dashboard-grid">
        <section className="panel appointments-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Workspace</span>
              <h2>Healthcare modules</h2>
            </div>
          </div>

          <div className="quick-actions">
            <NavLink to="/appointments" className="quick-action">
              <CalendarDays size={20} />
              <span>Appointments</span>
            </NavLink>

            <NavLink to="/records" className="quick-action">
              <ClipboardList size={20} />
              <span>Medical records</span>
            </NavLink>

            <NavLink to="/prescriptions" className="quick-action">
              <Pill size={20} />
              <span>Prescriptions</span>
            </NavLink>

            <NavLink to="/documents" className="quick-action">
              <FileText size={20} />
              <span>Documents</span>
            </NavLink>
          </div>
        </section>

        <section className="panel ai-panel">
          <div className="ai-panel-icon">
            <MessageSquareText size={24} />
          </div>
          <span className="eyebrow">AI Copilot</span>
          <h2>Grounded healthcare assistance</h2>
          <p>
            Ask questions using your connected healthcare information.
          </p>
          <NavLink className="primary-button" to="/ai">
            Open AI Copilot
          </NavLink>
        </section>
      </div>

      <div className="dashboard-grid">
        <section className="panel activity-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Security</span>
              <h2>Protected workspace</h2>
            </div>
          </div>

          <div className="activity-list">
            <div className="activity-row">
              <div className="activity-icon">
                <ShieldCheck size={18} />
              </div>
              <div>
                <strong>JWT authentication enabled</strong>
                <span>Authenticated API requests use access tokens.</span>
              </div>
            </div>

            <div className="activity-row">
              <div className="activity-icon">
                <HeartPulse size={18} />
              </div>
              <div>
                <strong>Healthcare data connected</strong>
                <span>
                  Clinical modules are connected to the Django backend.
                </span>
              </div>
            </div>

            <div className="activity-row">
              <div className="activity-icon">
                <MessageSquareText size={18} />
              </div>
              <div>
                <strong>AI assistance available</strong>
                <span>Use the AI Copilot for grounded healthcare questions.</span>
              </div>
            </div>
          </div>
        </section>

        <section className="panel quick-actions-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Management</span>
              <h2>People & security</h2>
            </div>
          </div>

          <div className="quick-actions">
            <NavLink to="/patients" className="quick-action">
              <Users size={20} />
              <span>Patients</span>
            </NavLink>

            <NavLink to="/doctors" className="quick-action">
              <Stethoscope size={20} />
              <span>Doctors</span>
            </NavLink>

            <NavLink to="/audit" className="quick-action">
              <ShieldCheck size={20} />
              <span>Audit logs</span>
            </NavLink>

            <NavLink to="/notifications" className="quick-action">
              <Bell size={20} />
              <span>Notifications</span>
            </NavLink>
          </div>
        </section>
      </div>
    </section>
  )
}

function DashboardLayout() {
  const { user, logout } = useAuth()

  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)

  const displayName = useMemo(() => {
    if (!user) {
      return 'User'
    }

    if (user.first_name?.trim()) {
      return `${user.first_name} ${user.last_name ?? ''}`.trim()
    }

    return user.username
  }, [user])

  const navItems: NavItem[] = [
    {
      label: 'Dashboard',
      path: '/',
      icon: <LayoutDashboard size={19} />,
    },
    {
      label: 'Appointments',
      path: '/appointments',
      icon: <CalendarDays size={19} />,
    },
    {
      label: 'Medical Records',
      path: '/records',
      icon: <ClipboardList size={19} />,
    },
    {
      label: 'Prescriptions',
      path: '/prescriptions',
      icon: <Pill size={19} />,
    },
    {
      label: 'Documents',
      path: '/documents',
      icon: <FileText size={19} />,
    },
    {
      label: 'AI Copilot',
      path: '/ai',
      icon: <MessageSquareText size={19} />,
    },
    {
      label: 'Patients',
      path: '/patients',
      icon: <Users size={19} />,
    },
    {
      label: 'Doctors',
      path: '/doctors',
      icon: <Stethoscope size={19} />,
    },
    {
      label: 'Audit Logs',
      path: '/audit',
      icon: <ShieldCheck size={19} />,
    },
  ]

  const secondaryItems: NavItem[] = [
    {
      label: 'Notifications',
      path: '/notifications',
      icon: <Bell size={19} />,
    },
    {
      label: 'Profile',
      path: '/profile',
      icon: <UserRound size={19} />,
    },
    {
      label: 'Settings',
      path: '/settings',
      icon: <Settings size={19} />,
    },
  ]

  useEffect(() => {
    const closeSidebar = () => {
      if (window.innerWidth > 900) {
        setSidebarOpen(false)
      }
    }

    window.addEventListener('resize', closeSidebar)

    return () => {
      window.removeEventListener('resize', closeSidebar)
    }
  }, [])

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          type="button"
          className="mobile-overlay"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-mark">
            <HeartPulse size={23} />
          </div>
          <div>
            <strong>HealthCare</strong>
            <span>Copilot</span>
          </div>

          <button
            type="button"
            className="sidebar-close"
            aria-label="Close navigation"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-user">
          <div className="avatar avatar-photo">
            <img src={doctorPhoto} alt="Doctor profile" />
          </div>
          <div>
            <strong>{displayName}</strong>
            <span>{user?.role ?? 'USER'}</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-label">Workspace</div>

          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `nav-item ${isActive ? 'active' : ''}`
              }
              onClick={() => setSidebarOpen(false)}
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}

          <div className="nav-label nav-label-secondary">Account</div>

          {secondaryItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `nav-item ${isActive ? 'active' : ''}`
              }
              onClick={() => setSidebarOpen(false)}
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button
            type="button"
            className="logout-button"
            onClick={() => logout()}
          >
            <LogOut size={19} />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button
              type="button"
              className="mobile-menu-button"
              aria-label="Open navigation"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={21} />
            </button>

            <button
              type="button"
              className="search-trigger"
              onClick={() => setSearchOpen((current) => !current)}
            >
              <Search size={19} />
              <span>Search healthcare data...</span>
            </button>
          </div>

          <div className="topbar-actions">
            <NavLink
              to="/notifications"
              className="icon-button"
              aria-label="Notifications"
            >
              <Bell size={20} />
              <span className="notification-badge">3</span>
            </NavLink>

            <div className="topbar-profile">
              <div className="avatar avatar-photo">
                <img src={doctorPhoto} alt="Doctor profile" />
              </div>

              <div className="topbar-profile-copy">
                <strong>{displayName}</strong>
                <span>{user?.role ?? 'USER'}</span>
              </div>

              <ChevronDown size={17} />
            </div>
          </div>
        </header>

        {searchOpen && (
          <div className="search-panel">
            <Search size={18} />
            <input
              type="search"
              placeholder="Search patients, records, documents..."
              autoFocus
            />
          </div>
        )}

        <div className="content-area">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/*" element={<DashboardLayout />}>
          <Route index element={<DashboardHome />} />

          <Route path="appointments" element={<AppointmentsPage />} />

          <Route path="records" element={<MedicalRecordsPage />} />

          <Route path="prescriptions" element={<PrescriptionsPage />} />

          <Route path="documents" element={<DocumentsPage />} />

          <Route path="ai" element={<AICopilotPage />} />

          <Route path="patients" element={<PatientsPage />} />

          <Route path="doctors" element={<DoctorsPage />} />

          <Route path="audit" element={<AuditPage />} />

          <Route
            path="notifications"
            element={<NotificationsPage />}
          />

          <Route path="profile" element={<ProfilePage />} />

          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Route>
    </Routes>
  )
}



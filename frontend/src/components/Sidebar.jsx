import { Activity, BarChart3, Camera, House, ScanLine } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Home', icon: House, end: true },
  { to: '/image-detection', label: 'Image detection', icon: ScanLine },
  { to: '/video-detection', label: 'Video detection', icon: Camera },
  { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <NavLink className="brand" to="/">
        <span className="brand-mark"><Activity size={19} /></span>
        <span>CrowdVision<span className="brand-accent">AI</span></span>
      </NavLink>
      <div className="nav-caption">WORKSPACE</div>
      <nav className="side-nav" aria-label="Main navigation">
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <span className="status-dot" />
        <span>Local processing</span>
      </div>
    </aside>
  )
}

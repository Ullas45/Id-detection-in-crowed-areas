import { Activity, Bell } from 'lucide-react'

export default function Navbar() {
  return (
    <header className="topbar">
      <div className="mobile-brand">
        <span className="brand-mark"><Activity size={18} /></span>
        <span>CrowdVision<span className="brand-accent">AI</span></span>
      </div>
      <div className="topbar-status"><span className="status-dot" /> Vision workspace</div>
      <button className="icon-button" type="button" aria-label="Notifications">
        <Bell size={18} />
      </button>
    </header>
  )
}

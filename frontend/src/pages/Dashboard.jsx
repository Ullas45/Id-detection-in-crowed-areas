import { BarChart3, CircleHelp } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="page-stack">
      <div className="page-heading">
        <span className="feature-icon"><BarChart3 size={20} /></span>
        <div><div className="eyebrow">OVERVIEW</div><h1>Dashboard</h1></div>
      </div>
      <section className="empty-state">
        <span className="empty-icon"><CircleHelp size={24} /></span>
        <h2>No analysis history yet</h2>
        <p>Completed processing jobs will appear here when analysis history is available.</p>
      </section>
    </div>
  )
}

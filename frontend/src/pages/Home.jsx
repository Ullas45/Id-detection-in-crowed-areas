import { ArrowRight, Camera, ScanLine, ShieldCheck, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'

const features = [
  { icon: ScanLine, title: 'Image detection', text: 'Inspect image-based crowd scenes and identify people.' },
  { icon: Camera, title: 'Video detection', text: 'Process uploaded videos and track detections frame by frame.' },
  { icon: ShieldCheck, title: 'Local processing', text: 'Your media is processed by your local backend service.' },
]

export default function Home() {
  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div className="hero-copy">
          <div className="eyebrow"><Zap size={14} /> COMPUTER VISION WORKSPACE</div>
          <h1>Understand the crowd.<br /><span>See the bigger picture.</span></h1>
          <p>Analyze visual footage with a streamlined crowd detection and tracking workspace.</p>
          <Link className="button button-light" to="/video-detection">Process a video <ArrowRight size={17} /></Link>
        </div>
        <div className="hero-graphic" aria-hidden="true">
          <div className="scan-frame"><span /><span /><span /><span /><div className="scan-person">●</div></div>
          <div className="graphic-label"><i /> LIVE ANALYSIS</div>
        </div>
      </section>
      <section>
        <div className="section-heading">
          <div><div className="eyebrow">GET STARTED</div><h2>Your analysis tools</h2></div>
        </div>
        <div className="feature-grid">
          {features.map(({ icon: Icon, title, text }) => (
            <article className="feature-card" key={title}>
              <span className="feature-icon"><Icon size={20} /></span>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

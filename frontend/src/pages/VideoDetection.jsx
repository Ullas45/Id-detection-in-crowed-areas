import { Camera } from 'lucide-react'
import UploadBox from '../components/UploadBox.jsx'

export default function VideoDetection() {
  return (
    <div className="page-stack narrow-page">
      <div className="page-heading">
        <span className="feature-icon"><Camera size={20} /></span>
        <div><div className="eyebrow">VIDEO ANALYSIS</div><h1>Video detection</h1></div>
      </div>
      <p className="page-intro">Upload a video to detect and track objects across its frames.</p>
      <UploadBox
        supported={false}
        unavailableMessage="Video processing is not available yet. The backend currently exposes image detection only."
      />
      <p className="helper-text">The backend is expected at <code>http://localhost:8000</code>.</p>
    </div>
  )
}

import { ScanLine } from 'lucide-react'
import UploadBox from '../components/UploadBox.jsx'

export default function ImageDetection() {
  return (
    <div className="page-stack narrow-page">
      <div className="page-heading">
        <span className="feature-icon"><ScanLine size={20} /></span>
        <div><div className="eyebrow">IMAGE ANALYSIS</div><h1>Image detection</h1></div>
      </div>
      <p className="page-intro">Choose an image to prepare it for crowd detection.</p>
      <UploadBox kind="image" />
    </div>
  )
}

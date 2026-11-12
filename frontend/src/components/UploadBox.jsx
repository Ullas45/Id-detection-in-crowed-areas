import { useRef, useState } from 'react'
import { FileVideo2, ImagePlus, LoaderCircle, Upload } from 'lucide-react'
import { processImage, processVideo } from '../services/api.js'

export default function UploadBox({
  kind = 'video',
  supported = true,
  unavailableMessage = 'Image processing is not available yet. The backend currently supports video processing only.',
}) {
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const isVideo = kind === 'video'
  const Icon = isVideo ? FileVideo2 : ImagePlus
  const accept = isVideo ? '.mp4,.mov,.avi,.mkv' : '.jpg,.jpeg,.png'

  function chooseFile(nextFile) {
    setFile(nextFile)
    setResult(null)
    setError('')
  }

  async function submit(event) {
    event.preventDefault()
    if (!file || !supported || busy) return

    setBusy(true)
    setError('')
    setResult(null)
    try {
      setResult(isVideo ? await processVideo(file) : await processImage(file))
    } catch (requestError) {
      setError(requestError.response?.data?.detail || requestError.message || 'Could not process this video.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="upload-card" onSubmit={submit}>
      <input
        ref={inputRef}
        className="visually-hidden"
        type="file"
        accept={accept}
        onChange={(event) => chooseFile(event.target.files?.[0] || null)}
        disabled={!supported || busy}
      />
      <button
        className={`drop-zone${file ? ' has-file' : ''}`}
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault()
          chooseFile(event.dataTransfer.files?.[0] || null)
        }}
        disabled={!supported || busy}
      >
        <span className="upload-icon"><Icon size={23} /></span>
        <strong>{file ? file.name : `Drop your ${kind} here`}</strong>
        <span>{file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB · Click to change` : 'or click to browse your files'}</span>
        <span className="file-types">{isVideo ? 'MP4, MOV, AVI, MKV' : 'JPG, PNG, WEBP'}</span>
      </button>
      {!supported && <p className="notice">{unavailableMessage}</p>}
      {error && <p className="error-message" role="alert">{error}</p>}
      {result && (isVideo ? (
        <div className="result-message" role="status">
          <strong>Video processed</strong>
          <span>{result.frames_processed} frames analyzed</span>
          <span>Output saved as {result.output_file.split(/[\\/]/).pop()}</span>
        </div>
      ) : (
        <div className="result-message" role="status">
          <strong>Detection complete · {result.person_count} people detected</strong>
          <img className="detection-result-image" src={result.output_url} alt="Image with detected people highlighted" />
        </div>
      ))}
      <button className="button button-primary upload-submit" type="submit" disabled={!file || !supported || busy}>
        {busy ? <><LoaderCircle className="spin" size={17} /> Processing video…</> : <><Upload size={17} /> Start detection</>}
      </button>
    </form>
  )
}

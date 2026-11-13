import { useEffect, useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  FileImage,
  FileVideo,
  LoaderCircle,
  RotateCcw,
  ScanSearch,
  ShieldCheck,
  UserRoundSearch,
  UsersRound,
  UploadCloud
} from "lucide-react";

const API_BASE =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function UploadBox() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [referenceFile, setReferenceFile] = useState(null);
  const [referencePreview, setReferencePreview] = useState("");
  const [detectionMode, setDetectionMode] = useState("all");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  useEffect(() => {
    return () => {
      if (referencePreview) URL.revokeObjectURL(referencePreview);
    };
  }, [referencePreview]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    const isImage = selectedFile.type.startsWith("image/");
    const isVideo = selectedFile.type.startsWith("video/");

    if (!isImage && !isVideo) {
      setError("Please select an image or video.");
      return;
    }

    if (isImage && selectedFile.size > 20 * 1024 * 1024) {
      setError("Image must be smaller than 20 MB.");
      return;
    }

    if (isVideo && selectedFile.size > 100 * 1024 * 1024) {
      setError("Video must be smaller than 100 MB.");
      return;
    }

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setError("");
  };

  const handleReferenceFileChange = (event) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    if (!selectedFile.type.startsWith("image/")) {
      setError("Please select a reference photo.");
      return;
    }

    if (selectedFile.size > 20 * 1024 * 1024) {
      setError("Reference photo must be smaller than 20 MB.");
      return;
    }

    setReferencePreview(URL.createObjectURL(selectedFile));
    setReferenceFile(selectedFile);
    setResult(null);
    setError("");
  };

  const handleDetection = async () => {
    if (!file) {
      setError("Please upload an image or video first.");
      return;
    }

    const isVideo = file.type.startsWith("video/");
    const isPersonMatch = detectionMode === "match";

    if (isPersonMatch && !referenceFile) {
      setError("Please upload a reference photo of the person.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();

      if (isPersonMatch && isVideo) {
        formData.append("file", file);
        formData.append("reference_image", referenceFile);
      } else if (isPersonMatch) {
        formData.append("group_image", file);
        formData.append("reference_image", referenceFile);
      } else {
        formData.append("file", file);
      }

      const endpoint = isVideo
        ? isPersonMatch
          ? "/detect/person-match/video"
          : "/detect/video"
        : isPersonMatch
          ? "/detect/person-match"
          : "/detect/image";

      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        body: formData
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Detection failed");
      }

      if (!data.success) {
        throw new Error("Detection was unsuccessful");
      }

      const outputPath = isVideo ? data.output_video : data.output_image;
      if (!outputPath) {
        throw new Error("Output file path was not returned");
      }

      setResult({
        type: isVideo ? "video" : "image",
        mode: isPersonMatch ? "match" : "all",
        outputUrl: `${API_BASE}${outputPath}`,
        personCount: isVideo
          ? isPersonMatch
            ? data.max_matches_in_frame
            : data.max_people_in_frame
          : isPersonMatch
            ? data.matched_count
            : data.person_count,
        details: data
      });
    } catch (err) {
      console.error("Detection error:", err);
      setError(err.message || "Unable to process file");
    } finally {
      setLoading(false);
    }
  };

  const resetDetection = () => {
    setFile(null);
    setPreview("");
    setReferenceFile(null);
    setReferencePreview("");
    setDetectionMode("all");
    setResult(null);
    setError("");
  };

  const isVideo = file?.type.startsWith("video/");

  return (
    <div className={`analysis-layout ${result ? "has-result" : ""}`}>
      <section className="analysis-panel">
        <div className="analysis-panel-heading">
          <div className="analysis-heading-icon"><ScanSearch size={20} /></div>
          <div>
            <p className="analysis-step">STEP 01 <span>·</span> CONFIGURE</p>
            <h3>Choose your analysis</h3>
          </div>
          <span className="analysis-private"><ShieldCheck size={14} /> PRIVATE</span>
        </div>

        <div className="analysis-mode-grid">
          <button
            type="button"
            onClick={() => {
              setDetectionMode("all");
              setResult(null);
              setError("");
            }}
            aria-pressed={detectionMode === "all"}
            className={`analysis-mode-card ${detectionMode === "all" ? "is-selected" : ""}`}
          >
            <span className="analysis-mode-icon"><UsersRound size={20} /></span>
            <span className="analysis-mode-copy">
              <strong>Detect everyone</strong>
              <small>Count and mark every person in your media.</small>
            </span>
            <span className="mode-radio" />
          </button>
          <button
            type="button"
            onClick={() => {
              setDetectionMode("match");
              setResult(null);
              setError("");
            }}
            aria-pressed={detectionMode === "match"}
            className={`analysis-mode-card ${detectionMode === "match" ? "is-selected" : ""}`}
          >
            <span className="analysis-mode-icon"><UserRoundSearch size={20} /></span>
            <span className="analysis-mode-copy">
              <strong>Find a person</strong>
              <small>Match one face in a photo or video.</small>
            </span>
            <span className="mode-radio" />
          </button>
        </div>

        <div className="upload-field-label">
          <span>YOUR MEDIA</span>
          <small>{isVideo ? "VIDEO SELECTED" : "IMAGE OR VIDEO"}</small>
        </div>

        <label className={`media-dropzone ${file ? "has-file" : ""}`}>
          <input
            type="file"
            accept="image/jpeg,image/png,video/mp4,video/avi,video/quicktime"
            onChange={handleFileChange}
          />
          <span className="dropzone-icon"><UploadCloud size={25} /></span>
          {file ? (
            <>
              <strong className="dropzone-filename">{file.name}</strong>
              <span>{(file.size / (1024 * 1024)).toFixed(1)} MB · Click to replace</span>
            </>
          ) : (
            <>
              <strong>Drop your image or video here</strong>
              <span>or <em>browse files</em> from your device</span>
              <small>JPG, PNG, MP4, AVI or MOV <i>·</i> Up to 100 MB</small>
            </>
          )}
        </label>

        {file && !result && (
          <div className="media-preview">
            <div className="preview-heading">
              <span><CheckCircle2 size={15} /> Media ready</span>
              {isVideo
                ? <FileVideo size={16} aria-label="Video file" />
                : <FileImage size={16} aria-label="Image file" />}
            </div>
            {isVideo ? (
              <video src={preview} controls className="preview-media" />
            ) : (
              <img src={preview} alt="Selected crowd" className="preview-media" />
            )}
          </div>
        )}

        {detectionMode === "match" && (
          <div className="reference-section">
            <div className="upload-field-label">
              <span>REFERENCE PERSON</span>
              <small>ONE CLEAR FACE</small>
            </div>
            <label className={`reference-dropzone ${referenceFile ? "has-file" : ""}`}>
              <input
                type="file"
                accept="image/jpeg,image/png"
                onChange={handleReferenceFileChange}
              />
              {referencePreview ? (
                <>
                  <img src={referencePreview} alt="Reference person" />
                  <span className="reference-file-name">{referenceFile?.name}</span>
                  <small>Click to choose another photo</small>
                </>
              ) : (
                <>
                  <span className="reference-icon"><UserRoundSearch size={20} /></span>
                  <span><strong>Add a reference photo</strong><small>JPG or PNG · One face, looking clearly at camera</small></span>
                  <span className="reference-browse">Browse</span>
                </>
              )}
            </label>
            <p className="privacy-note">
              <ShieldCheck size={14} />
              Your images are processed privately. Temporary uploads are removed.
            </p>
          </div>
        )}

        {error && (
          <div className="upload-error" role="alert">{error}</div>
        )}

        <button
          type="button"
          onClick={handleDetection}
          disabled={!file || loading}
          className="detect-button"
        >
          {loading ? (
            <><LoaderCircle className="loading-spinner" size={18} /> Analyzing your media…</>
          ) : (
            <>{detectionMode === "match" ? "Find this person" : "Analyze media"} <ArrowRight size={17} /></>
          )}
        </button>

        {loading && (
          <p className="processing-note">
            {detectionMode === "match"
              ? "Comparing faces and preparing your highlighted result."
              : "Our vision model is scanning your media. This may take a moment."}
          </p>
        )}
      </section>

      {result && (
        <section className="result-panel">
          <div className="result-heading">
            <div>
              <p className="analysis-step">ANALYSIS COMPLETE</p>
              <h3>Your results</h3>
            </div>
            <span className="result-complete"><CheckCircle2 size={15} /> COMPLETE</span>
          </div>

          <div className="result-summary">
            <span className="result-icon">
              {result.mode === "match" ? <UserRoundSearch size={19} /> : <UsersRound size={19} />}
            </span>
            <div className="result-count-copy">
              <span>
                {result.mode === "match"
                  ? result.type === "video"
                    ? "MAX MATCHES IN ONE FRAME"
                    : "MATCHING PEOPLE FOUND"
                  : result.type === "video"
                    ? "MAX PEOPLE IN ONE FRAME"
                    : "PEOPLE DETECTED"}
              </span>
              <strong>{result.personCount}</strong>
            </div>
            <span className="result-count-label">
              {result.mode === "match" ? "face matches" : "people"}
            </span>
          </div>

          <div className="detection-result">
            <div className="result-media-heading">
              <span>{result.mode === "match" ? "HIGHLIGHTED MATCHES" : "ANNOTATED MEDIA"}</span>
              <span>{result.type === "video" ? "VIDEO" : "IMAGE"}</span>
            </div>
            {result.type === "image" ? (
              <img
                src={result.outputUrl}
                alt={result.mode === "match" ? "Reference photo matches" : "Detected people"}
              />
            ) : (
              <video
                key={result.outputUrl}
                src={result.outputUrl}
                controls
                playsInline
                preload="metadata"
              >
                Your browser does not support video playback.
              </video>
            )}
          </div>

          {result.type === "video" && (
            <div className="video-analytics-grid">
              {result.mode === "match" ? (
                <>
                  <div className="analytics-item">
                    <span>Frames containing a match</span>
                    <strong>{result.details.matched_frames}</strong>
                  </div>
                  <div className="analytics-item">
                    <span>Frames processed</span>
                    <strong>{result.details.processed_frames}</strong>
                  </div>
                </>
              ) : (
                <>
                  <div className="analytics-item">
                    <span>Unique tracking IDs</span>
                    <strong>{result.details.unique_person_count}</strong>
                  </div>
                  <div className="analytics-item">
                    <span>Average people per frame</span>
                    <strong>{result.details.average_people_per_frame}</strong>
                  </div>
                  <div className="analytics-item">
                    <span>Frames processed</span>
                    <strong>{result.details.processed_frames}</strong>
                  </div>
                </>
              )}
            </div>
          )}

          <button onClick={resetDetection} className="reset-button">
            <RotateCcw size={16} /> Analyze another file
          </button>
        </section>
      )}
    </div>
  );
}

export default UploadBox;

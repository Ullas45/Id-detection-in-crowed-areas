
import { useEffect, useState } from "react";

const API_BASE =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function UploadBox() {

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Create preview when file changes
  useEffect(() => {

    if (!file) {
      setPreview("");
      return;
    }

    const url = URL.createObjectURL(file);
    setPreview(url);

    return () => URL.revokeObjectURL(url);

  }, [file]);

  // Upload file
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
    setResult(null);
    setError("");
  };

  // Detect people
  const handleDetection = async () => {

    if (!file) {
      setError("Please upload an image or video first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {

      const isVideo = file.type.startsWith("video/");

      const formData = new FormData();
      formData.append("file", file);

      const endpoint = isVideo
        ? "/detect/video"
        : "/detect/image";

      const response = await fetch(
        `${API_BASE}${endpoint}`,
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Detection failed"
        );
      }

      if (!data.success) {
        throw new Error("Detection was unsuccessful");
      }

      const outputPath = isVideo
        ? data.output_video
        : data.output_image;

      if (!outputPath) {
        throw new Error("Output file path was not returned");
      }

      setResult({
        type: isVideo ? "video" : "image",
        outputUrl: `${API_BASE}${outputPath}`,
        personCount: isVideo
          ? data.max_people_in_frame
          : data.person_count,
        details: data
      });

    } catch (err) {

      console.error("Detection error:", err);

      setError(
        err.message || "Unable to process file"
      );

    } finally {

      setLoading(false);

    }
  };

  const resetDetection = () => {
    setFile(null);
    setResult(null);
    setError("");
  };

  return (

    <div className="w-full space-y-6">

      {/* Upload section */}

      <div className="bg-[#111827] border border-gray-800
                      rounded-2xl p-6">

        <h2 className="text-xl font-bold mb-5">
          Person Detection
        </h2>

        <label
          className="flex flex-col items-center justify-center
                     min-h-64 border-2 border-dashed
                     border-gray-600 rounded-xl
                     cursor-pointer hover:border-blue-500
                     transition p-6 text-center"
        >

          <div className="text-blue-400 text-5xl mb-4">
            ↑
          </div>

          <h3 className="text-lg font-semibold">
            Upload your crowd image or video
          </h3>

          <p className="text-gray-400 mt-2">
            Drag and drop or browse files
          </p>

          <p className="text-gray-500 text-sm mt-2">
            JPG, PNG, MP4, AVI, MOV
          </p>

          <input
            type="file"
            accept="image/jpeg,image/png,video/mp4,video/avi,video/quicktime"
            onChange={handleFileChange}
            className="hidden"
          />

        </label>

        {/* Selected file preview */}

        {file && !result && (

          <div className="mt-5 space-y-3">

            <p className="text-gray-300 text-sm">
              Selected: {file.name}
            </p>

            {file.type.startsWith("image/") ? (

              <img
                src={preview}
                alt="Selected crowd"
                className="max-h-96 w-full object-contain
                           rounded-xl bg-black"
              />

            ) : (

              <video
                src={preview}
                controls
                className="w-full max-h-96 rounded-xl bg-black"
              />

            )}

          </div>

        )}

        {/* Detect button */}

        <button
          onClick={handleDetection}
          disabled={!file || loading}
          className="w-full mt-5 bg-blue-600
                     hover:bg-blue-700
                     disabled:bg-gray-600
                     disabled:cursor-not-allowed
                     text-white font-bold py-3
                     rounded-lg transition"
        >

          {loading
            ? "Processing..."
            : "Detect People"}

        </button>

        {loading && (

          <p className="text-center text-blue-400 mt-3">
            AI is processing your file. Please wait...
          </p>

        )}

        {error && (

          <div className="mt-4 bg-red-900/30
                          border border-red-500
                          text-red-300 rounded-lg p-3">
            {error}
          </div>

        )}

      </div>

      {/* Detection result */}

      {result && (

        <div className="bg-[#111827] border border-gray-800
                        rounded-2xl p-6 space-y-5">

          <h2 className="text-xl font-bold">
            Detection Result
          </h2>

          {/* Count */}

          <div className="bg-blue-900/30 border
                          border-blue-500/30
                          rounded-xl p-5">

            <p className="text-gray-400 text-sm">
              {result.type === "image"
                ? "People Detected"
                : "Maximum People in a Frame"}
            </p>

            <h3 className="text-4xl font-bold text-blue-400">
              {result.personCount}
            </h3>

          </div>

          {/* Output image */}

          {result.type === "image" && (

            <img
              src={result.outputUrl}
              alt="Detected people"
              className="w-full rounded-xl border
                         border-gray-700"
            />

          )}

          {/* Output video */}

          {result.type === "video" && (

            <video
              key={result.outputUrl}
              src={result.outputUrl}
              controls
              playsInline
              preload="metadata"
              className="w-full rounded-xl
                         border border-gray-700
                         bg-black"
            >
              Your browser does not support video playback.
            </video>

          )}

          {/* Video analytics */}

          {result.type === "video" && (

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">

              <div className="bg-[#080b12] rounded-lg p-4">
                <p className="text-gray-400 text-sm">
                  Unique tracking IDs
                </p>
                <p className="text-xl font-bold">
                  {result.details.unique_person_count}
                </p>
              </div>

              <div className="bg-[#080b12] rounded-lg p-4">
                <p className="text-gray-400 text-sm">
                  Average people per frame
                </p>
                <p className="text-xl font-bold">
                  {result.details.average_people_per_frame}
                </p>
              </div>

              <div className="bg-[#080b12] rounded-lg p-4">
                <p className="text-gray-400 text-sm">
                  Processed frames
                </p>
                <p className="text-xl font-bold">
                  {result.details.processed_frames}
                </p>
              </div>

            </div>

          )}
          <button
            onClick={resetDetection}
            className="w-full bg-gray-700
                       hover:bg-gray-600
                       text-white py-3 rounded-lg"
          >
            Upload Another File
          </button>

        </div>

      )}

    </div>

  );

}

export default UploadBox;

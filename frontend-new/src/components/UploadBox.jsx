
import { useState } from "react";
import { detectImage } from "../services/api";
import {
  Upload,
  LoaderCircle,
  Scan
} from "lucide-react";

function UploadBox() {

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [cacheBuster, setCacheBuster] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFile = (selectedFile) => {

    if (!selectedFile) return;

    if (!["image/jpeg", "image/png"].includes(selectedFile.type)) {
      setError("Please upload JPG or PNG images only.");
      return;
    }

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setResult(null);
    setError("");
  };

  const handleUpload = async () => {

    if (!file) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {

      const data = await detectImage(file);

      setResult(data);
      setCacheBuster(Date.now());

    } catch (err) {

      setError(
        err.response?.data?.detail ||
        "Detection failed. Check your backend server."
      );

    } finally {

      setLoading(false);

    }
  };

  return (

    <div className="home-upload-panel bg-[#111827] border border-gray-800
                    rounded-2xl p-6 md:p-8">

      <div className="flex items-center gap-3 mb-6">

        <Scan className="text-blue-400" size={26} />

        <h2 className="text-xl font-bold">
          Person Detection
        </h2>

      </div>

      <label
        className="border-2 border-dashed border-gray-700
                   hover:border-blue-500 rounded-xl p-10
                   flex flex-col items-center justify-center
                   cursor-pointer transition"
      >

        <Upload size={42} className="text-blue-400 mb-4" />

        <p className="text-gray-200 font-medium">
          Upload your crowd image
        </p>

        <p className="text-gray-500 text-sm mt-2">
          Drag and drop or browse files
        </p>

        <p className="text-gray-600 text-xs mt-2">
          Supports JPG and PNG
        </p>

        <input
          type="file"
          accept="image/jpeg,image/png"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />

      </label>

      {preview && (

        <div className="mt-5">

          <p className="text-gray-400 mb-2">
            Selected Image
          </p>

          <img
            src={preview}
            alt="Uploaded crowd"
            className="max-h-64 rounded-xl object-contain"
          />

        </div>

      )}

      {file && (

        <p className="text-sm text-gray-400 mt-4">
          Selected: {file.name}
        </p>

      )}

      <button
        onClick={handleUpload}
        disabled={loading || !file}
        className="mt-6 w-full bg-blue-600
                   hover:bg-blue-700 disabled:opacity-50
                   py-3 rounded-lg font-semibold
                   flex items-center justify-center gap-2"
      >

        {loading ? (
          <>
            <LoaderCircle className="animate-spin" />
            Processing Image...
          </>
        ) : (
          <>
            <Scan size={19} />
            Detect People
          </>
        )}

      </button>

      {error && (

        <p className="text-red-400 mt-4">
          {error}
        </p>

      )}

      {result && (

        <div className="mt-7 space-y-5">

          <div className="bg-gray-900 border border-gray-800
                          rounded-xl p-5">

            <p className="text-gray-400 text-sm">
              Total People Detected
            </p>

            <h1 className="text-4xl font-bold
                           text-green-400 mt-2">
              {result.person_count}
            </h1>

          </div>

          <div>

            <h3 className="font-semibold mb-3">
              Detection Result
            </h3>

            <img
              src={`http://127.0.0.1:8000${result.output_image}?t=${cacheBuster}`}
              alt="AI detected people"
              className="w-full bg-[#111827] border border-gray-800
             rounded-2xl p-6 md:p-8 shadow-xl"
            />

            <a
              href={`http://127.0.0.1:8000${result.output_image}`}
              target="_blank"
              rel="noreferrer"
              className="inline-block mt-3 text-blue-400 hover:underline"
            >
              View processed image
            </a>

          </div>

        </div>

      )}

    </div>
  );
}

export default UploadBox;

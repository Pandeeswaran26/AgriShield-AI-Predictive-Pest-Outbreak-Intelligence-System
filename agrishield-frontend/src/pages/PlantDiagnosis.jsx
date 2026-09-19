import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import {
  Camera,
  Upload,
  Image as ImageIcon,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Trash2,
  ScanLine,
  Sparkles,
  ShieldCheck,
  Sprout,
  Activity,
  ArrowRight,
  Info,
  Bug,
  Droplets,
  Layers,
  X,
  Eye,
  Sliders,
  Compass,
} from "lucide-react";
import * as diagnosisService from "../services/diagnosisService";

// Curated sample leaf test presets with pre-drawn canvas textures for immediate one-click testing
const SAMPLE_PRESETS = [
  {
    name: "Tomato Early Blight",
    crop: "Tomato",
    condition: "Early Blight (Alternaria)",
    bgColor: "#2d5a27",
    spotColor: "#613b16",
    hasSpots: true,
    pattern: "concentric",
  },
  {
    name: "Healthy Apple Leaf",
    crop: "Apple",
    condition: "Healthy Foliage",
    bgColor: "#2e7d32",
    spotColor: "#2e7d32",
    hasSpots: false,
    pattern: "clean",
  },
  {
    name: "Corn Common Rust",
    crop: "Corn",
    condition: "Common Rust (Puccinia)",
    bgColor: "#556b2f",
    spotColor: "#b85d19",
    hasSpots: true,
    pattern: "pustules",
  },
  {
    name: "Potato Late Blight",
    crop: "Potato",
    condition: "Late Blight (Phytophthora)",
    bgColor: "#274e13",
    spotColor: "#1c1c1c",
    hasSpots: true,
    pattern: "water_soaked",
  },
  {
    name: "Grape Black Rot",
    crop: "Grape",
    condition: "Black Rot (Guignardia)",
    bgColor: "#38761d",
    spotColor: "#351c75",
    hasSpots: true,
    pattern: "circular",
  },
];

export default function PlantDiagnosis() {
  const navigate = useNavigate();

  // Selected file and preview
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [fileDetails, setFileDetails] = useState({ name: "", size: "" });

  // Camera state
  const [isCameraActive, setIsCameraActive] = useState(false);
  const videoRef = useRef(null);
  const cameraStreamRef = useRef(null);

  // Analysis & Results state
  const [analyzing, setAnalyzing] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState(null);
  const [recentHistory, setRecentHistory] = useState([]);
  const [showTaxonomy, setShowTaxonomy] = useState(false);
  const [taxonomyData, setTaxonomyData] = useState(null);

  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);
  const dropZoneRef = useRef(null);

  useEffect(() => {
    loadRecentHistory();
    loadTaxonomy();
    return () => {
      stopCamera();
    };
  }, []);

  const loadRecentHistory = async () => {
    try {
      const data = await diagnosisService.getDiagnosisHistory(6);
      if (data && data.history) {
        setRecentHistory(data.history);
      }
    } catch {
      // Non-fatal
    }
  };

  const loadTaxonomy = async () => {
    try {
      const data = await diagnosisService.getSupportedClasses();
      setTaxonomyData(data);
    } catch {
      // Non-fatal
    }
  };

  // ----------------------------------------------------
  // Image Selection & Drag-and-Drop
  // ----------------------------------------------------
  const handleFileSelect = (file) => {
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      toast.error("Please upload a valid image file (JPG, PNG, WebP)");
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error("File exceeds 10MB limit. Please choose a smaller leaf photo.");
      return;
    }

    setSelectedFile(file);
    setFileDetails({
      name: file.name,
      size: `${(file.size / 1024).toFixed(1)} KB`,
    });

    const reader = new FileReader();
    reader.onload = (e) => setPreviewUrl(e.target.result);
    reader.readAsDataURL(file);

    // Reset previous result
    setDiagnosisResult(null);
    toast.success("Leaf image loaded and ready for analysis");
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleRemoveImage = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setFileDetails({ name: "", size: "" });
    setDiagnosisResult(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (cameraInputRef.current) cameraInputRef.current.value = "";
  };

  // ----------------------------------------------------
  // Live Camera Controls (WebRTC)
  // ----------------------------------------------------
  const startCamera = async () => {
    try {
      setIsCameraActive(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      cameraStreamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err) {
      setIsCameraActive(false);
      // If WebRTC fails or denied, fall back to native device camera input
      if (cameraInputRef.current) {
        cameraInputRef.current.click();
      } else {
        toast.error("Unable to access camera directly. Please use file upload.");
      }
    }
  };

  const captureCameraSnapshot = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth || 640;
    canvas.height = videoRef.current.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `camera_scan_${Date.now()}.jpg`, { type: "image/jpeg" });
        handleFileSelect(file);
      }
      stopCamera();
    }, "image/jpeg", 0.92);
  };

  const stopCamera = () => {
    if (cameraStreamRef.current) {
      cameraStreamRef.current.getTracks().forEach((track) => track.stop());
      cameraStreamRef.current = null;
    }
    setIsCameraActive(false);
  };

  // ----------------------------------------------------
  // Generate Sample Leaf Preset
  // ----------------------------------------------------
  const handleLoadSample = (sample) => {
    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext("2d");

    // Leaf background
    ctx.fillStyle = sample.bgColor;
    ctx.fillRect(0, 0, 256, 256);

    // Draw main vein
    ctx.strokeStyle = "#4a8536";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(128, 20);
    ctx.lineTo(128, 236);
    ctx.stroke();

    // Draw lateral veins
    for (let y = 50; y < 220; y += 30) {
      ctx.beginPath();
      ctx.moveTo(128, y);
      ctx.lineTo(50, y - 20);
      ctx.moveTo(128, y);
      ctx.lineTo(206, y - 20);
      ctx.stroke();
    }

    // Add symptoms pattern if diseased
    if (sample.hasSpots) {
      ctx.fillStyle = sample.spotColor;
      if (sample.pattern === "concentric") {
        // Alternaria target spots
        ctx.beginPath();
        ctx.arc(90, 110, 32, 0, 2 * Math.PI);
        ctx.fill();
        ctx.strokeStyle = "#805220";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(90, 110, 20, 0, 2 * Math.PI);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(170, 160, 26, 0, 2 * Math.PI);
        ctx.fill();
      } else if (sample.pattern === "pustules") {
        // Rust pustules
        for (let i = 0; i < 28; i++) {
          const rx = 60 + Math.random() * 136;
          const ry = 50 + Math.random() * 156;
          ctx.beginPath();
          ctx.ellipse(rx, ry, 6, 3, Math.PI / 4, 0, 2 * Math.PI);
          ctx.fill();
        }
      } else {
        // General blotch
        ctx.beginPath();
        ctx.ellipse(100, 120, 45, 30, Math.PI / 6, 0, 2 * Math.PI);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(160, 170, 35, 25, -Math.PI / 5, 0, 2 * Math.PI);
        ctx.fill();
      }
    }

    canvas.toBlob((blob) => {
      const file = new File([blob], `${sample.name.toLowerCase().replace(/\s+/g, "_")}.jpg`, {
        type: "image/jpeg",
      });
      handleFileSelect(file);
      toast.success(`Loaded sample: ${sample.name}`);
    }, "image/jpeg", 0.95);
  };

  // ----------------------------------------------------
  // Run AI Leaf Diagnosis
  // ----------------------------------------------------
  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast.error("Please upload or take a plant leaf photo first.");
      return;
    }

    setAnalyzing(true);
    setDiagnosisResult(null);

    try {
      const result = await diagnosisService.diagnosePlantImage(selectedFile);

      // ── Plant/Leaf Validation Gate ────────────────────────────────────────
      // The backend runs a plant validator BEFORE the disease model.
      // When is_valid_plant is false the disease model never ran and
      // no DB record was saved — we must NOT show disease results.
      if (result.is_valid_plant === false) {
        setDiagnosisResult({ ...result, _rejected: true });
        // Do NOT reload history — nothing was saved
        toast.error("Image rejected: not a supported plant leaf.");
        return;
      }

      // Valid plant image — show full diagnosis
      setDiagnosisResult(result);
      loadRecentHistory();

      if (result.is_ambiguous_image) {
        toast("⚠️ Image quality is borderline — results may be less accurate.", {
          icon: "⚠️",
          duration: 4000,
        });
      } else {
        toast.success(`Diagnosis complete: ${result.crop} — ${result.disease}`);
      }
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        "AI diagnosis unavailable. Unable to process this image. Please try again.";
      toast.error(msg);
      // Show error state without fake disease results
      setDiagnosisResult({ _error: true, errorMessage: msg });
    } finally {
      setAnalyzing(false);
    }
  };


  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="card p-6 relative overflow-hidden bg-gradient-to-r from-field-900 via-field-800 to-field-900">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-canopy/15 border border-canopy/30 text-canopy text-xs font-semibold uppercase tracking-wider mb-2">
              <Camera size={13} />
              Computer Vision & Pathology AI
            </div>
            <h1 className="text-2xl lg:text-3xl font-bold font-display text-white tracking-tight">
              Plant Image Diagnosis & Health Scanner
            </h1>
            <p className="text-sm text-mist/70 mt-1 max-w-2xl">
              Upload a plant leaf image or snap a photo in the field to automatically identify the
              crop, diagnose foliar diseases, evaluate leaf health, and receive targeted IPM
              treatment plans.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setShowTaxonomy(!showTaxonomy)}
              className="btn-ghost text-xs py-2 px-3 flex items-center gap-1.5"
            >
              <Info size={14} />
              {showTaxonomy ? "Hide Supported Crops" : "Supported Crops (14)"}
            </button>
          </div>
        </div>
      </div>

      {/* Supported Classes Accordion */}
      {showTaxonomy && taxonomyData && (
        <div className="card p-5 border border-canopy/25 bg-field-950/70 animate-fadeIn">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-canopy flex items-center gap-2">
              <Sprout size={16} />
              Supported Crops & Pathology Coverage ({taxonomyData.total_classes} Classes across{" "}
              {taxonomyData.total_crops} Crops)
            </h3>
            <button
              onClick={() => setShowTaxonomy(false)}
              className="text-xs text-mist/60 hover:text-mist"
            >
              Close
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
            {Object.entries(taxonomyData.crops || {}).map(([cropName, details]) => (
              <div
                key={cropName}
                className="p-2.5 rounded-xl bg-field-800/80 border border-field-900/10 dark:border-mist/10 text-xs"
              >
                <span className="font-semibold text-white block truncate">{cropName}</span>
                <span className="text-[11px] text-canopy block mt-0.5">
                  {details.diseases.length} Diseases
                </span>
                {details.has_healthy_class && (
                  <span className="text-[10px] text-emerald-400/80 block">+ Healthy Control</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Grid: Upload/Capture Column (Left) & Diagnosis Results Column (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Image Input */}
        <div className="lg:col-span-5 space-y-4">
          <div className="card p-5 space-y-4">
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <ScanLine size={18} className="text-canopy" />
              1. Leaf Image Input
            </h2>

            {/* Hidden native inputs */}
            <input
              type="file"
              ref={fileInputRef}
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) handleFileSelect(e.target.files[0]);
              }}
            />
            <input
              type="file"
              ref={cameraInputRef}
              accept="image/*"
              capture="environment"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) handleFileSelect(e.target.files[0]);
              }}
            />

            {/* Drag & Drop Box or Preview */}
            {!previewUrl && !isCameraActive && (
              <div
                ref={dropZoneRef}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current && fileInputRef.current.click()}
                className="border-2 border-dashed border-field-900/20 dark:border-mist/20 hover:border-canopy/60 rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition bg-field-950/40 group min-h-[260px]"
              >
                <div className="w-14 h-14 rounded-2xl bg-canopy/10 border border-canopy/20 flex items-center justify-center text-canopy group-hover:scale-110 transition mb-3">
                  <Upload size={24} />
                </div>
                <p className="text-sm font-semibold text-white">Drag & drop plant leaf photo here</p>
                <p className="text-xs text-mist/50 mt-1 max-w-xs">
                  Supports JPG, PNG, or WebP up to 10MB. High-resolution top-down leaf shots provide
                  best diagnosis.
                </p>

                <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
                  <span className="btn-ghost text-xs py-1.5 px-3">Browse File</span>
                </div>
              </div>
            )}

            {/* Live Camera Viewport */}
            {isCameraActive && (
              <div className="relative rounded-2xl overflow-hidden bg-black border border-canopy/40">
                <video ref={videoRef} playsInline autoPlay className="w-full h-64 object-cover" />
                <div className="absolute inset-x-0 bottom-3 flex items-center justify-center gap-3 z-10 px-4">
                  <button
                    type="button"
                    onClick={captureCameraSnapshot}
                    className="btn-primary text-xs py-2 px-4 shadow-lg shadow-canopy/20"
                  >
                    <Camera size={14} />
                    Capture Leaf
                  </button>
                  <button
                    type="button"
                    onClick={stopCamera}
                    className="btn-ghost text-xs py-2 px-3 bg-black/60 text-white"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Selected Image Preview */}
            {previewUrl && !isCameraActive && (
              <div className="relative rounded-2xl overflow-hidden border border-canopy/30 bg-field-950/60 p-2">
                <div className="relative h-64 w-full rounded-xl overflow-hidden bg-black flex items-center justify-center">
                  <img src={previewUrl} alt="Leaf preview" className="max-h-full object-contain" />
                  <div className="absolute top-2 right-2 flex items-center gap-1.5">
                    <button
                      onClick={handleRemoveImage}
                      className="p-1.5 rounded-lg bg-black/70 hover:bg-alert/80 text-white transition backdrop-blur-sm"
                      title="Remove image"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between mt-2.5 px-2 text-xs text-mist/70">
                  <span className="font-mono truncate max-w-[200px]">{fileDetails.name}</span>
                  <span>{fileDetails.size}</span>
                </div>
              </div>
            )}

            {/* Dual Upload / Camera Buttons */}
            <div className="grid grid-cols-2 gap-2.5 pt-1">
              <button
                type="button"
                onClick={() => fileInputRef.current && fileInputRef.current.click()}
                className="btn-ghost text-xs py-2.5 flex items-center justify-center gap-2"
              >
                <ImageIcon size={15} />
                {selectedFile ? "Replace File" : "Choose File"}
              </button>

              <button
                type="button"
                onClick={startCamera}
                className="btn-ghost text-xs py-2.5 flex items-center justify-center gap-2 text-canopy border-canopy/30 hover:bg-canopy/10"
              >
                <Camera size={15} />
                Use Camera
              </button>
            </div>

            {/* Primary Action Button */}
            <button
              type="button"
              disabled={!selectedFile || analyzing}
              onClick={handleAnalyze}
              className="btn-primary w-full py-3 text-sm flex items-center justify-center gap-2 font-semibold shadow-lg shadow-canopy/15"
            >
              {analyzing ? (
                <>
                  <RefreshCw size={17} className="animate-spin" />
                  Running Neural Vision Classifier...
                </>
              ) : (
                <>
                  <Sparkles size={17} />
                  Analyze Plant Leaf
                </>
              )}
            </button>
          </div>

          {/* Quick Preset Samples Card */}
          <div className="card p-4 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-mist/60 flex items-center gap-1.5">
              <Activity size={14} className="text-canopy" />
              Quick Test: One-Click Leaf Presets
            </h3>
            <p className="text-xs text-mist/60">
              Don't have a leaf image ready? Test immediately with these calibrated crop disease
              profiles:
            </p>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_PRESETS.map((sample) => (
                <button
                  key={sample.name}
                  onClick={() => handleLoadSample(sample)}
                  className="px-2.5 py-1.5 rounded-xl border border-field-900/10 dark:border-mist/10 hover:border-canopy bg-field-950/40 text-xs font-medium text-white transition hover:bg-canopy/10 text-left"
                >
                  <span className="block">{sample.name}</span>
                  <span className="text-[10px] text-mist/50 block">{sample.condition}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Results & Treatment Plan */}
        <div className="lg:col-span-7 space-y-4">
          {!diagnosisResult && !analyzing && (
            <div className="card p-10 flex flex-col items-center justify-center text-center min-h-[420px] bg-field-950/20 border-dashed">
              <div className="w-16 h-16 rounded-3xl bg-canopy/10 border border-canopy/20 flex items-center justify-center text-canopy mb-4">
                <Sprout size={32} />
              </div>
              <h3 className="text-lg font-semibold text-white">No Leaf Analyzed Yet</h3>
              <p className="text-xs text-mist/60 max-w-md mt-1.5">
                Upload a plant photo on the left or select a quick test leaf to run disease
                diagnosis, review symptoms, and receive Integrated Pest Management (IPM) guidance.
              </p>
              <div className="mt-6 flex items-center gap-2 text-xs text-canopy font-medium">
                <ShieldCheck size={16} />
                Trained on 87,000+ PlantVillage leaf observation records
              </div>
            </div>
          )}

          {analyzing && (
            <div className="card p-12 flex flex-col items-center justify-center text-center min-h-[420px] space-y-4">
              <div className="relative">
                <div className="w-20 h-20 rounded-full border-4 border-canopy/20 border-t-canopy animate-spin" />
                <div className="absolute inset-0 flex items-center justify-center text-canopy">
                  <ScanLine size={24} />
                </div>
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">Extracting Foliar Features</h3>
                <p className="text-xs text-mist/60 mt-1 max-w-xs">
                  Running multi-scale convolutional pattern matching, chlorosis detection, and
                  confidence calculations...
                </p>
              </div>
            </div>
          )}

          {/* ── Rejection Panel: non-plant image ──────────────────────── */}
          {diagnosisResult && diagnosisResult._rejected && (
            <div className="card p-8 border border-rose-500/40 bg-gradient-to-br from-field-900 to-rose-950/30 animate-fadeIn flex flex-col items-center text-center space-y-4 min-h-[320px] justify-center">
              <div className="w-16 h-16 rounded-2xl bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-400">
                <AlertTriangle size={30} />
              </div>
              <div>
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/25 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-3">
                  <X size={12} />
                  Invalid Image — Not a Plant Leaf
                </div>
                <h3 className="text-xl font-bold text-white mt-1">No Supported Plant Leaf Detected</h3>
                <p className="text-sm text-mist/70 mt-2 max-w-md leading-relaxed">
                  {diagnosisResult.rejection_reason ||
                    "This image does not appear to contain a supported plant leaf. Please upload a clear, close-up photograph of a plant leaf."}
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full max-w-sm mt-2">
                {["Human / Selfie", "Animal / Pet", "Vehicle / Building", "Document / Screenshot", "Random Object", "Sky / Landscape"].map((ex) => (
                  <div key={ex} className="px-2.5 py-1.5 rounded-xl bg-rose-500/8 border border-rose-500/20 text-xs text-rose-300/70 text-center">
                    ✗ {ex}
                  </div>
                ))}
              </div>
              <div className="mt-2 p-3 rounded-xl bg-canopy/10 border border-canopy/20 text-xs text-canopy max-w-sm">
                <span className="font-semibold block mb-0.5">✓ What works:</span>
                Close-up photos of tomato, potato, corn, apple, grape, or any other supported crop leaves — including diseased or yellowing leaves.
              </div>
              <div className="text-xs text-mist/40 mt-1">
                Leaf confidence score: {diagnosisResult.plant_confidence !== undefined ? `${(diagnosisResult.plant_confidence * 100).toFixed(0)}%` : "—"} (threshold: 35%)
              </div>
            </div>
          )}

          {/* ── Error Panel: API / inference failure ───────────────────── */}
          {diagnosisResult && diagnosisResult._error && (
            <div className="card p-8 border border-clay/30 bg-gradient-to-br from-field-900 to-amber-950/20 animate-fadeIn flex flex-col items-center text-center space-y-3 min-h-[260px] justify-center">
              <div className="w-14 h-14 rounded-2xl bg-clay/15 border border-clay/30 flex items-center justify-center text-amber-400">
                <AlertTriangle size={26} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">AI Diagnosis Unavailable</h3>
                <p className="text-sm text-mist/60 mt-1.5 max-w-sm leading-relaxed">
                  {diagnosisResult.errorMessage || "Unable to process this image. Please try again."}
                </p>
              </div>
              <button
                onClick={() => setDiagnosisResult(null)}
                className="mt-2 px-4 py-2 rounded-xl bg-field-800 border border-mist/10 text-xs text-mist/70 hover:text-white hover:border-canopy/40 transition"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* ── Full Diagnosis Panel: valid plant leaf ─────────────────── */}
          {diagnosisResult && !diagnosisResult._rejected && !diagnosisResult._error && (
            <div className="space-y-4 animate-fadeIn">
              {/* Ambiguous image warning banner */}
              {diagnosisResult.is_ambiguous_image && (
                <div className="flex items-start gap-3 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300">
                  <AlertTriangle size={15} className="shrink-0 mt-0.5" />
                  <span>
                    <span className="font-semibold">Low leaf confidence ({diagnosisResult.plant_confidence !== undefined ? `${(diagnosisResult.plant_confidence * 100).toFixed(0)}%` : "—"}).</span>{" "}
                    The image could not be confidently identified as a clear plant leaf. For best results, upload a close-up photo with the leaf filling the frame. The disease prediction below may be less accurate.
                  </span>
                </div>
              )}

              {/* Primary Diagnostic Card */}
              <div
                className={`card p-6 border ${
                  diagnosisResult.is_healthy
                    ? "border-emerald-500/40 bg-gradient-to-br from-field-900 to-emerald-950/30"
                    : diagnosisResult.severity === "High"
                    ? "border-alert/40 bg-gradient-to-br from-field-900 to-rose-950/30"
                    : "border-clay/40 bg-gradient-to-br from-field-900 to-amber-950/30"
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-field-900/10 dark:border-mist/10">
                  <div>
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="px-2.5 py-0.5 rounded-lg text-xs font-semibold uppercase tracking-wider bg-canopy/20 text-canopy border border-canopy/30">
                        {diagnosisResult.crop}
                      </span>
                      <span
                        className={`px-2.5 py-0.5 rounded-lg text-xs font-semibold ${
                          diagnosisResult.is_healthy
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                            : diagnosisResult.severity === "High"
                            ? "bg-alert/20 text-rose-400 border border-alert/30"
                            : "bg-clay/20 text-amber-400 border border-clay/30"
                        }`}
                      >
                        {diagnosisResult.is_healthy ? "Healthy Plant" : `${diagnosisResult.severity} Severity`}
                      </span>
                      <span className="text-xs text-mist/50">
                        {diagnosisResult.pathogen_type}
                      </span>
                    </div>

                    <h2 className="text-2xl font-bold text-white tracking-tight">
                      {diagnosisResult.disease}
                    </h2>
                  </div>

                  {/* Confidence Meter Badge */}
                  <div className="p-3 rounded-2xl bg-field-950/70 border border-field-900/20 dark:border-mist/20 text-right min-w-[130px]">
                    <span className="text-[11px] uppercase tracking-wider font-semibold text-mist/50 block">
                      AI Confidence
                    </span>
                    <span className="text-2xl font-bold text-canopy font-display block">
                      {diagnosisResult.confidence}%
                    </span>
                    <span className="text-[10px] text-mist/50">Softmax probability</span>
                  </div>
                </div>

                {/* Description */}
                <p className="text-xs text-mist/80 mt-4 leading-relaxed">
                  {diagnosisResult.description}
                </p>

                {/* Causes */}
                {diagnosisResult.causes && (
                  <div className="mt-3.5 p-3 rounded-xl bg-field-950/40 border border-field-900/10 dark:border-mist/10 text-xs">
                    <span className="font-semibold text-amber-400 block mb-0.5">
                      Favorable Conditions & Vectors:
                    </span>
                    <span className="text-mist/70">{diagnosisResult.causes}</span>
                  </div>
                )}
              </div>

              {/* Symptoms Checklist */}
              {diagnosisResult.symptoms && diagnosisResult.symptoms.length > 0 && (
                <div className="card p-5 space-y-2.5">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-canopy flex items-center gap-1.5">
                    <Eye size={15} />
                    Observable Foliar Symptoms
                  </h3>
                  <div className="grid sm:grid-cols-2 gap-2">
                    {diagnosisResult.symptoms.map((symptom, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-2 p-2.5 rounded-xl bg-field-950/40 border border-field-900/10 dark:border-mist/10 text-xs text-mist/80"
                      >
                        <CheckCircle2 size={15} className="text-canopy shrink-0 mt-0.5" />
                        <span>{symptom}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Integrated Pest Management (IPM) Recommendations */}
              <div className="card p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <ShieldCheck size={18} className="text-canopy" />
                    Integrated Pest & Disease Management Plan
                  </h3>
                  <span className="text-[11px] text-mist/50">Agronomic Guidelines</span>
                </div>

                {/* Prevention */}
                {diagnosisResult.prevention && diagnosisResult.prevention.length > 0 && (
                  <div className="space-y-1.5">
                    <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider">
                      Cultural & Preventive Hygiene
                    </h4>
                    <ul className="space-y-1 text-xs text-mist/80 list-disc list-inside">
                      {diagnosisResult.prevention.map((item, idx) => (
                        <li key={idx}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Biological Controls */}
                {diagnosisResult.treatment?.biological &&
                  diagnosisResult.treatment.biological.length > 0 && (
                    <div className="space-y-1.5 p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/20">
                      <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Sprout size={13} />
                        Eco-Friendly & Biological Controls
                      </h4>
                      <ul className="space-y-1 text-xs text-mist/80 list-disc list-inside">
                        {diagnosisResult.treatment.biological.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                {/* Chemical Controls */}
                {diagnosisResult.treatment?.chemical &&
                  diagnosisResult.treatment.chemical.length > 0 && (
                    <div className="space-y-1.5 p-3.5 rounded-xl bg-rose-950/20 border border-alert/20">
                      <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Droplets size={13} />
                        Scientific Chemical Interventions (When ETL Exceeded)
                      </h4>
                      <ul className="space-y-1 text-xs text-mist/80 list-disc list-inside">
                        {diagnosisResult.treatment.chemical.map((item, idx) => (
                          <li key={idx}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
              </div>

              {/* Cross-Link Synergy: Link to Tabular Outbreak Predictor */}
              <div className="card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-canopy/30 bg-canopy/5">
                <div>
                  <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Compass size={16} className="text-canopy" />
                    Cross-Check Meteorological Outbreak Risk for {diagnosisResult.crop}
                  </h4>
                  <p className="text-xs text-mist/70 mt-0.5 max-w-xl">
                    Connect visual leaf diagnosis with live GPS weather telemetry to assess whether
                    current temperature and humidity conditions favor further spread across your field.
                  </p>
                </div>
                <Link
                  to={`/app/predict`}
                  className="btn-primary text-xs py-2 px-4 shrink-0 flex items-center gap-1.5"
                >
                  Predict Weather Risk
                  <ArrowRight size={14} />
                </Link>
              </div>

              {/* Alternative Prediction Candidates */}
              {diagnosisResult.top_candidates && diagnosisResult.top_candidates.length > 1 && (
                <div className="card p-4">
                  <h4 className="text-xs font-semibold text-mist/60 uppercase tracking-wider mb-2.5">
                    Class Probability Distribution (Top Matches)
                  </h4>
                  <div className="space-y-2">
                    {diagnosisResult.top_candidates.map((cand) => (
                      <div
                        key={cand.rank}
                        className="flex items-center justify-between text-xs p-2 rounded-lg bg-field-950/40 border border-field-900/10 dark:border-mist/10"
                      >
                        <span className="text-mist/80 font-medium">
                          #{cand.rank} {cand.crop} — {cand.disease}
                        </span>
                        <span className="font-mono text-canopy">{cand.confidence}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Recent History Table */}
      {recentHistory.length > 0 && (
        <div className="card p-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Activity size={16} className="text-canopy" />
              Recent Plant Diagnoses
            </h3>
            <span className="text-xs text-mist/50">{recentHistory.length} saved scans</span>
          </div>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {recentHistory.map((item) => (
              <div
                key={item.id}
                className="p-3 rounded-xl bg-field-950/50 border border-field-900/10 dark:border-mist/10 space-y-1"
              >
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-semibold text-canopy truncate">{item.crop_name}</span>
                  <span className="font-mono text-mist/60">{item.confidence}%</span>
                </div>
                <p className="text-xs text-white font-medium truncate">{item.disease_name}</p>
                <span
                  className={`inline-block px-1.5 py-0.5 rounded text-[10px] ${
                    item.is_healthy ? "bg-emerald-500/20 text-emerald-400" : "bg-clay/20 text-amber-400"
                  }`}
                >
                  {item.is_healthy ? "Healthy" : item.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

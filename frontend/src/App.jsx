
import { useEffect, useState } from "react";
import {
  Activity,
  Building2,
  LayoutDashboard,
  ScanSearch,
  History,
  Settings,
  Bell,
  Search,
  ArrowUpRight,
  CheckCircle2,
  AlertTriangle,
  ImagePlus,
  Upload,
  Cpu,
  Menu,
  X,
} from "lucide-react";
import "./App.css";

const API = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("Overview");
  const [modelStatus, setModelStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mobileMenu, setMobileMenu] = useState(false);

  async function loadDashboard() {
    try {
      const [statusResponse, historyResponse] = await Promise.all([
        fetch(`${API}/vision/model-status`),
        fetch(`${API}/vision/history`),
      ]);

      if (!statusResponse.ok || !historyResponse.ok) {
        throw new Error("Backend request failed");
      }

      const status = await statusResponse.json();
      const historyData = await historyResponse.json();

      setModelStatus(status);
      setHistory(historyData.inspections || []);
    } catch (error) {
      console.error("Dashboard API error:", error);
      setModelStatus(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
  let cancelled = false;

  async function fetchDashboard() {
    try {
      const [statusResponse, historyResponse] = await Promise.all([
        fetch(`${API}/vision/model-status`),
        fetch(`${API}/vision/history`),
      ]);

      if (!statusResponse.ok || !historyResponse.ok) {
        throw new Error("Backend request failed");
      }

      const status = await statusResponse.json();
      const historyData = await historyResponse.json();

      if (!cancelled) {
        setModelStatus(status);
        setHistory(historyData.inspections || []);
      }
    } catch (error) {
      console.error("Dashboard API error:", error);

      if (!cancelled) {
        setModelStatus(null);
      }
    } finally {
      if (!cancelled) {
        setLoading(false);
      }
    }
  }

  fetchDashboard();

  return () => {
    cancelled = true;
  };
}, []);

  const total = history.length;
  const cracked = history.filter(
    (item) => item.prediction === "cracked"
  ).length;
  const uncracked = history.filter(
    (item) => item.prediction === "uncracked"
  ).length;

  const navigation = [
    { name: "Overview", icon: LayoutDashboard },
    { name: "AI Analysis", icon: ScanSearch },
    { name: "Inspection History", icon: History },
  ];

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileMenu ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon">
            <Building2 size={23} />
          </div>
          <div>
            <h2>STRUCTURA<span>AI</span></h2>
            <p>STRUCTURAL INTELLIGENCE</p>
          </div>
          <button className="mobile-close" onClick={() => setMobileMenu(false)}>
            <X size={20} />
          </button>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav className="navigation">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.name}
                className={`nav-item ${activePage === item.name ? "active" : ""}`}
                onClick={() => {
                  setActivePage(item.name);
                  setMobileMenu(false);
                }}
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="system-card">
            <div className="system-card-title">
              <span className="status-dot" />
              System status
            </div>
            <p>{modelStatus?.status === "loaded" ? "AI Model Online" : "Backend Offline"}</p>
            <small>
              {modelStatus?.status === "loaded"
                ? "CNN model successfully loaded"
                : "Check FastAPI server"}
            </small>
          </div>
          <div className="sidebar-footer">
            <Settings size={17} />
            <span>Settings</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setMobileMenu(true)}
          >
            <Menu size={22} />
          </button>
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>{activePage}</strong>
          </div>
          <div className="topbar-actions">
            <div className="live-indicator">
              <span className="status-dot" />
              LIVE SYSTEM
            </div>
            <button className="icon-button" aria-label="Search">
              <Search size={19} />
            </button>
            <button className="icon-button" aria-label="Notifications">
              <Bell size={19} />
            </button>
            <div className="avatar">SA</div>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome-section">
            <div>
              <div className="eyebrow">STRUCTURAL HEALTH MONITORING</div>
              <h1>
                {activePage === "Overview"
                  ? "Engineering Overview"
                  : activePage}
              </h1>
              <p>
                Monitor concrete conditions and analyze structural images
                using artificial intelligence.
              </p>
            </div>
            <button className="refresh-button" onClick={loadDashboard}>
              <Activity size={17} />
              Refresh data
            </button>
          </section>

          {activePage === "Overview" && (
            <>
              <section className="metrics-grid">
                <MetricCard
                  title="Total Inspections"
                  value={loading ? "..." : total}
                  icon={<ScanSearch />}
                  color="green"
                  subtitle="Recorded inspections"
                />
                <MetricCard
                  title="Crack Detections"
                  value={loading ? "..." : cracked}
                  icon={<AlertTriangle />}
                  color="orange"
                  subtitle="Classified as cracked"
                />
                <MetricCard
                  title="Uncracked Results"
                  value={loading ? "..." : uncracked}
                  icon={<CheckCircle2 />}
                  color="blue"
                  subtitle="Classified as uncracked"
                />
                <MetricCard
                  title="Model Checkpoint"
                  value={modelStatus?.checkpoint_epoch ?? "--"}
                  icon={<Cpu />}
                  color="purple"
                  subtitle="CNN training epoch"
                />
              </section>

              <section className="content-grid">
                <div className="panel analysis-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>AI Concrete Analysis</h3>
                      <p>Start a new structural image inspection</p>
                    </div>
                    <span className="panel-icon"><ScanSearch size={20} /></span>
                  </div>
                  <div
                    className="upload-area"
                    onClick={() => setActivePage("AI Analysis")}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") setActivePage("AI Analysis");
                    }}
                  >
                    <div className="upload-icon">
                      <ImagePlus size={30} />
                    </div>
                    <h4>Analyze a concrete image</h4>
                    <p>Upload an image to detect possible concrete cracks.</p>
                    <button className="primary-button">
                      <Upload size={17} /> Open AI Analysis
                    </button>
                    <small>JPEG or PNG · Maximum 5 MB</small>
                  </div>
                </div>

                <div className="panel model-panel">
                  <div className="panel-heading">
                    <div>
                      <h3>AI Model Status</h3>
                      <p>Inference engine information</p>
                    </div>
                    <span className="panel-icon"><Cpu size={20} /></span>
                  </div>
                  <div className="model-status-row">
                    <span>Model</span>
                    <strong>{modelStatus?.model || "Unavailable"}</strong>
                  </div>
                  <div className="model-status-row">
                    <span>Checkpoint</span>
                    <strong>Epoch {modelStatus?.checkpoint_epoch ?? "--"}</strong>
                  </div>
                  <div className="model-status-row">
                    <span>Input dimensions</span>
                    <strong>{modelStatus?.image_size ? `${modelStatus.image_size} × ${modelStatus.image_size}` : "--"}</strong>
                  </div>
                  <div className="model-status-row">
                    <span>Inference device</span>
                    <strong>{modelStatus?.device || "--"}</strong>
                  </div>
                  <div className="model-online">
                    <span className="status-dot" />
                    {modelStatus?.status === "loaded"
                      ? "Model loaded and ready"
                      : "Model unavailable"}
                  </div>
                </div>
              </section>

              <HistoryPanel history={history.slice(0, 5)} />
            </>
          )}

          {activePage === "AI Analysis" && (
            <AnalysisPage onComplete={loadDashboard} />
          )}

          {activePage === "Inspection History" && (
            <HistoryPanel history={history} />
          )}

          <footer className="page-footer">
            <span>STRUCTURAAI · STRUCTURAL INTELLIGENCE PLATFORM</span>
            <span>AI-assisted experimental analysis · Not a safety assessment</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

function MetricCard({ title, value, icon, color, subtitle }) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span>{title}</span>
        <div className={`metric-icon ${color}`}>{icon}</div>
      </div>
      <h2>{value}</h2>
      <p><ArrowUpRight size={14} /> {subtitle}</p>
    </div>
  );
}

function HistoryPanel({ history }) {
  return (
    <section className="panel history-panel">
      <div className="panel-heading">
        <div>
          <h3>Recent Inspections</h3>
          <p>Previously analyzed concrete images</p>
        </div>
        <span className="record-count">{history.length} records</span>
      </div>

      {history.length === 0 ? (
        <div className="empty-state">
          No inspection records available yet.
        </div>
      ) : (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>IMAGE</th>
                <th>FILENAME</th>
                <th>RESULT</th>
                <th>CRACK PROBABILITY</th>
                <th>CONFIDENCE</th>
                <th>DATE</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={item.id}>
                  <td><div className="file-symbol"><ImagePlus size={17} /></div></td>
                  <td className="filename">{item.filename}</td>
                  <td>
                    <span className={`result-badge ${item.prediction}`}>
                      {item.prediction}
                    </span>
                  </td>
                  <td>{(item.crack_probability * 100).toFixed(1)}%</td>
                  <td>{(item.confidence * 100).toFixed(1)}%</td>
                  <td>{item.created_at ? new Date(item.created_at.replace(" ", "T") + "Z").toLocaleDateString() : "--"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function AnalysisPage({ onComplete }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [analyzing, setAnalyzing] = useState(false);

  function selectFile(selectedFile) {
    setResult(null);
    setError("");

    if (!selectedFile) return;

    if (!["image/jpeg", "image/png"].includes(selectedFile.type)) {
      setError("Please select a JPEG or PNG image.");
      return;
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      setError("Image must be smaller than 5 MB.");
      return;
    }

    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  }

  async function analyzeImage() {
    if (!file) return;

    setAnalyzing(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API}/vision/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Image analysis failed.");
      }

      setResult(data);
      onComplete();
    } catch (err) {
      setError(err.message || "Could not connect to the backend.");
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <section className="analysis-layout">
      <div className="panel analysis-workspace">
        <div className="panel-heading">
          <div>
            <h3>Concrete Image Inspection</h3>
            <p>Select a concrete surface image for AI analysis.</p>
          </div>
          <ScanSearch size={22} />
        </div>

        <label className="file-drop">
          <input
            type="file"
            accept="image/jpeg,image/png"
            onChange={(event) => selectFile(event.target.files[0])}
          />
          {preview ? (
            <img src={preview} alt="Selected concrete preview" />
          ) : (
            <>
              <ImagePlus size={38} />
              <strong>Choose a concrete image</strong>
              <span>JPEG or PNG · Maximum 5 MB</span>
            </>
          )}
        </label>

        {file && <p className="selected-file">Selected: {file.name}</p>}

        <button
          className="primary-button analyze-button"
          disabled={!file || analyzing}
          onClick={analyzeImage}
        >
          <ScanSearch size={18} />
          {analyzing ? "Analyzing image..." : "Run AI Analysis"}
        </button>

        {error && <div className="error-message">{error}</div>}
      </div>

      <div className="panel result-panel">
        <div className="panel-heading">
          <div>
            <h3>Analysis Results</h3>
            <p>CNN classification output</p>
          </div>
          <Activity size={22} />
        </div>

        {!result ? (
          <div className="empty-state result-empty">
            <ScanSearch size={36} />
            <strong>Waiting for analysis</strong>
            <span>Upload an image and run the model.</span>
          </div>
        ) : (
          <div className="result-content">
            <span className={`result-badge ${result.analysis.prediction}`}>
              {result.analysis.prediction}
            </span>
            <div className="probability-value">
              {(result.analysis.crack_probability * 100).toFixed(2)}%
            </div>
            <p>Crack probability</p>
            <div className="probability-track">
              <div
                style={{ width: `${result.analysis.crack_probability * 100}%` }}
              />
            </div>
            <div className="model-status-row">
              <span>Confidence</span>
              <strong>{(result.analysis.confidence * 100).toFixed(2)}%</strong>
            </div>
            <div className="model-status-row">
              <span>Model epoch</span>
              <strong>{result.analysis.model_epoch}</strong>
            </div>
            <div className="model-status-row">
              <span>Inspection ID</span>
              <strong>{result.inspection_id}</strong>
            </div>
            <p className="disclaimer">
              Experimental AI classification only. This result is not a
              structural safety assessment.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}

export default App;

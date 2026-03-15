import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import axios from "axios";

const API = "http://localhost:8000";

const NODE_ICONS = {
  planner: "🔍",
  human_review: "👤",
  code_writer: "✍️",
  executor: "⚙️",
  analyst: "📊",
  refiner: "🔄",
  report_writer: "📝",
};

const NODE_LABELS = {
  planner: "PLANNER",
  human_review: "HUMAN REVIEW",
  code_writer: "CODE WRITER",
  executor: "EXECUTOR",
  analyst: "ANALYST",
  refiner: "REFINER",
  report_writer: "REPORT WRITER",
};

const EXAMPLES = [
  "Gold rises when the dollar weakens",
  "Bitcoin drops after Fed rate hikes",
  "SPY momentum — buy after 3 green months",
  "VIX spikes predict market crashes",
  "S&P500 has positive returns over any rolling 10-year period"
];

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Bebas+Neue&family=DM+Mono:wght@400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --black: #0a0a0a;
    --white: #f5f0e8;
    --yellow: #FFE500;
    --red: #FF2D2D;
    --green: #00E676;
    --border: 3px solid #0a0a0a;
    --shadow: 5px 5px 0px #0a0a0a;
    --shadow-lg: 8px 8px 0px #0a0a0a;
    --font-display: 'Bebas Neue', sans-serif;
    --font-mono: 'DM Mono', monospace;
    --font-body: 'Space Mono', monospace;
  }

  html, body, #root {
    height: 100%;
    background: var(--white);
    color: var(--black);
    font-family: var(--font-body);
  }

  ::-webkit-scrollbar { width: 8px; }
  ::-webkit-scrollbar-track { background: var(--white); border-left: 2px solid var(--black); }
  ::-webkit-scrollbar-thumb { background: var(--black); }

  .app-wrapper {
    min-height: 100vh;
    background: var(--white);
    background-image: radial-gradient(circle, #0a0a0a 1px, transparent 1px);
    background-size: 24px 24px;
    background-attachment: fixed;
  }

  .header {
    background: var(--black);
    border-bottom: var(--border);
    padding: 0 40px;
    display: flex;
    align-items: stretch;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    min-height: 72px;
  }

  .header-brand {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 12px 0;
  }

  .header-title {
    font-family: var(--font-display);
    font-size: 42px;
    color: var(--yellow);
    letter-spacing: 2px;
    line-height: 1;
  }

  .header-sub {
    font-family: var(--font-mono);
    font-size: 10px;
    color: #666;
    letter-spacing: 2px;
    margin-top: 2px;
    text-transform: uppercase;
  }

  .nav-tabs {
    display: flex;
    align-items: stretch;
    gap: 0;
  }

  .nav-tab {
    font-family: var(--font-display);
    font-size: 20px;
    letter-spacing: 2px;
    padding: 0 28px;
    cursor: pointer;
    border: none;
    border-left: 2px solid #222;
    background: transparent;
    color: #555;
    transition: background 0.1s, color 0.1s;
    text-transform: uppercase;
  }

  .nav-tab:hover { background: #1a1a1a; color: var(--white); }
  .nav-tab.active { background: var(--yellow); color: var(--black); border-left-color: var(--yellow); }

  .main {
    max-width: 1160px;
    margin: 0 auto;
    padding: 36px 24px;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .card {
    background: var(--white);
    border: var(--border);
    box-shadow: var(--shadow-lg);
    border-radius: 0;
    padding: 28px;
  }

  .card-title {
    font-family: var(--font-display);
    font-size: 22px;
    letter-spacing: 2px;
    border-bottom: 3px solid var(--black);
    padding-bottom: 10px;
    margin-bottom: 20px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .card-title-dot {
    width: 14px;
    height: 14px;
    background: var(--yellow);
    border: 2px solid var(--black);
    display: inline-block;
    flex-shrink: 0;
  }

  .examples-row {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 10px;
  }

  .example-chip {
    padding: 4px 10px;
    border: 2px solid var(--black);
    background: var(--black);
    color: #888;
    font-family: var(--font-mono);
    font-size: 10px;
    letter-spacing: 1px;
    cursor: pointer;
    transition: color 0.1s, background 0.1s;
  }

  .example-chip:hover { background: #222; color: var(--yellow); }

  .input-row {
    display: flex;
    gap: 0;
  }

  .input-hypothesis {
    flex: 1;
    padding: 14px 18px;
    border: var(--border);
    border-right: none;
    background: var(--black);
    color: var(--yellow);
    font-family: var(--font-mono);
    font-size: 14px;
    outline: none;
  }

  .input-hypothesis::placeholder { color: #555; }
  .input-hypothesis:focus { background: #111; box-shadow: inset 0 0 0 2px var(--yellow); }

  .select-ref {
    padding: 14px 16px;
    border: var(--border);
    border-right: none;
    background: var(--black);
    color: #aaa;
    font-family: var(--font-mono);
    font-size: 12px;
    cursor: pointer;
    outline: none;
    appearance: none;
    -webkit-appearance: none;
    min-width: 140px;
    text-align: center;
  }

  .select-ref:focus { box-shadow: inset 0 0 0 2px var(--yellow)); }

  .btn-run {
    padding: 14px 32px;
    border: var(--border);
    background: var(--yellow);
    color: var(--black);
    font-family: var(--font-display);
    font-size: 22px;
    letter-spacing: 2px;
    cursor: pointer;
    transition: transform 0.08s, box-shadow 0.08s;
    white-space: nowrap;
  }

  .btn-run:hover:not(:disabled) { transform: translate(-2px, -2px); box-shadow: 7px 7px 0 var(--black); }
  .btn-run:active:not(:disabled) { transform: translate(2px, 2px); box-shadow: 3px 3px 0 var(--black); }
  .btn-run:disabled { background: #ddd; color: #999; cursor: not-allowed; }
  .btn-run.running { background: var(--black); color: var(--yellow); animation: pulse-btn 1.2s ease-in-out infinite; }

  @keyframes pulse-btn {
    0%, 100% { box-shadow: 5px 5px 0 var(--yellow); }
    50% { box-shadow: 3px 3px 0 var(--yellow); }
  }

  .two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }

  .log-feed {
    height: 300px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding-right: 4px;
  }

  .log-empty {
    font-family: var(--font-mono);
    font-size: 12px;
    color: #bbb;
    border: 2px dashed #ccc;
    padding: 20px;
    text-align: center;
    letter-spacing: 1px;
  }

  .log-entry {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border: 2px solid var(--black);
    background: var(--black);
    font-family: var(--font-mono);
    font-size: 11px;
    animation: slide-in 0.2s ease-out;
  }

  @keyframes slide-in {
    from { transform: translateX(-8px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }

  .log-icon { font-size: 14px; }

  .log-node {
    color: var(--yellow);
    font-weight: 700;
    letter-spacing: 1px;
    min-width: 110px;
    text-transform: uppercase;
    font-size: 10px;
  }

  .log-iter {
    color: #555;
    font-size: 10px;
    background: #1a1a1a;
    padding: 2px 6px;
    border: 1px solid #333;
  }

  .log-time {
    margin-left: auto;
    color: #444;
    font-size: 10px;
    font-family: var(--font-mono);
  }

  .status-empty {
    font-family: var(--font-mono);
    font-size: 12px;
    color: #bbb;
    border: 2px dashed #ccc;
    padding: 20px;
    text-align: center;
    letter-spacing: 1px;
  }

  .status-grid {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .status-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border: 2px solid var(--black);
    border-top: none;
    background: var(--white);
  }

  .status-row:first-child { border-top: 2px solid var(--black); }
  .status-row:nth-child(even) { background: #f0ebe0; }

  .status-label {
    font-family: var(--font-mono);
    font-size: 11px;
    color: #666;
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .status-value {
    font-family: var(--font-display);
    font-size: 18px;
    letter-spacing: 1px;
  }

  .status-value.mono {
    font-family: var(--font-mono);
    font-size: 11px;
  }

  .badge {
    display: inline-block;
    padding: 4px 12px;
    border: 2px solid var(--black);
    font-family: var(--font-display);
    font-size: 16px;
    letter-spacing: 2px;
  }

  .badge.running { background: #FFE500; color: var(--black); animation: blink-badge 1s step-end infinite; }
  .badge.completed { background: var(--green); color: var(--black); }
  .badge.failed { background: var(--red); color: var(--white); }
  .badge.pending { background: #ccc; color: var(--black); }

  @keyframes blink-badge {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  .verdict-strong { color: var(--green); }
  .verdict-weak { color: #e0a000; }

  .error-box {
    background: #2a0a0a;
    border: 2px solid var(--red);
    padding: 12px 16px;
    margin-top: 10px;
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--red);
    letter-spacing: 1px;
  }

  .report-body {
    background: var(--black);
    border: var(--border);
    padding: 28px;
    max-height: 520px;
    overflow-y: auto;
    font-family: var(--font-mono);
    font-size: 13px;
    line-height: 1.75;
    color: #d4d0c8;
  }

  .report-body h1, .report-body h2, .report-body h3 {
    font-family: var(--font-display);
    color: var(--yellow);
    letter-spacing: 2px;
    margin: 20px 0 8px;
  }

  .report-body h1 { font-size: 30px; }
  .report-body h2 { font-size: 24px; border-bottom: 2px solid #333; padding-bottom: 6px; }
  .report-body h3 { font-size: 20px; }
  .report-body p { margin-bottom: 12px; }
  .report-body strong { color: var(--white); }
  .report-body code { background: #1a1a1a; border: 1px solid #333; padding: 1px 6px; color: var(--yellow); border-radius: 0; }
  .report-body pre { background: #111; border: 2px solid #333; padding: 16px; overflow-x: auto; margin: 12px 0; }
  .report-body ul, .report-body ol { padding-left: 20px; margin-bottom: 12px; }
  .report-body li { margin-bottom: 4px; }
  .report-body blockquote { border-left: 4px solid var(--yellow); padding-left: 16px; color: #888; margin: 12px 0; }

  .chart-img {
    width: 100%;
    border: var(--border);
    display: block;
  }

  .grave-item {
    border: var(--border);
    box-shadow: var(--shadow);
    padding: 0;
    background: var(--white);
    transition: transform 0.1s, box-shadow 0.1s;
    margin-bottom: 16px;
    cursor: pointer;
  }

  .grave-item:hover { transform: translate(-3px, -3px); box-shadow: var(--shadow-lg); }

  .grave-header {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    border-bottom: var(--border);
    background: var(--black);
  }

  .grave-hypothesis {
    font-family: var(--font-mono);
    font-size: 13px;
    color: var(--white);
    padding: 14px 18px;
    flex: 1;
  }

  .grave-verdict-tag {
    font-family: var(--font-display);
    font-size: 18px;
    letter-spacing: 2px;
    padding: 14px 20px;
    border-left: var(--border);
    display: flex;
    align-items: center;
    white-space: nowrap;
  }

  .grave-verdict-tag.strong { background: var(--green); color: var(--black); }
  .grave-verdict-tag.weak { background: var(--yellow); color: var(--black); }
  .grave-verdict-tag.none { background: #333; color: #888; }

  .grave-stats {
    display: flex;
    gap: 0;
    padding: 0;
  }

  .grave-stat {
    flex: 1;
    padding: 14px 18px;
    border-right: var(--border);
    font-family: var(--font-mono);
    font-size: 11px;
  }

  .grave-stat:last-child { border-right: none; }
  .grave-stat-label { color: #888; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }
  .grave-stat-val { font-size: 16px; font-weight: 700; }
  .grave-stat-val.pos { color: var(--green); }
  .grave-stat-val.neg { color: var(--red); }
  .grave-stat-val.neutral { color: var(--black); }

  .grave-reasoning {
    padding: 18px 18px;
    border-top: var(--border);
    background: #f0ebe0;
    font-family: var(--font-mono);
    font-size: 11px;
    color: #555;
    line-height: 1.7;
    animation: slide-in 0.2s ease-out;
  }

  .grave-reasoning strong { color: var(--black); }

  .btn-view-report {
    margin-top: 16px;
    padding: 8px 20px;
    border: 2px solid var(--black);
    font-family: var(--font-display);
    font-size: 16px;
    letter-spacing: 2px;
    cursor: pointer;
    transition: transform 0.08s, box-shadow 0.08s;
    display: inline-block;
  }

  .btn-view-report:hover { transform: translate(-2px, -2px); box-shadow: 4px 4px 0 var(--black); }
  .btn-view-report:active { transform: translate(1px, 1px); box-shadow: 2px 2px 0 var(--black); }
  .btn-view-report.show { background: var(--black); color: var(--yellow); }
  .btn-view-report.hide { background: var(--yellow); color: var(--black); }

  .grave-report-wrapper {
    margin-top: 16px;
    animation: slide-in 0.2s ease-out;
  }

  .job-item {
    border: var(--border);
    box-shadow: var(--shadow);
    padding: 0;
    background: var(--white);
    cursor: pointer;
    transition: transform 0.1s, box-shadow 0.1s;
    margin-bottom: 12px;
    display: flex;
    align-items: stretch;
  }

  .job-item:hover { transform: translate(-3px, -3px); box-shadow: var(--shadow-lg); }

  .job-status-bar { width: 8px; flex-shrink: 0; }
  .job-status-bar.completed { background: var(--green); }
  .job-status-bar.failed { background: var(--red); }
  .job-status-bar.running { background: var(--yellow); animation: blink-bar 1s step-end infinite; }
  .job-status-bar.pending { background: #ccc; }

  @keyframes blink-bar {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  .job-body { flex: 1; padding: 14px 20px; border-left: var(--border); }
  .job-hypothesis { font-family: var(--font-mono); font-size: 13px; color: var(--black); margin-bottom: 4px; }
  .job-id { font-family: var(--font-mono); font-size: 10px; color: #aaa; letter-spacing: 1px; }

  .job-meta {
    display: flex;
    gap: 16px;
    padding: 14px 20px;
    align-items: center;
    border-left: var(--border);
    background: #f5f0e8;
  }

  .job-verdict { font-family: var(--font-display); font-size: 18px; letter-spacing: 2px; }
  .job-status-label { font-family: var(--font-mono); font-size: 11px; letter-spacing: 1px; text-transform: uppercase; }

  .ticker-strip {
    background: var(--black);
    border-top: var(--border);
    border-bottom: var(--border);
    overflow: hidden;
    white-space: nowrap;
    padding: 8px 0;
  }

  .ticker-inner { display: inline-block; animation: ticker 20s linear infinite; }

  @keyframes ticker {
    from { transform: translateX(0); }
    to { transform: translateX(-50%); }
  }

  .ticker-item { font-family: var(--font-mono); font-size: 11px; color: var(--yellow); letter-spacing: 2px; margin: 0 32px; }

  .empty-state { text-align: center; padding: 48px 24px; border: 3px dashed #ccc; }
  .empty-state-icon { font-size: 40px; margin-bottom: 12px; }
  .empty-state-text { font-family: var(--font-mono); font-size: 12px; color: #aaa; letter-spacing: 2px; text-transform: uppercase; }

  @media (max-width: 768px) {
    .two-col { grid-template-columns: 1fr; }
    .header { padding: 0 16px; flex-direction: column; align-items: flex-start; }
    .nav-tabs { width: 100%; }
    .nav-tab { flex: 1; text-align: center; border-left: none; border-top: 2px solid #222; }
    .input-row { flex-direction: column; }
    .input-hypothesis, .select-ref, .btn-run { border-right: var(--border); border-top: none; }
    .input-hypothesis { border-top: var(--border); border-right: var(--border); }
    .btn-run { width: 100%; }
  }
`;

export default function App() {
  const [hypothesis, setHypothesis] = useState("");
  const [maxRef, setMaxRef] = useState(2);
  const [jobId, setJobId] = useState(null);
  const [job, setJob] = useState(null);
  const [logs, setLogs] = useState([]);
  const [report, setReport] = useState("");
  const [chartUrl, setChartUrl] = useState("");
  const [graveyard, setGraveyard] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [tab, setTab] = useState("research");
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);
  const [expanded, setExpanded] = useState(null);
  const [graveyardReport, setGraveyardReport] = useState("");
  const [graveyardReportId, setGraveyardReportId] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const pollRef = useRef(null);
  const logsEndRef = useRef(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  useEffect(() => {
    if (!polling || !jobId) return;
    pollRef.current = setInterval(async () => {
      try {
        const [statusRes, logsRes] = await Promise.all([
          axios.get(`${API}/research/${jobId}`),
          axios.get(`${API}/research/${jobId}/logs`),
        ]);
        setJob(statusRes.data);
        setLogs(logsRes.data.logs || []);

        if (["completed", "failed"].includes(statusRes.data.status)) {
          setPolling(false);
          clearInterval(pollRef.current);
          if (statusRes.data.status === "completed") {
            try {
              const repRes = await axios.get(`${API}/research/${jobId}/report`);
              setReport(repRes.data.report || "");
            } catch {}
            setChartUrl(`${API}/research/${jobId}/chart?t=${Date.now()}`);
            fetchGraveyard();
            fetchJobs();
          }
        }
      } catch {}
    }, 3000);
    return () => clearInterval(pollRef.current);
  }, [polling, jobId]);

  const fetchGraveyard = async () => {
    const res = await axios.get(`${API}/graveyard`);
    setGraveyard(res.data.entries || []);
  };

  const fetchJobs = async () => {
    const res = await axios.get(`${API}/jobs`);
    setJobs(res.data.jobs || []);
  };

  useEffect(() => {
    fetchGraveyard();
    fetchJobs();
  }, []);

  const startResearch = async () => {
    if (!hypothesis.trim()) return;
    setLoading(true);
    setJob(null);
    setLogs([]);
    setReport("");
    setChartUrl("");
    try {
      const res = await axios.post(`${API}/research`, {
        hypothesis,
        max_refinements: maxRef,
        auto_approve: true,
      });
      setJobId(res.data.job_id);
      setPolling(true);
      setTab("research");
    } catch (e) {
      alert("Failed to start research: " + e.message);
    }
    setLoading(false);
  };

  const handleViewReport = async (e, entryId) => {
    e.stopPropagation();
    if (graveyardReportId === entryId) {
      setGraveyardReport("");
      setGraveyardReportId(null);
      return;
    }
    setReportLoading(true);
    try {
      const res = await axios.get(`${API}/graveyard/${entryId}/report`);
      setGraveyardReport(res.data.report || "");
      setGraveyardReportId(entryId);
    } catch {
      setGraveyardReport("⚠ Report file not found for this entry.");
      setGraveyardReportId(entryId);
    }
    setReportLoading(false);
  };

  const getStatusClass = (s) => {
    if (!s) return "pending";
    if (s === "completed") return "completed";
    if (s === "failed") return "failed";
    if (s === "running") return "running";
    return "pending";
  };

  const verdictClass = (v) => {
    if (!v) return "";
    return v.toLowerCase() === "strong" ? "verdict-strong" : "verdict-weak";
  };

  const graveyardVerdictClass = (v) => {
    if (!v) return "none";
    return v.toLowerCase() === "strong" ? "strong" : "weak";
  };

  const tickerItems = [
    "⚡ QUANT RESEARCH AGENT",
    "◆ LANGGRAPH + GPT-5-mini + E2B",
    "◆ AUTOMATED HYPOTHESIS TESTING",
    "◆ LIVE AGENT ORCHESTRATION",
    "◆ REAL-TIME BACKTESTING",
    "◆ SHARPE RATIO ANALYSIS",
    "⚡ QUANT RESEARCH AGENT",
    "◆ LANGGRAPH + GPT-4O + E2B",
    "◆ AUTOMATED HYPOTHESIS TESTING",
    "◆ LIVE AGENT ORCHESTRATION",
    "◆ REAL-TIME BACKTESTING",
    "◆ SHARPE RATIO ANALYSIS",
  ];

  return (
    <>
      <style>{styles}</style>
      <div className="app-wrapper">
        <header className="header">
          <div className="header-brand">
            <div className="header-title">⚡ QUANT RESEARCH AGENT</div>
            <div className="header-sub">
              LANGGRAPH · GPT-4O · E2B · BACKTESTING ENGINE
            </div>
          </div>
          <nav className="nav-tabs">
            {[
              { id: "research", label: "RESEARCH", icon: "◈" },
              { id: "graveyard", label: "GRAVEYARD", icon: "💀" },
              { id: "jobs", label: "ALL JOBS", icon: "▤" },
            ].map((t) => (
              <button
                key={t.id}
                className={`nav-tab ${tab === t.id ? "active" : ""}`}
                onClick={() => {
                  setTab(t.id);
                  if (t.id === "graveyard") fetchGraveyard();
                  if (t.id === "jobs") fetchJobs();
                }}
              >
                {t.icon} {t.label}
              </button>
            ))}
          </nav>
        </header>

        <div className="ticker-strip">
          <div className="ticker-inner">
            {tickerItems.map((item, i) => (
              <span key={i} className="ticker-item">
                {item}
              </span>
            ))}
          </div>
        </div>

        <main className="main">
          {/* ── RESEARCH TAB ── */}
          {tab === "research" && (
            <>
              <div className="card">
                <div className="card-title">
                  <span className="card-title-dot" />
                  INPUT HYPOTHESIS
                </div>
                <div className="examples-row">
                  {EXAMPLES.map((ex) => (
                    <button
                      key={ex}
                      className="example-chip"
                      onClick={() => setHypothesis(ex)}
                    >
                      {ex}
                    </button>
                  ))}
                </div>
                <div className="input-row">
                  <input
                    className="input-hypothesis"
                    value={hypothesis}
                    onChange={(e) => setHypothesis(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && startResearch()}
                    placeholder='e.g. "Gold rises when the dollar weakens"'
                  />
                  <select
                    className="select-ref"
                    value={maxRef}
                    onChange={(e) => setMaxRef(Number(e.target.value))}
                  >
                    {[1, 2, 3].map((n) => (
                      <option key={n} value={n}>
                        MAX {n} REF{n > 1 ? "S" : ""}
                      </option>
                    ))}
                  </select>
                  <button
                    className={`btn-run ${polling ? "running" : ""}`}
                    onClick={startResearch}
                    disabled={loading || polling}
                  >
                    {loading
                      ? "⏳ STARTING..."
                      : polling
                        ? "⚙️ RUNNING"
                        : "▶ RUN"}
                  </button>
                </div>
              </div>

              <div className="two-col">
                <div className="card">
                  <div className="card-title">
                    <span
                      className="card-title-dot"
                      style={{
                        background: polling ? "var(--green)" : "var(--yellow)",
                        animation: polling
                          ? "blink-badge 0.8s step-end infinite"
                          : "none",
                      }}
                    />
                    LIVE AGENT ACTIVITY
                  </div>
                  <div className="log-feed">
                    {logs.length === 0 ? (
                      <div className="log-empty">
                        WAITING FOR AGENT SIGNALS...
                      </div>
                    ) : (
                      logs.map((log, i) => (
                        <div key={i} className="log-entry">
                          <span className="log-icon">
                            {NODE_ICONS[log.node] || "●"}
                          </span>
                          <span className="log-node">
                            {NODE_LABELS[log.node] || log.node}
                          </span>
                          <span className="log-iter">ITER {log.iteration}</span>
                          <span className="log-time">
                            {log.timestamp?.slice(11, 19)}
                          </span>
                        </div>
                      ))
                    )}
                    <div ref={logsEndRef} />
                  </div>
                </div>

                <div className="card">
                  <div className="card-title">
                    <span className="card-title-dot" />
                    RESEARCH STATUS
                  </div>
                  {!job ? (
                    <div className="status-empty">
                      NO ACTIVE JOB — RUN A HYPOTHESIS TO BEGIN
                    </div>
                  ) : (
                    <div className="status-grid">
                      <div className="status-row">
                        <span className="status-label">Status</span>
                        <span className={`badge ${getStatusClass(job.status)}`}>
                          {job.status?.toUpperCase()}
                        </span>
                      </div>
                      <div className="status-row">
                        <span className="status-label">Job ID</span>
                        <span className="status-value mono">{job.job_id}</span>
                      </div>
                      {job.verdict && (
                        <div className="status-row">
                          <span className="status-label">Verdict</span>
                          <span
                            className={`status-value ${verdictClass(job.verdict)}`}
                          >
                            {job.verdict?.toUpperCase()}
                          </span>
                        </div>
                      )}
                      {job.sharpe_ratio != null && (
                        <div className="status-row">
                          <span className="status-label">Sharpe Ratio</span>
                          <span
                            className="status-value"
                            style={{
                              color:
                                job.sharpe_ratio > 0.3
                                  ? "var(--green)"
                                  : "var(--red)",
                            }}
                          >
                            {job.sharpe_ratio?.toFixed(3)}
                          </span>
                        </div>
                      )}
                      {job.total_return != null && (
                        <div className="status-row">
                          <span className="status-label">Total Return</span>
                          <span
                            className="status-value"
                            style={{
                              color:
                                job.total_return > 0
                                  ? "var(--green)"
                                  : "var(--red)",
                            }}
                          >
                            {job.total_return > 0 ? "+" : ""}
                            {job.total_return?.toFixed(2)}%
                          </span>
                        </div>
                      )}
                      {job.n_trades != null && (
                        <div className="status-row">
                          <span className="status-label">Trades</span>
                          <span className="status-value">{job.n_trades}</span>
                        </div>
                      )}
                      {job.iterations != null && (
                        <div className="status-row">
                          <span className="status-label">Iterations</span>
                          <span className="status-value">{job.iterations}</span>
                        </div>
                      )}
                      {job.status === "failed" && (
                        <div className="error-box">
                          ⚠ JOB FAILED — CHECK API LOGS FOR DETAILS
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {chartUrl && (
                <div className="card">
                  <div className="card-title">
                    <span
                      className="card-title-dot"
                      style={{ background: "var(--green)" }}
                    />
                    BACKTEST CHART
                  </div>
                  <img
                    src={chartUrl}
                    alt="Backtest Chart"
                    className="chart-img"
                    onError={() => setChartUrl("")}
                  />
                </div>
              )}

              {report && (
                <div className="card">
                  <div className="card-title">
                    <span
                      className="card-title-dot"
                      style={{ background: "var(--green)" }}
                    />
                    RESEARCH REPORT
                  </div>
                  <div className="report-body">
                    <ReactMarkdown>{report}</ReactMarkdown>
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── GRAVEYARD TAB ── */}
          {tab === "graveyard" && (
            <div>
              <div
                className="card"
                style={{ padding: "16px 28px", marginBottom: 0 }}
              >
                <div className="card-title" style={{ marginBottom: 0 }}>
                  <span
                    className="card-title-dot"
                    style={{ background: "var(--red)" }}
                  />
                  HYPOTHESIS GRAVEYARD
                  <span
                    style={{
                      marginLeft: "auto",
                      fontFamily: "var(--font-mono)",
                      fontSize: 12,
                      color: "#888",
                    }}
                  >
                    {graveyard.length} ENTRIES
                  </span>
                </div>
              </div>

              <div style={{ marginTop: 16 }}>
                {graveyard.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-state-icon">💀</div>
                    <div className="empty-state-text">
                      NO HYPOTHESES BURIED YET
                    </div>
                  </div>
                ) : (
                  graveyard.map((entry) => (
                    <div
                      key={entry.id}
                      className="grave-item"
                      onClick={() => {
                        if (expanded === entry.id) {
                          setExpanded(null);
                          setGraveyardReport("");
                          setGraveyardReportId(null);
                        } else {
                          setExpanded(entry.id);
                          setGraveyardReport("");
                          setGraveyardReportId(null);
                        }
                      }}
                    >
                      <div className="grave-header">
                        <div className="grave-hypothesis">
                          {entry.original_hypothesis}
                        </div>
                        <div
                          className={`grave-verdict-tag ${graveyardVerdictClass(entry.verdict)}`}
                        >
                          {entry.verdict?.toUpperCase() || "N/A"}
                        </div>
                      </div>
                      <div className="grave-stats">
                        <div className="grave-stat">
                          <div className="grave-stat-label">Sharpe</div>
                          <div
                            className={`grave-stat-val ${entry.sharpe_ratio > 0.3 ? "pos" : "neg"}`}
                          >
                            {entry.sharpe_ratio?.toFixed(3) ?? "N/A"}
                          </div>
                        </div>
                        <div className="grave-stat">
                          <div className="grave-stat-label">Return</div>
                          <div
                            className={`grave-stat-val ${entry.total_return > 0 ? "pos" : "neg"}`}
                          >
                            {entry.total_return != null
                              ? `${entry.total_return > 0 ? "+" : ""}${entry.total_return.toFixed(1)}%`
                              : "N/A"}
                          </div>
                        </div>
                        <div className="grave-stat">
                          <div className="grave-stat-label">Trades</div>
                          <div className="grave-stat-val neutral">
                            {entry.n_trades ?? "N/A"}
                          </div>
                        </div>
                        <div className="grave-stat">
                          <div className="grave-stat-label">Iterations</div>
                          <div className="grave-stat-val neutral">
                            {entry.iterations}
                          </div>
                        </div>
                        <div
                          className="grave-stat"
                          style={{ textAlign: "right" }}
                        >
                          <div className="grave-stat-label">Date</div>
                          <div
                            className="grave-stat-val neutral"
                            style={{ fontSize: 12 }}
                          >
                            {entry.timestamp?.slice(0, 10)}
                          </div>
                        </div>
                      </div>

                      {/* Expanded reasoning + report viewer */}
                      {expanded === entry.id && (
                        <div className="grave-reasoning">
                          {entry.reasoning && (
                            <>
                              <strong>ANALYST REASONING:</strong>
                              <br />
                              <br />
                              {entry.reasoning}
                            </>
                          )}
                          {entry.suggested_refinement && (
                            <>
                              <br />
                              <br />
                              <strong>SUGGESTED NEXT:</strong>
                              <br />
                              {entry.suggested_refinement}
                            </>
                          )}

                          {/* View Report Button */}
                          <div style={{ marginTop: 16 }}>
                            <button
                              className={`btn-view-report ${graveyardReportId === entry.id ? "hide" : "show"}`}
                              onClick={(e) => handleViewReport(e, entry.id)}
                            >
                              {reportLoading && graveyardReportId !== entry.id
                                ? "⏳ LOADING..."
                                : graveyardReportId === entry.id
                                  ? "▲ HIDE REPORT"
                                  : "▼ VIEW REPORT"}
                            </button>
                          </div>

                          {/* Inline Report */}
                          {graveyardReportId === entry.id &&
                            graveyardReport && (
                              <div className="grave-report-wrapper">
                                <div className="report-body">
                                  <ReactMarkdown>
                                    {graveyardReport}
                                  </ReactMarkdown>
                                </div>
                              </div>
                            )}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* ── JOBS TAB ── */}
          {tab === "jobs" && (
            <div>
              <div
                className="card"
                style={{ padding: "16px 28px", marginBottom: 0 }}
              >
                <div className="card-title" style={{ marginBottom: 0 }}>
                  <span className="card-title-dot" />
                  ALL RESEARCH JOBS
                  <span
                    style={{
                      marginLeft: "auto",
                      fontFamily: "var(--font-mono)",
                      fontSize: 12,
                      color: "#888",
                    }}
                  >
                    {jobs.length} TOTAL
                  </span>
                </div>
              </div>

              <div style={{ marginTop: 16 }}>
                {jobs.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-state-icon">▤</div>
                    <div className="empty-state-text">
                      NO JOBS FOUND — RUN YOUR FIRST HYPOTHESIS
                    </div>
                  </div>
                ) : (
                  jobs.map((j) => (
                    <div
                      key={j.job_id}
                      className="job-item"
                      onClick={() => {
                        setJobId(j.job_id);
                        setTab("research");
                      }}
                    >
                      <div
                        className={`job-status-bar ${getStatusClass(j.status)}`}
                      />
                      <div className="job-body">
                        <div className="job-hypothesis">{j.hypothesis}</div>
                        <div className="job-id">{j.job_id}</div>
                      </div>
                      <div className="job-meta">
                        {j.verdict && (
                          <span
                            className={`job-verdict ${verdictClass(j.verdict)}`}
                          >
                            {j.verdict?.toUpperCase()}
                          </span>
                        )}
                        <span
                          className="job-status-label"
                          style={{
                            color:
                              j.status === "completed"
                                ? "var(--green)"
                                : j.status === "failed"
                                  ? "var(--red)"
                                  : j.status === "running"
                                    ? "#e0a000"
                                    : "#aaa",
                          }}
                        >
                          {j.status?.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}

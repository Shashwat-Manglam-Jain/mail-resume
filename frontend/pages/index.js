import { useState, useEffect, useCallback } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const PAGE_SIZE = 50;

const ROLE_LABELS = {
  ai_ml_engineer: "AI/ML Engineer",
  data_scientist: "Data Scientist",
  data_engineer: "Data Engineer",
  data_analyst_bi: "Data Analyst",
  business_analyst: "Business Analyst",
  software_engineer: "Software Engineer",
  full_stack_developer: "Full Stack",
  backend_engineer: "Backend",
  frontend_engineer: "Frontend",
  cloud_devops_engineer: "DevOps",
  cybersecurity_analyst: "Security",
  mobile_app_developer: "Mobile Dev",
  software_tester_qa: "QA",
  ui_ux_engineer: "UI/UX",
  product_designer: "Product Design",
  web_developer: "Web Dev",
  site_reliability_engineer: "SRE",
  network_engineer: "Networking",
  database_administrator: "DBA",
  blockchain_developer: "Blockchain",
  game_developer: "Game Dev",
};

function roleLabel(key) {
  return ROLE_LABELS[key] || (key ? key.replace(/_/g, " ") : "—");
}

function fmtDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "numeric", month: "short", year: "numeric",
  });
}

export default function Home() {
  const [tab, setTab] = useState("jobs");
  const [flash, setFlash] = useState(null);

  // ── Scraped Jobs ──────────────────────────────────────────
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [draftSearch, setDraftSearch] = useState("");
  const [search, setSearch] = useState("");
  const [srcFilter, setSrcFilter] = useState("");
  const [sources, setSources] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [applyingId, setApplyingId] = useState(null);

  // ── History ───────────────────────────────────────────────
  const [history, setHistory] = useState([]);
  const [histTotal, setHistTotal] = useState(0);
  const [histPage, setHistPage] = useState(0);
  const [loadingHist, setLoadingHist] = useState(false);

  function showFlash(msg, err = false) {
    setFlash({ msg, err });
    setTimeout(() => setFlash(null), 4000);
  }

  // Load source list once
  useEffect(() => {
    fetch(`${API}/scraped-jobs/sources`)
      .then(r => r.json())
      .then(setSources)
      .catch(() => {});
  }, []);

  const loadJobs = useCallback(() => {
    setLoadingJobs(true);
    const p = new URLSearchParams({
      limit: PAGE_SIZE,
      offset: page * PAGE_SIZE,
      include_sent: "false",
    });
    if (search) p.set("search", search);
    if (srcFilter) p.set("source", srcFilter);
    fetch(`${API}/scraped-jobs?${p}`)
      .then(r => r.json())
      .then(d => { setJobs(d.jobs || []); setTotal(d.total || 0); })
      .catch(() => showFlash("Failed to load jobs", true))
      .finally(() => setLoadingJobs(false));
  }, [page, search, srcFilter]);

  useEffect(() => { if (tab === "jobs") loadJobs(); }, [tab, loadJobs]);

  const loadHistory = useCallback(() => {
    setLoadingHist(true);
    const p = new URLSearchParams({ limit: PAGE_SIZE, offset: histPage * PAGE_SIZE });
    fetch(`${API}/sent-companies?${p}`)
      .then(r => r.json())
      .then(d => { setHistory(d.companies || []); setHistTotal(d.total || 0); })
      .catch(() => showFlash("Failed to load history", true))
      .finally(() => setLoadingHist(false));
  }, [histPage]);

  useEffect(() => { if (tab === "history") loadHistory(); }, [tab, loadHistory]);

  function handleSearch(e) {
    e.preventDefault();
    setPage(0);
    setSearch(draftSearch);
  }

  async function markApplied(job) {
    if (applyingId) return;
    setApplyingId(job.id);
    try {
      const r = await fetch(`${API}/jobs/${job.id}/mark-applied`, { method: "POST" });
      if (!r.ok) throw new Error((await r.json()).detail || "Error");
      showFlash(`Marked "${job.company_name}" as applied`);
      loadJobs();
    } catch (e) {
      showFlash(e.message, true);
    } finally {
      setApplyingId(null);
    }
  }

  async function clearHistory() {
    if (!confirm("Clear ALL application history?\nJobs will reappear in the list.")) return;
    try {
      const r = await fetch(`${API}/history`, { method: "DELETE" });
      if (!r.ok) throw new Error((await r.json()).detail || "Error");
      showFlash("History cleared");
      setHistPage(0);
      loadHistory();
      if (tab === "jobs") loadJobs();
    } catch (e) {
      showFlash(e.message, true);
    }
  }

  async function clearJobs() {
    if (!confirm("Delete ALL scraped job data?\nApplication history is preserved.")) return;
    try {
      const r = await fetch(`${API}/clear-monthly`, { method: "POST" });
      if (!r.ok) throw new Error((await r.json()).detail || "Error");
      showFlash("All job data cleared");
      setPage(0);
      loadJobs();
    } catch (e) {
      showFlash(e.message, true);
    }
  }

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const histPages  = Math.ceil(histTotal / PAGE_SIZE);

  return (
    <main>
      {/* Header */}
      <div className="app-header">
        <h1>Job Tracker</h1>
        <p>Foreign IT jobs · Scrape · Apply manually · Track history</p>
      </div>

      {/* Flash message */}
      {flash && (
        <div className={`status${flash.err ? " status-error" : ""}`}>
          {flash.msg}
          <button className="status-close" onClick={() => setFlash(null)}>×</button>
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab${tab === "jobs" ? " active" : ""}`}
          onClick={() => setTab("jobs")}
        >
          Scraped Jobs
          {total > 0 && <span className="tab-badge">{total}</span>}
        </button>
        <button
          className={`tab${tab === "history" ? " active" : ""}`}
          onClick={() => setTab("history")}
        >
          History
          {histTotal > 0 && <span className="tab-badge">{histTotal}</span>}
        </button>
      </div>

      {/* ═══════════ SCRAPED JOBS ═══════════ */}
      {tab === "jobs" && (
        <div className="card">
          <form className="filter-row" onSubmit={handleSearch}>
            <input
              className="filter-input"
              placeholder="Search company or title…"
              value={draftSearch}
              onChange={e => setDraftSearch(e.target.value)}
            />
            <select
              className="filter-select"
              value={srcFilter}
              onChange={e => { setSrcFilter(e.target.value); setPage(0); }}
            >
              <option value="">All Sources</option>
              {sources.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <button className="btn-primary btn-sm" type="submit">Search</button>
            <button
              className="btn-danger-outline btn-sm"
              type="button"
              onClick={clearJobs}
            >
              Clear Jobs
            </button>
          </form>

          {loadingJobs ? (
            <p className="state-msg">Loading…</p>
          ) : jobs.length === 0 ? (
            <p className="state-msg empty-state">
              No jobs found. Run the scraper to populate data.
            </p>
          ) : (
            <>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th style={{ width: 36 }}>#</th>
                      <th>Company</th>
                      <th>Title</th>
                      <th>Location</th>
                      <th>Role</th>
                      <th style={{ width: 90 }}></th>
                    </tr>
                  </thead>
                  <tbody>
                    {jobs.map((job, i) => (
                      <tr key={job.id}>
                        <td className="td-num">{page * PAGE_SIZE + i + 1}</td>
                        <td className="td-company">{job.company_name}</td>
                        <td>
                          {job.url
                            ? <a href={job.url} target="_blank" rel="noreferrer" className="job-link">{job.title}</a>
                            : job.title}
                        </td>
                        <td className="td-muted">{job.location || "Remote"}</td>
                        <td>
                          <span className="role-tag">{roleLabel(job.role_key)}</span>
                        </td>
                        <td>
                          <button
                            className="btn-apply"
                            disabled={applyingId === job.id}
                            onClick={() => {
                              if (job.url) window.open(job.url, "_blank");
                              markApplied(job);
                            }}
                          >
                            {applyingId === job.id ? "…" : "✓ Apply"}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="btn-secondary btn-sm"
                    disabled={page === 0}
                    onClick={() => setPage(p => p - 1)}
                  >← Prev</button>
                  <span className="page-info">
                    Page {page + 1} / {totalPages} &nbsp;·&nbsp; {total} jobs
                  </span>
                  <button
                    className="btn-secondary btn-sm"
                    disabled={page >= totalPages - 1}
                    onClick={() => setPage(p => p + 1)}
                  >Next →</button>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* ═══════════ HISTORY ═══════════ */}
      {tab === "history" && (
        <div className="card">
          <div className="history-hdr">
            <div>
              <h2>Application History</h2>
              <p className="subtitle">
                Applied companies are hidden from the jobs list automatically.
              </p>
            </div>
            <button className="btn-danger-outline btn-sm" onClick={clearHistory}>
              Clear All History
            </button>
          </div>

          {loadingHist ? (
            <p className="state-msg">Loading…</p>
          ) : history.length === 0 ? (
            <p className="state-msg empty-state">
              No applications recorded. Click "✓ Apply" on a job to track it here.
            </p>
          ) : (
            <>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th style={{ width: 36 }}>#</th>
                      <th>Company</th>
                      <th>Applied On</th>
                      <th>Via</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((h, i) => (
                      <tr key={h.id}>
                        <td className="td-num">{histPage * PAGE_SIZE + i + 1}</td>
                        <td className="td-company">{h.company_name}</td>
                        <td className="td-muted">{fmtDate(h.sent_at)}</td>
                        <td className="td-muted">{h.sent_via || "manual"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {histPages > 1 && (
                <div className="pagination">
                  <button
                    className="btn-secondary btn-sm"
                    disabled={histPage === 0}
                    onClick={() => setHistPage(p => p - 1)}
                  >← Prev</button>
                  <span className="page-info">
                    Page {histPage + 1} / {histPages} &nbsp;·&nbsp; {histTotal} entries
                  </span>
                  <button
                    className="btn-secondary btn-sm"
                    disabled={histPage >= histPages - 1}
                    onClick={() => setHistPage(p => p + 1)}
                  >Next →</button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </main>
  );
}

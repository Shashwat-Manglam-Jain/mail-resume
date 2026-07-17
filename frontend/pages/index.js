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

const EMPTY_FORM = {
  to_email: "",
  cc_emails: "",
  hr_name: "",
  company_name: "",
  role_key: "",
  message_type: "job_apply",
  custom_subject: "",
  custom_body: "",
};

export default function Home() {
  const [tab, setTab] = useState("queue");
  const [flash, setFlash] = useState(null);

  // ── Mail Queue ────────────────────────────────────────────
  const [profile, setProfile] = useState({});
  const [roles, setRoles] = useState([]);
  const [msgTypes, setMsgTypes] = useState([]);
  const [records, setRecords] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [roleSkills, setRoleSkills] = useState([]);
  const [msgPreview, setMsgPreview] = useState(null);
  const [queueLoading, setQueueLoading] = useState(false);
  const [sending, setSending] = useState({});
  const [editingId, setEditingId] = useState(null);
  const [validating, setValidating] = useState(false);
  const [validation, setValidation] = useState(null);
  const [editingCC, setEditingCC] = useState(null);
  const [ccDraft, setCcDraft] = useState("");
  const [showCC, setShowCC] = useState(false);

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

  // ── Mail Queue init ───────────────────────────────────────
  useEffect(() => {
    fetch(`${API}/profile`).then(r => r.ok ? r.json() : null).then(d => d && setProfile(d)).catch(() => {});
    fetch(`${API}/roles`).then(r => r.json()).then(data => {
      setRoles(data);
      if (data.length) setForm(f => ({ ...f, role_key: f.role_key || data[0].key }));
    }).catch(() => {});
    fetch(`${API}/message-templates`).then(r => r.ok ? r.json() : []).then(setMsgTypes).catch(() => {});
    fetchRecords();
  }, []);

  async function fetchRecords() {
    fetch(`${API}/records`).then(r => r.ok ? r.json() : []).then(setRecords).catch(() => {});
  }

  async function fetchSkills(roleKey) {
    if (!roleKey) { setRoleSkills([]); return; }
    fetch(`${API}/roles/${roleKey}/skills`).then(r => r.ok ? r.json() : []).then(setRoleSkills).catch(() => setRoleSkills([]));
  }

  async function fetchMsgPreview() {
    fetch(`${API}/message-preview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message_type: form.message_type, hr_name: form.hr_name, company_name: form.company_name, role_key: form.role_key, custom_subject: form.custom_subject, custom_body: form.custom_body }),
    }).then(r => r.ok ? r.json() : null).then(d => d && setMsgPreview(d)).catch(() => {});
  }

  async function validateEmail(email) {
    if (!email) return;
    setValidating(true); setValidation(null);
    try {
      const r = await fetch(`${API}/validate-email`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, skip_smtp: false }) });
      if (r.ok) setValidation(await r.json());
    } catch {} finally { setValidating(false); }
  }

  function updateForm(field, value) {
    setForm(f => ({ ...f, [field]: value }));
    if (field === "role_key") fetchSkills(value);
    if (field === "to_email") setValidation(null);
  }

  function cancelEdit() {
    setEditingId(null);
    setForm({ ...EMPTY_FORM, role_key: roles.length ? roles[0].key : "", message_type: "job_apply" });
    setMsgPreview(null); setRoleSkills([]); setValidation(null); setShowCC(false);
  }

  function startEdit(record) {
    setEditingId(record.id);
    setForm({ to_email: record.to_email, cc_emails: record.cc_emails || "", hr_name: record.hr_name, company_name: record.company_name, role_key: record.role_key, message_type: record.message_type, custom_subject: record.custom_subject || "", custom_body: record.custom_body || "" });
    fetchSkills(record.role_key);
    setMsgPreview(null); setValidation(null); setShowCC(!!(record.cc_emails));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function saveCC(recordId) {
    const r = await fetch(`${API}/records/${recordId}/cc`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ cc_emails: ccDraft }) });
    if (r.ok) { setEditingCC(null); setCcDraft(""); fetchRecords(); showFlash("CC updated."); }
  }

  async function submitForm(e) {
    e.preventDefault();
    if (!form.to_email) { showFlash("Please enter a recipient email.", true); return; }
    if (!form.role_key) { showFlash("Please select a target role.", true); return; }
    if (form.message_type === "custom" && (!form.custom_subject || !form.custom_body)) { showFlash("Custom message needs subject and body.", true); return; }
    setQueueLoading(true);
    try {
      const isEdit = editingId !== null;
      const r = await fetch(isEdit ? `${API}/records/${editingId}` : `${API}/records`, { method: isEdit ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      if (!r.ok) throw new Error(((await r.json().catch(() => ({}))).detail) || "Request failed.");
      setEditingId(null);
      showFlash(isEdit ? "Record updated." : "Added to queue.");
      setForm(f => ({ ...EMPTY_FORM, role_key: f.role_key, message_type: f.message_type }));
      setMsgPreview(null); setValidation(null); setShowCC(false);
      fetchRecords();
    } catch (err) { showFlash(err.message, true); }
    finally { setQueueLoading(false); }
  }

  async function sendOne(id) {
    if (sending[id]) return;
    setSending(s => ({ ...s, [id]: true }));
    try {
      const r = await fetch(`${API}/records/${id}/send`, { method: "POST" });
      const result = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(result.detail || "Send failed.");
      showFlash(result.failed > 0 ? `Failed: ${result.errors?.[0]?.error || "Unknown"}` : "Email sent!", result.failed > 0);
    } catch (err) { showFlash(err.message, true); }
    finally {
      setSending(s => ({ ...s, [id]: false }));
      fetchRecords(); // always sync — server may have deleted the record even on timeout
    }
  }

  async function sendAll() {
    if (!records.length) { showFlash("No records to send.", true); return; }
    setQueueLoading(true);
    try {
      const r = await fetch(`${API}/send-all`, { method: "POST" });
      const result = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(result.detail || "Send failed.");
      showFlash(`Done! Sent: ${result.sent}${result.failed > 0 ? `, Failed: ${result.failed}` : ""}`);
    } catch (err) { showFlash(err.message, true); }
    finally {
      setQueueLoading(false);
      fetchRecords(); // always sync — server may have sent and deleted records even on 502
    }
  }

  async function deleteRecord(id) {
    if (editingId === id) cancelEdit();
    await fetch(`${API}/records/${id}`, { method: "DELETE" });
    fetchRecords(); showFlash("Record removed.");
  }

  async function clearAllRecords() {
    if (!confirm("Clear all queued emails?")) return;
    cancelEdit();
    await fetch(`${API}/records`, { method: "DELETE" });
    fetchRecords(); showFlash("All records cleared.");
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
        <button className={`tab${tab === "queue" ? " active" : ""}`} onClick={() => setTab("queue")}>
          Mail Queue
          {records.length > 0 && <span className="tab-badge">{records.length}</span>}
        </button>
        <button className={`tab${tab === "jobs" ? " active" : ""}`} onClick={() => setTab("jobs")}>
          Scraped Jobs
          {total > 0 && <span className="tab-badge">{total}</span>}
        </button>
        <button className={`tab${tab === "history" ? " active" : ""}`} onClick={() => setTab("history")}>
          History
          {histTotal > 0 && <span className="tab-badge">{histTotal}</span>}
        </button>
      </div>

      {/* ═══════════ MAIL QUEUE ═══════════ */}
      {tab === "queue" && (
        <>
          {/* ── Compose form ── */}
          <div className={`card${editingId !== null ? " card-editing" : ""}`}>
            <div className="form-header">
              <div>
                <h2>{editingId !== null ? "Edit Record" : "Add Email Record"}</h2>
                <p className="subtitle">
                  {editingId !== null
                    ? "Update fields below and click Update Record."
                    : "Enter recipient email, pick a role & template, then add to queue and send."}
                </p>
              </div>
              {editingId !== null && (
                <button className="btn-secondary btn-sm" onClick={cancelEdit}>Cancel Edit</button>
              )}
            </div>

            {profile.name && (
              <div className="profile-banner">
                <strong>{profile.name}</strong>
                <span>{[profile.email, profile.phone].filter(Boolean).join(" | ")}</span>
              </div>
            )}

            <form onSubmit={submitForm}>
              <div className="form-grid">
                <label>
                  To Email *
                  <div className="input-with-btn">
                    <input type="email" value={form.to_email} onChange={e => updateForm("to_email", e.target.value)} placeholder="hr@company.com" required />
                    <button type="button" className="btn-validate" onClick={() => validateEmail(form.to_email)} disabled={!form.to_email || validating}>
                      {validating ? "..." : "Verify"}
                    </button>
                  </div>
                </label>

                {showCC || form.cc_emails ? (
                  <label>
                    CC (optional, comma-separated)
                    <div className="input-with-btn">
                      <input type="text" value={form.cc_emails} onChange={e => updateForm("cc_emails", e.target.value)} placeholder="cc1@company.com, cc2@company.com" />
                      <button type="button" className="btn-cc-remove" onClick={() => { updateForm("cc_emails", ""); setShowCC(false); }}>Remove</button>
                    </div>
                  </label>
                ) : (
                  <label>
                    <span>&nbsp;</span>
                    <button type="button" className="btn-add-cc" onClick={() => setShowCC(true)}>+ Add CC (optional)</button>
                  </label>
                )}

                <label>
                  HR / Contact Name
                  <input type="text" value={form.hr_name} onChange={e => updateForm("hr_name", e.target.value)} placeholder="Leave empty for Dear Sir/Madam" />
                </label>

                <label>
                  Company Name (optional)
                  <input type="text" value={form.company_name} onChange={e => updateForm("company_name", e.target.value)} placeholder="Optional — skipped if empty" />
                </label>

                <label>
                  Target Role *
                  <select value={form.role_key} onChange={e => updateForm("role_key", e.target.value)}>
                    <option value="">-- Select Role --</option>
                    {roles.map(r => <option key={r.key} value={r.key}>{r.title}</option>)}
                  </select>
                </label>

                <label>
                  Message Template
                  <select value={form.message_type} onChange={e => updateForm("message_type", e.target.value)}>
                    {msgTypes.map(mt => <option key={mt.key} value={mt.key}>{mt.label}</option>)}
                  </select>
                </label>
              </div>

              {validation && (
                <div className={`validation-panel ${validation.valid ? "validation-ok" : "validation-fail"}`}>
                  <div className="validation-header">
                    <strong>{validation.valid ? "✓ VALID" : "✗ INVALID"}: {validation.email}</strong>
                    <span className="validation-reason">{validation.reason}</span>
                  </div>
                  {validation.suggestion && (
                    <div className="validation-suggestion">
                      Did you mean <strong>{validation.suggestion}</strong>?
                      <button type="button" className="btn-use-suggestion" onClick={() => { updateForm("to_email", validation.suggestion); setValidation(null); }}>Use this</button>
                    </div>
                  )}
                  <div className="validation-checks">
                    {(validation.checks || []).map((c, i) => (
                      <span key={i} className={`check-badge ${c.ok ? "check-pass" : "check-fail"}`}>{c.ok ? "✓" : "✗"} {c.name}</span>
                    ))}
                  </div>
                </div>
              )}

              {form.message_type === "custom" && (
                <div className="custom-message-section">
                  <label>Subject * <input type="text" value={form.custom_subject} onChange={e => updateForm("custom_subject", e.target.value)} placeholder="Enter email subject" /></label>
                  <label>Body * <textarea value={form.custom_body} onChange={e => updateForm("custom_body", e.target.value)} placeholder="Write your email body here..." rows={8} /></label>
                </div>
              )}

              {roleSkills.length > 0 && (
                <div className="skills-panel">
                  <strong>Top Skills for This Role</strong>
                  <div className="skills-grid">
                    {roleSkills.map(cat => (
                      <div key={cat.category} className="skill-category">
                        <span className="cat-label">{cat.category}</span>
                        <div className="skill-chips">{cat.skills.map(s => <span key={s} className="chip">{s}</span>)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="actions">
                <button className={editingId !== null ? "btn-update" : "btn-primary"} type="submit" disabled={queueLoading}>
                  {editingId !== null ? "Update Record" : "Add to Queue"}
                </button>
                {editingId !== null && <button className="btn-secondary" type="button" onClick={cancelEdit}>Cancel</button>}
                <button className="btn-secondary" type="button" onClick={fetchMsgPreview} disabled={queueLoading}>Preview Message</button>
              </div>
            </form>

            {msgPreview && (
              <div className="preview-panel">
                <h3>Email Preview</h3>
                <div className="preview-subject"><strong>Subject:</strong> {msgPreview.subject}</div>
                <pre className="preview-body">{msgPreview.body}</pre>
                <button className="btn-secondary btn-sm" onClick={() => setMsgPreview(null)}>Close Preview</button>
              </div>
            )}
          </div>

          {/* ── Queue table ── */}
          <div className="card">
            <div className="queue-header">
              <div>
                <h2>Mail Queue</h2>
                <p className="subtitle">{records.length} record(s) waiting.</p>
              </div>
              <div className="actions">
                <button className="btn-send-all" onClick={sendAll} disabled={queueLoading || !records.length}>
                  Send All ({records.length})
                </button>
                {records.length > 0 && (
                  <button className="btn-secondary" onClick={clearAllRecords} disabled={queueLoading}>Clear All</button>
                )}
              </div>
            </div>

            {records.length > 0 ? (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>#</th><th>Email</th><th>CC</th><th>HR Name</th><th>Company</th><th>Role</th><th>Template</th><th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((r, i) => {
                      const roleName = roles.find(t => t.key === r.role_key)?.title || r.role_key;
                      const msgLabel = msgTypes.find(m => m.key === r.message_type)?.label || r.message_type;
                      const isSending = sending[r.id];
                      const isEditing = editingId === r.id;
                      const ccList = r.cc_emails ? r.cc_emails.split(",").map(e => e.trim()).filter(Boolean) : [];
                      const isEditingCC = editingCC === r.id;
                      return (
                        <tr key={r.id} className={isSending ? "row-sending" : isEditing ? "row-editing" : ""}>
                          <td className="cell-num">{i + 1}</td>
                          <td className="cell-email">{r.to_email}</td>
                          <td className="cell-cc">
                            {isEditingCC ? (
                              <div className="cc-edit-inline">
                                <input type="text" value={ccDraft} onChange={e => setCcDraft(e.target.value)}
                                  placeholder="cc1@co.com, cc2@co.com" className="cc-edit-input" autoFocus
                                  onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); saveCC(r.id); } }} />
                                <div className="cc-edit-btns">
                                  <button className="btn-send btn-xs" onClick={() => saveCC(r.id)}>Save</button>
                                  <button className="btn-delete btn-xs" onClick={() => setEditingCC(null)}>Cancel</button>
                                </div>
                              </div>
                            ) : (
                              <div className="cc-cell-clickable" onClick={() => { setEditingCC(r.id); setCcDraft(r.cc_emails || ""); }} title="Click to edit CC">
                                {ccList.length > 0
                                  ? <div className="cc-tags">{ccList.map((cc, j) => <span key={j} className="cc-tag">{cc}</span>)}</div>
                                  : <span className="cc-add-hint">+ Add CC</span>}
                              </div>
                            )}
                          </td>
                          <td>{r.hr_name || "Sir/Madam"}</td>
                          <td>{r.company_name || "—"}</td>
                          <td><span className="role-tag">{roleName}</span></td>
                          <td>{msgLabel}{r.custom_subject && <span className="custom-badge">custom</span>}</td>
                          <td className="cell-actions">
                            <button className="btn-send" onClick={() => sendOne(r.id)} disabled={isSending || queueLoading}>{isSending ? "Sending..." : "Send"}</button>
                            <button className="btn-edit" onClick={() => startEdit(r)} disabled={isSending || queueLoading}>{isEditing ? "Editing..." : "Edit"}</button>
                            <button className="btn-delete" onClick={() => deleteRecord(r.id)} disabled={isSending || queueLoading}>Delete</button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="empty-state">No records in queue. Add an email above and hit Send All.</p>
            )}
          </div>
        </>
      )}

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

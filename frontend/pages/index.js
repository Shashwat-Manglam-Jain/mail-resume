import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

  const [profile, setProfile] = useState({});
  const [roles, setRoles] = useState([]);
  const [msgTypes, setMsgTypes] = useState([]);
  const [records, setRecords] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [roleSkills, setRoleSkills] = useState([]);
  const [preview, setPreview] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState({});
  const [tab, setTab] = useState("queue");
  const [editingId, setEditingId] = useState(null);
  const [validating, setValidating] = useState(false);
  const [validation, setValidation] = useState(null);
  const [editingCC, setEditingCC] = useState(null);
  const [ccDraft, setCcDraft] = useState("");
  const [showCC, setShowCC] = useState(false);

  // Scraped Jobs tab state
  const [scrapedJobs, setScrapedJobs] = useState([]);
  const [scrapedTotal, setScrapedTotal] = useState(0);
  const [scrapedSources, setScrapedSources] = useState([]);
  const [sjFilter, setSjFilter] = useState({ source: "", has_email: "", search: "", role_key: "" });
  const [sjPage, setSjPage] = useState(0);
  const [sjLoading, setSjLoading] = useState(false);
  const [addEmailJobId, setAddEmailJobId] = useState(null);
  const [addEmailForm, setAddEmailForm] = useState({ email: "", name: "", title: "" });
  const [sentCompanies, setSentCompanies] = useState([]);
  const [sentTotal, setSentTotal] = useState(0);

  // Manual Apply tab state
  const [manualJobs, setManualJobs] = useState([]);
  const [manualTotal, setManualTotal] = useState(0);
  const [careerApps, setCareerApps] = useState([]);
  const [careerTotal, setCareerTotal] = useState(0);
  const [manualLoading, setManualLoading] = useState(false);

  useEffect(() => {
    fetchProfile();
    fetchRoles();
    fetchMsgTypes();
    fetchRecords();
  }, []);

  const totalCount = records.length;
  const isCustom = form.message_type === "custom";

  async function fetchProfile() {
    try {
      const res = await fetch(`${API}/profile`);
      if (res.ok) setProfile(await res.json());
    } catch {}
  }

  async function fetchRoles() {
    try {
      const res = await fetch(`${API}/roles`);
      const data = await res.json();
      setRoles(data);
      if (data.length) setForm(f => ({ ...f, role_key: f.role_key || data[0].key }));
    } catch {
      setStatus("Cannot load roles. Is the backend running?");
    }
  }

  async function fetchMsgTypes() {
    try {
      const res = await fetch(`${API}/message-templates`);
      if (res.ok) setMsgTypes(await res.json());
    } catch {}
  }

  async function fetchRecords() {
    try {
      const res = await fetch(`${API}/records`);
      if (res.ok) setRecords(await res.json());
    } catch {
      setStatus("Cannot load records. Is the backend running?");
    }
  }

  async function fetchSkills(roleKey) {
    if (!roleKey) { setRoleSkills([]); return; }
    try {
      const res = await fetch(`${API}/roles/${roleKey}/skills`);
      if (res.ok) setRoleSkills(await res.json());
    } catch { setRoleSkills([]); }
  }

  async function fetchPreview() {
    try {
      const res = await fetch(`${API}/message-preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message_type: form.message_type,
          hr_name: form.hr_name,
          company_name: form.company_name,
          role_key: form.role_key,
          custom_subject: form.custom_subject,
          custom_body: form.custom_body,
        }),
      });
      if (res.ok) setPreview(await res.json());
    } catch { setPreview(null); }
  }

  async function validateEmail(email) {
    if (!email) return;
    setValidating(true);
    setValidation(null);
    try {
      const res = await fetch(`${API}/validate-email`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, skip_smtp: false }),
      });
      if (res.ok) setValidation(await res.json());
    } catch {
      setValidation(null);
    } finally {
      setValidating(false);
    }
  }

  function updateForm(field, value) {
    setForm(f => ({ ...f, [field]: value }));
    if (field === "role_key") fetchSkills(value);
    if (field === "to_email") setValidation(null);
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(f => ({ ...EMPTY_FORM, role_key: roles.length ? roles[0].key : "", message_type: "job_apply" }));
    setPreview(null);
    setRoleSkills([]);
    setValidation(null);
    setShowCC(false);
  }

  function startEdit(record) {
    setEditingId(record.id);
    setForm({
      to_email: record.to_email,
      cc_emails: record.cc_emails || "",
      hr_name: record.hr_name,
      company_name: record.company_name,
      role_key: record.role_key,
      message_type: record.message_type,
      custom_subject: record.custom_subject || "",
      custom_body: record.custom_body || "",
    });
    fetchSkills(record.role_key);
    setPreview(null);
    setValidation(null);
    setShowCC(!!(record.cc_emails));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function startEditCC(record) {
    setEditingCC(record.id);
    setCcDraft(record.cc_emails || "");
  }

  async function saveCC(recordId) {
    try {
      const res = await fetch(`${API}/records/${recordId}/cc`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cc_emails: ccDraft }),
      });
      if (res.ok) {
        setEditingCC(null);
        setCcDraft("");
        await fetchRecords();
        setStatus("CC updated.");
      }
    } catch (err) {
      setStatus(`Failed to update CC: ${err.message}`);
    }
  }

  async function submitForm(e) {
    e.preventDefault();
    if (!form.to_email) { setStatus("Please enter a recipient email."); return; }
    if (!form.role_key) { setStatus("Please select a target role."); return; }
    if (isCustom && (!form.custom_subject || !form.custom_body)) {
      setStatus("Custom message requires both subject and body."); return;
    }

    setLoading(true);
    const isEditing = editingId !== null;
    setStatus(isEditing ? "Updating..." : "Adding...");

    try {
      const url = isEditing ? `${API}/records/${editingId}` : `${API}/records`;
      const method = isEditing ? "PUT" : "POST";
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        let detail = "Request failed.";
        try { detail = (await res.json()).detail || detail; } catch {}
        throw new Error(detail);
      }
      setEditingId(null);
      setStatus(isEditing ? "Record updated." : "Record added to queue.");
      setForm(f => ({ ...EMPTY_FORM, role_key: f.role_key, message_type: f.message_type }));
      setPreview(null);
      setValidation(null);
      setShowCC(false);
      await fetchRecords();
    } catch (err) {
      setStatus(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function sendOne(id) {
    if (sending[id]) return;
    setSending(s => ({ ...s, [id]: true }));
    setStatus("Sending...");
    try {
      const res = await fetch(`${API}/records/${id}/send`, { method: "POST" });
      let result;
      try { result = await res.json(); } catch { throw new Error("Invalid response."); }
      if (!res.ok) throw new Error(result.detail || `Send failed (HTTP ${res.status}).`);
      if (result.failed > 0) {
        setStatus(`Failed: ${result.errors?.[0]?.error || "Unknown error"}`);
      } else {
        setStatus("Email sent and record removed.");
      }
      await fetchRecords();
    } catch (err) {
      setStatus(`Send error: ${err.message}`);
    } finally {
      setSending(s => ({ ...s, [id]: false }));
    }
  }

  async function sendAll() {
    if (!totalCount) { setStatus("No records to send."); return; }
    setLoading(true);
    setStatus("Sending all emails...");
    try {
      const res = await fetch(`${API}/send-all`, { method: "POST" });
      let result;
      try { result = await res.json(); } catch { throw new Error("Invalid response."); }
      if (!res.ok) throw new Error(result.detail || "Send failed.");
      let msg = `Done! Sent: ${result.sent}`;
      if (result.failed > 0) msg += `, Failed: ${result.failed}`;
      setStatus(msg);
      await fetchRecords();
    } catch (err) {
      setStatus(`Send error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function deleteRecord(id) {
    if (editingId === id) cancelEdit();
    try {
      await fetch(`${API}/records/${id}`, { method: "DELETE" });
      await fetchRecords();
      setStatus("Record removed.");
    } catch (err) { setStatus(err.message); }
  }

  async function clearAll() {
    cancelEdit();
    try {
      await fetch(`${API}/records`, { method: "DELETE" });
      await fetchRecords();
      setStatus("All records cleared.");
    } catch (err) { setStatus(err.message); }
  }

  /* ── Scraped Jobs Tab ──────────────────────────────────────────────── */
  async function fetchScrapedJobs(page = 0) {
    setSjLoading(true);
    try {
      const params = new URLSearchParams();
      if (sjFilter.source) params.set("source", sjFilter.source);
      if (sjFilter.has_email === "yes") params.set("has_email", "true");
      if (sjFilter.has_email === "no") params.set("has_email", "false");
      if (sjFilter.search) params.set("search", sjFilter.search);
      if (sjFilter.role_key) params.set("role_key", sjFilter.role_key);
      params.set("limit", "50");
      params.set("offset", String(page * 50));
      const res = await fetch(`${API}/scraped-jobs?${params}`);
      if (res.ok) {
        const data = await res.json();
        setScrapedJobs(data.jobs);
        setScrapedTotal(data.total);
      }
    } catch { setStatus("Cannot load scraped jobs."); }
    finally { setSjLoading(false); }
  }

  async function fetchScrapedSources() {
    try {
      const res = await fetch(`${API}/scraped-jobs/sources`);
      if (res.ok) setScrapedSources(await res.json());
    } catch {}
  }

  async function queueScrapedJob(jobId, contactEmail, companyName, roleKey) {
    try {
      const res = await fetch(`${API}/scraped-jobs/${jobId}/queue`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ contact_email: contactEmail, hr_name: "", role_key: roleKey || "", message_type: "job_apply" }),
      });
      if (res.ok) {
        setStatus(`Queued email to ${contactEmail} (${companyName})`);
        await fetchRecords();
      } else {
        const err = await res.json().catch(() => ({}));
        setStatus(err.detail || "Failed to queue.");
      }
    } catch (err) { setStatus(`Queue error: ${err.message}`); }
  }

  async function addContactToJob(jobId) {
    if (!addEmailForm.email) { setStatus("Enter an email address."); return; }
    try {
      const res = await fetch(`${API}/scraped-jobs/${jobId}/add-contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(addEmailForm),
      });
      if (res.ok) {
        setStatus("Contact added.");
        setAddEmailJobId(null);
        setAddEmailForm({ email: "", name: "", title: "" });
        fetchScrapedJobs(sjPage);
      } else {
        const err = await res.json().catch(() => ({}));
        setStatus(err.detail || "Failed to add contact.");
      }
    } catch (err) { setStatus(`Error: ${err.message}`); }
  }

  async function fetchSentCompanies() {
    try {
      const res = await fetch(`${API}/sent-companies?limit=500`);
      if (res.ok) {
        const data = await res.json();
        setSentCompanies(data.companies);
        setSentTotal(data.total);
      }
    } catch {}
  }

  async function clearMonthlyData() {
    if (!confirm("Clear all scraped jobs/companies data? Sent history will be preserved.")) return;
    try {
      const res = await fetch(`${API}/clear-monthly`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setStatus(data.detail);
        fetchScrapedJobs(0);
        setSjPage(0);
      }
    } catch (err) { setStatus(`Error: ${err.message}`); }
  }

  useEffect(() => {
    if (tab === "scraped") { fetchScrapedJobs(sjPage); fetchScrapedSources(); fetchSentCompanies(); }
    if (tab === "manual") { fetchManualJobs(); fetchCareerApps(); }
  }, [tab, sjPage]);

  async function fetchManualJobs() {
    setManualLoading(true);
    try {
      const res = await fetch(`${API}/manual-apply-jobs?limit=200`);
      if (res.ok) { const data = await res.json(); setManualJobs(data.jobs); setManualTotal(data.total); }
    } catch {} finally { setManualLoading(false); }
  }

  async function fetchCareerApps() {
    try {
      const res = await fetch(`${API}/career-applications?limit=200`);
      if (res.ok) { const data = await res.json(); setCareerApps(data.applications); setCareerTotal(data.total); }
    } catch {}
  }

  /* ── Resume Preview Tab ────────────────────────────────────────────── */
  const [previewRole, setPreviewRole] = useState("");
  const [cacheStatus, setCacheStatus] = useState(null);
  const [latexSource, setLatexSource] = useState("");
  const [compilingLatex, setCompilingLatex] = useState(false);
  const [latexPdfUrl, setLatexPdfUrl] = useState(null);
  const [latexError, setLatexError] = useState("");

  useEffect(() => {
    if (roles.length && !previewRole) setPreviewRole(roles[0].key);
  }, [roles]);

  useEffect(() => { fetchCacheStatus(); }, []);

  async function fetchCacheStatus() {
    try {
      const res = await fetch(`${API}/resumes/status`);
      if (res.ok) setCacheStatus(await res.json());
    } catch {}
  }

  async function regenerateResumes() {
    setLoading(true);
    setStatus("Regenerating all resume PDFs...");
    try {
      const res = await fetch(`${API}/resumes/generate`, { method: "POST" });
      const data = await res.json();
      setStatus(data.detail);
      fetchCacheStatus();
    } catch (err) { setStatus(err.message); }
    finally { setLoading(false); }
  }

  async function compileLatex() {
    if (!latexSource.trim()) {
      setStatus("Paste your LaTeX source first.");
      return;
    }
    setCompilingLatex(true);
    setLatexError("");
    setStatus("Compiling LaTeX... (first run may download compiler, please wait)");
    if (latexPdfUrl) { URL.revokeObjectURL(latexPdfUrl); setLatexPdfUrl(null); }

    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 120000);
      const res = await fetch(`${API}/resume/compile-latex`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ latex: latexSource, filename: "resume.pdf" }),
        signal: controller.signal,
      });
      clearTimeout(timer);

      if (!res.ok) {
        let detail = "Compilation failed.";
        try { detail = (await res.json()).detail || detail; } catch {}
        setLatexError(detail);
        throw new Error(detail);
      }

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setLatexPdfUrl(url);
      setStatus("LaTeX compiled successfully!");
    } catch (err) {
      setStatus(err.message);
    } finally {
      setCompilingLatex(false);
    }
  }

  function downloadLatexPdf() {
    if (!latexPdfUrl) return;
    const a = document.createElement("a");
    a.href = latexPdfUrl;
    a.download = "resume.pdf";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  const activeRole = roles.find(r => r.key === previewRole);

  /* ── Render ────────────────────────────────────────────────────────── */
  return (
    <main>

      <header className="app-header">
        <h1>Resume Mailer</h1>
        <p>Add HR emails, select a role & template, then send all with one click.</p>
      </header>

      {profile.name && (
        <div className="profile-banner">
          <strong>{profile.name}</strong>
          <span>{[profile.email, profile.phone].filter(Boolean).join(" | ")}</span>
          <span className="profile-hint">Edit .env to change your details</span>
        </div>
      )}

      {status && (
        <div className={`status ${status.startsWith("Send error") || status.startsWith("Failed") ? "status-error" : ""}`}>
          {status}
          <button className="status-close" onClick={() => setStatus("")}>x</button>
        </div>
      )}

      <nav className="tabs">
        <button className={tab === "queue" ? "tab active" : "tab"} onClick={() => setTab("queue")}>
          Mail Queue
          {totalCount > 0 && <span className="tab-badge">{totalCount}</span>}
        </button>
        <button className={tab === "scraped" ? "tab active" : "tab"} onClick={() => setTab("scraped")}>
          Scraped Jobs
          {scrapedTotal > 0 && <span className="tab-badge">{scrapedTotal}</span>}
        </button>
        <button className={tab === "manual" ? "tab active" : "tab"} onClick={() => setTab("manual")}>
          Manual Apply
          {manualTotal > 0 && <span className="tab-badge">{manualTotal}</span>}
        </button>
        <button className={tab === "resume" ? "tab active" : "tab"} onClick={() => setTab("resume")}>
          Resume Preview
        </button>
      </nav>

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* TAB: Mail Queue                                               */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {tab === "queue" && (
        <>
          <div className={`card ${editingId !== null ? "card-editing" : ""}`}>
            <div className="form-header">
              <div>
                <h2>{editingId !== null ? "Edit Record" : "Add Email Record"}</h2>
                <p className="subtitle">
                  {editingId !== null
                    ? "Update the fields below and click Update Record."
                    : "Fill in details, pick a role and template. Use 'Custom Message' to write your own subject & body."}
                </p>
              </div>
              {editingId !== null && (
                <button className="btn-secondary btn-sm" onClick={cancelEdit}>Cancel Edit</button>
              )}
            </div>

            <form onSubmit={submitForm}>
              <div className="form-grid">
                <label>
                  To Email *
                  <div className="input-with-btn">
                    <input type="email" value={form.to_email}
                      onChange={e => updateForm("to_email", e.target.value)}
                      placeholder="hr@company.com" required />
                    <button type="button" className="btn-validate"
                      onClick={() => validateEmail(form.to_email)}
                      disabled={!form.to_email || validating}>
                      {validating ? "..." : "Verify"}
                    </button>
                  </div>
                </label>

                {showCC || form.cc_emails ? (
                  <label>
                    CC (optional, comma-separated)
                    <div className="input-with-btn">
                      <input type="text" value={form.cc_emails}
                        onChange={e => updateForm("cc_emails", e.target.value)}
                        placeholder="cc1@company.com, cc2@company.com" />
                      <button type="button" className="btn-cc-remove"
                        onClick={() => { updateForm("cc_emails", ""); setShowCC(false); }}>
                        Remove
                      </button>
                    </div>
                  </label>
                ) : (
                  <label>
                    <span>&nbsp;</span>
                    <button type="button" className="btn-add-cc" onClick={() => setShowCC(true)}>
                      + Add CC (optional)
                    </button>
                  </label>
                )}

                <label>
                  HR / Contact Name
                  <input type="text" value={form.hr_name}
                    onChange={e => updateForm("hr_name", e.target.value)}
                    placeholder="Leave empty for Dear Sir/Madam" />
                </label>

                <label>
                  Company Name (optional)
                  <input type="text" value={form.company_name}
                    onChange={e => updateForm("company_name", e.target.value)}
                    placeholder="Optional — skipped if empty" />
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
                    <strong>{validation.valid ? "VALID" : "INVALID"}: {validation.email}</strong>
                    <span className="validation-reason">{validation.reason}</span>
                  </div>
                  {validation.suggestion && (
                    <div className="validation-suggestion">
                      Did you mean <strong>{validation.suggestion}</strong>?
                      <button
                        type="button"
                        className="btn-use-suggestion"
                        onClick={() => {
                          updateForm("to_email", validation.suggestion);
                          setValidation(null);
                        }}
                      >
                        Use this
                      </button>
                    </div>
                  )}
                  <div className="validation-checks">
                    {validation.checks.map((c, i) => (
                      <span key={i} className={`check-badge ${c.ok ? "check-pass" : "check-fail"}`}>
                        {c.ok ? "✓" : "✗"} {c.name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {isCustom && (
                <div className="custom-message-section">
                  <label>
                    Subject *
                    <input type="text" value={form.custom_subject}
                      onChange={e => updateForm("custom_subject", e.target.value)}
                      placeholder="Enter email subject" required={isCustom} />
                  </label>
                  <label>
                    Body *
                    <textarea value={form.custom_body}
                      onChange={e => updateForm("custom_body", e.target.value)}
                      placeholder="Write your email body here..." rows={8} required={isCustom} />
                  </label>
                </div>
              )}

              {!isCustom && (
                <details className="custom-override">
                  <summary>Override subject or body (optional)</summary>
                  <div className="custom-override-fields">
                    <label>
                      Custom Subject (leave empty to use template)
                      <input type="text" value={form.custom_subject}
                        onChange={e => updateForm("custom_subject", e.target.value)}
                        placeholder="Override the auto-generated subject" />
                    </label>
                    <label>
                      Custom Body (leave empty to use template)
                      <textarea value={form.custom_body}
                        onChange={e => updateForm("custom_body", e.target.value)}
                        placeholder="Override the auto-generated body" rows={6} />
                    </label>
                  </div>
                </details>
              )}

              {roleSkills.length > 0 && (
                <div className="skills-panel">
                  <strong>Top Skills for This Role</strong>
                  <div className="skills-grid">
                    {roleSkills.map(cat => (
                      <div key={cat.category} className="skill-category">
                        <span className="cat-label">{cat.category}</span>
                        <div className="skill-chips">
                          {cat.skills.map(s => <span key={s} className="chip">{s}</span>)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="actions">
                <button className={editingId !== null ? "btn-update" : "btn-primary"} type="submit" disabled={loading}>
                  {editingId !== null ? "Update Record" : "Add to Queue"}
                </button>
                {editingId !== null && (
                  <button className="btn-secondary" type="button" onClick={cancelEdit}>Cancel</button>
                )}
                <button className="btn-secondary" type="button" onClick={fetchPreview} disabled={loading}>
                  Preview Message
                </button>
              </div>
            </form>

            {preview && (
              <div className="preview-panel">
                <h3>Email Preview</h3>
                <div className="preview-subject"><strong>Subject:</strong> {preview.subject}</div>
                <pre className="preview-body">{preview.body}</pre>
                <button className="btn-secondary btn-sm" onClick={() => setPreview(null)}>Close Preview</button>
              </div>
            )}
          </div>

          {/* ── Mail Queue Table ─────────────────────────────────────── */}
          <div className="card">
            <div className="queue-header">
              <div>
                <h2>Mail Queue</h2>
                <p className="subtitle">
                  {totalCount} record(s) waiting. Click CC to edit. Emails are validated before sending.
                </p>
              </div>
              <div className="actions">
                <button className="btn-send-all" onClick={sendAll} disabled={loading || !totalCount}>
                  Send All ({totalCount})
                </button>
                {totalCount > 0 && (
                  <button className="btn-secondary" onClick={clearAll} disabled={loading}>Clear All</button>
                )}
              </div>
            </div>

            {totalCount > 0 ? (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Email</th>
                      <th>CC</th>
                      <th>HR Name</th>
                      <th>Company</th>
                      <th>Role</th>
                      <th>Message</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((r, i) => {
                      const roleName = roles.find(t => t.key === r.role_key)?.title || r.role_key;
                      const msgLabel = msgTypes.find(m => m.key === r.message_type)?.label || r.message_type;
                      const isSending = sending[r.id];
                      const isEditing = editingId === r.id;
                      const ccList = r.cc_emails ? r.cc_emails.split(",").map(e => e.trim()).filter(Boolean) : [];
                      const isEditingThisCC = editingCC === r.id;

                      return (
                        <tr key={r.id} className={isSending ? "row-sending" : isEditing ? "row-editing" : ""}>
                          <td className="cell-num">{i + 1}</td>
                          <td className="cell-email">{r.to_email}</td>
                          <td className="cell-cc">
                            {isEditingThisCC ? (
                              <div className="cc-edit-inline">
                                <input
                                  type="text"
                                  value={ccDraft}
                                  onChange={e => setCcDraft(e.target.value)}
                                  placeholder="cc1@co.com, cc2@co.com"
                                  className="cc-edit-input"
                                  onKeyDown={e => { if (e.key === "Enter") { e.preventDefault(); saveCC(r.id); } }}
                                  autoFocus
                                />
                                <div className="cc-edit-btns">
                                  <button className="btn-send btn-xs" onClick={() => saveCC(r.id)}>Save</button>
                                  <button className="btn-delete btn-xs" onClick={() => setEditingCC(null)}>Cancel</button>
                                </div>
                              </div>
                            ) : (
                              <div className="cc-cell-clickable" onClick={() => startEditCC(r)} title="Click to edit CC">
                                {ccList.length > 0 ? (
                                  <div className="cc-tags">
                                    {ccList.map((cc, j) => (
                                      <span key={j} className="cc-tag">{cc}</span>
                                    ))}
                                  </div>
                                ) : (
                                  <span className="cc-add-hint">+ Add CC</span>
                                )}
                              </div>
                            )}
                          </td>
                          <td>{r.hr_name || "Sir/Madam"}</td>
                          <td>{r.company_name || "—"}</td>
                          <td><span className="role-tag">{roleName}</span></td>
                          <td>
                            {msgLabel}
                            {r.custom_subject && <span className="custom-badge">custom</span>}
                          </td>
                          <td className="cell-actions">
                            <button className="btn-send" onClick={() => sendOne(r.id)} disabled={isSending || loading}>
                              {isSending ? "Sending..." : "Send"}
                            </button>
                            <button className="btn-edit" onClick={() => startEdit(r)} disabled={isSending || loading}>
                              {isEditing ? "Editing..." : "Edit"}
                            </button>
                            <button className="btn-delete" onClick={() => deleteRecord(r.id)} disabled={isSending || loading}>
                              Delete
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="empty-state">No records in queue. Add emails above and hit &quot;Send All&quot; to deliver.</p>
            )}
          </div>
        </>
      )}

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* TAB: Scraped Jobs                                              */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {tab === "scraped" && (
        <>
          <div className="card">
            <div className="queue-header">
              <div>
                <h2>Scraped Jobs</h2>
                <p className="subtitle">
                  Jobs scraped by auto-job-applier. {sentTotal > 0 && <strong>{sentTotal} companies contacted so far.</strong>}
                </p>
              </div>
              <div className="actions">
                <button className="btn-secondary btn-sm" onClick={clearMonthlyData}>
                  Clear Monthly Data
                </button>
              </div>
            </div>

            <div className="form-grid" style={{marginBottom: 12}}>
              <label>
                Source
                <select value={sjFilter.source} onChange={e => { setSjFilter(f => ({...f, source: e.target.value})); setSjPage(0); }}>
                  <option value="">All Sources</option>
                  {scrapedSources.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </label>
              <label>
                Email Status
                <select value={sjFilter.has_email} onChange={e => { setSjFilter(f => ({...f, has_email: e.target.value})); setSjPage(0); }}>
                  <option value="">All</option>
                  <option value="yes">Has Email</option>
                  <option value="no">No Email</option>
                </select>
              </label>
              <label>
                Search
                <input type="text" value={sjFilter.search} placeholder="Company or title..."
                  onChange={e => setSjFilter(f => ({...f, search: e.target.value}))} />
              </label>
              <label>
                <span>&nbsp;</span>
                <button className="btn-primary" onClick={() => { setSjPage(0); fetchScrapedJobs(0); }}>
                  {sjLoading ? "Loading..." : "Search"}
                </button>
              </label>
            </div>

            <p className="subtitle">{scrapedTotal} job(s) found</p>

            {scrapedJobs.length > 0 ? (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Company</th>
                      <th>Title</th>
                      <th>Source</th>
                      <th>Location</th>
                      <th>Contact</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scrapedJobs.map((job, i) => (
                      <tr key={job.id}>
                        <td className="cell-num">{sjPage * 50 + i + 1}</td>
                        <td>
                          <strong>{job.company_name}</strong>
                          {job.company_domain && <div style={{fontSize:"0.8em",color:"#888"}}>{job.company_domain}</div>}
                        </td>
                        <td>
                          {job.url ? <a href={job.url} target="_blank" rel="noopener noreferrer">{job.title}</a> : job.title}
                        </td>
                        <td><span className="role-tag">{job.source}</span></td>
                        <td>{job.location || "Remote"}</td>
                        <td className="cell-cc">
                          {job.contacts.length > 0 ? (
                            <div className="cc-tags">
                              {job.contacts.map((c, j) => (
                                <span key={j} className="cc-tag" title={`${c.name || ""} ${c.title || ""} (${Math.round((c.confidence||0)*100)}%)`}>
                                  {c.email}
                                </span>
                              ))}
                            </div>
                          ) : (
                            addEmailJobId === job.id ? (
                              <div className="cc-edit-inline">
                                <input type="email" placeholder="email@company.com" value={addEmailForm.email}
                                  onChange={e => setAddEmailForm(f => ({...f, email: e.target.value}))}
                                  className="cc-edit-input" autoFocus />
                                <input type="text" placeholder="Name (optional)" value={addEmailForm.name}
                                  onChange={e => setAddEmailForm(f => ({...f, name: e.target.value}))}
                                  className="cc-edit-input" />
                                <div className="cc-edit-btns">
                                  <button className="btn-send btn-xs" onClick={() => addContactToJob(job.id)}>Save</button>
                                  <button className="btn-delete btn-xs" onClick={() => { setAddEmailJobId(null); setAddEmailForm({email:"",name:"",title:""}); }}>Cancel</button>
                                </div>
                              </div>
                            ) : (
                              <span className="cc-add-hint" onClick={() => setAddEmailJobId(job.id)}>+ Add Email</span>
                            )
                          )}
                        </td>
                        <td className="cell-actions">
                          {job.contacts.length > 0 && (
                            <button className="btn-send btn-xs"
                              onClick={() => queueScrapedJob(job.id, job.contacts[0].email, job.company_name, job.role_key)}>
                              Queue
                            </button>
                          )}
                          {job.contacts.length === 0 && addEmailJobId !== job.id && (
                            <button className="btn-edit btn-xs" onClick={() => setAddEmailJobId(job.id)}>
                              Add Email
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="empty-state">{sjLoading ? "Loading..." : "No scraped jobs found. Run auto-job-applier first."}</p>
            )}

            {scrapedTotal > 50 && (
              <div className="actions" style={{justifyContent:"center", gap:8, marginTop:12}}>
                <button className="btn-secondary btn-sm" disabled={sjPage === 0} onClick={() => setSjPage(p => p - 1)}>
                  Previous
                </button>
                <span>Page {sjPage + 1} of {Math.ceil(scrapedTotal / 50)}</span>
                <button className="btn-secondary btn-sm" disabled={(sjPage + 1) * 50 >= scrapedTotal} onClick={() => setSjPage(p => p + 1)}>
                  Next
                </button>
              </div>
            )}
          </div>

          {sentCompanies.length > 0 && (
            <div className="card">
              <h2>Sent History ({sentTotal})</h2>
              <p className="subtitle">Companies you have already contacted. These are excluded from scraped jobs above.</p>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Company</th>
                      <th>Email Used</th>
                      <th>Sent At</th>
                      <th>Via</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sentCompanies.map((sc, i) => (
                      <tr key={sc.id}>
                        <td className="cell-num">{i + 1}</td>
                        <td><strong>{sc.company_name}</strong></td>
                        <td>{sc.email_used}</td>
                        <td>{sc.sent_at ? new Date(sc.sent_at).toLocaleDateString() : "—"}</td>
                        <td>{sc.sent_via || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* ══════════════════════════════════════════════════════════════ */}
      {/* TAB: Resume Preview                                           */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {/* TAB: Manual Apply                                            */}
      {/* ══════════════════════════════════════════════════════════════ */}
      {tab === "manual" && (
        <>
          <div className="card">
            <h2>Jobs Needing Manual Apply</h2>
            <p className="subtitle">
              These jobs failed auto-apply (CAPTCHA, incomplete form, etc). Click the URL to apply manually, then download a resume for that role.
            </p>
            {manualLoading ? <p>Loading...</p> : (
              manualJobs.length === 0 ? <p style={{color:"#888"}}>No jobs need manual apply right now.</p> : (
                <table className="records-table">
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th>Title</th>
                      <th>Location</th>
                      <th>Role</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {manualJobs.map(j => (
                      <tr key={j.id}>
                        <td>{j.company_name}</td>
                        <td>{j.title}</td>
                        <td>{j.location || "Remote"}</td>
                        <td><span className="chip">{(j.role_key || "").replace(/_/g, " ")}</span></td>
                        <td>
                          <div className="actions" style={{margin:0,gap:6}}>
                            {j.url && <a href={j.url} target="_blank" rel="noopener noreferrer" className="btn-primary btn-sm">Apply</a>}
                            {j.role_key && <button className="btn-secondary btn-sm" onClick={() => window.open(`${API}/resume/${j.role_key}/pdf`, "_blank")}>Resume</button>}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )
            )}
          </div>

          <div className="card">
            <h2>Career Auto-Apply History</h2>
            <p className="subtitle">Results from automated career page applications.</p>
            {careerApps.length === 0 ? <p style={{color:"#888"}}>No career applications yet.</p> : (
              <table className="records-table">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Title</th>
                    <th>ATS</th>
                    <th>Status</th>
                    <th>Fields</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {careerApps.map(a => (
                    <tr key={a.id}>
                      <td>{a.company_name}</td>
                      <td>
                        {a.job_url ? <a href={a.job_url} target="_blank" rel="noopener noreferrer">{a.job_title || "View"}</a> : a.job_title}
                      </td>
                      <td><span className="chip">{a.ats_type}</span></td>
                      <td>
                        <span className={
                          a.status === "applied" ? "status-sent" :
                          a.status === "submitted_unconfirmed" ? "status-sent" :
                          a.status === "captcha_blocked" ? "status-warning" :
                          "status-failed"
                        }>
                          {a.status}
                        </span>
                      </td>
                      <td>{a.fields_filled}</td>
                      <td>{a.applied_at ? new Date(a.applied_at).toLocaleDateString() : ""}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}

      {tab === "resume" && (
        <>
          {/* ── Download Pre-Generated Resume ────────────────────────── */}
          <div className="card">
            <h2>Download Resume</h2>
            <p className="subtitle">Download a pre-generated resume for any role.</p>

            <label>
              Role
              <select value={previewRole} onChange={e => setPreviewRole(e.target.value)}>
                {roles.map(r => <option key={r.key} value={r.key}>{r.title}</option>)}
              </select>
            </label>

            {activeRole && (
              <div className="template-detail">
                <strong>{activeRole.title}</strong>
                <p>{activeRole.summary}</p>
                <div className="skill-chips">
                  {activeRole.skills.map(s => <span key={s} className="chip">{s}</span>)}
                </div>
                {activeRole.focus?.length > 0 && (
                  <div className="focus-list">
                    <strong>Interview Focus Areas</strong>
                    <ul>{activeRole.focus.map(f => <li key={f}>{f}</li>)}</ul>
                  </div>
                )}
              </div>
            )}

            <div className="actions">
              <button className="btn-primary" onClick={() => window.open(`${API}/resume/${previewRole}/pdf`, "_blank")} disabled={!previewRole}>
                Download PDF
              </button>
              <button className="btn-secondary" onClick={() => window.open(`${API}/resume/${previewRole}/latex`, "_blank")} disabled={!previewRole}>
                Download LaTeX
              </button>
              <button className="btn-send-all" onClick={() => window.open(`${API}/resumes/download-all`, "_blank")}>
                Download All (ZIP)
              </button>
            </div>

            <div className="cache-panel">
              <div className="cache-info">
                <strong>Resume Cache</strong>
                {cacheStatus ? (
                  <span className={cacheStatus.ready ? "cache-ready" : "cache-stale"}>
                    {cacheStatus.cached}/{cacheStatus.total} PDFs cached
                    {cacheStatus.ready ? " (ready)" : " (incomplete)"}
                  </span>
                ) : <span>Checking...</span>}
              </div>
              <p className="cache-hint">Click Regenerate after updating your .env file.</p>
              <button className="btn-secondary" onClick={regenerateResumes} disabled={loading}>
                Regenerate All Resumes
              </button>
            </div>
          </div>

          {/* ── LaTeX Resume Builder ──────────────────────────────────── */}
          <div className="card">
            <h2>LaTeX Resume</h2>
            <p className="subtitle">
              Paste your LaTeX source below, compile to PDF, preview, and download.
            </p>

            <div className="actions" style={{marginTop: 0, marginBottom: 14}}>
              <button className="btn-secondary btn-sm" type="button"
                onClick={async () => {
                  if (!previewRole) return;
                  try {
                    const res = await fetch(`${API}/resume/${previewRole}/latex`);
                    if (res.ok) { setLatexSource(await res.text()); setStatus("Loaded LaTeX for " + previewRole); }
                  } catch {}
                }}
                disabled={!previewRole}>
                Load Template LaTeX ({previewRole || "select role above"})
              </button>
            </div>

            <label>
              LaTeX Source
              <textarea className="latex-editor" value={latexSource}
                onChange={e => setLatexSource(e.target.value)}
                placeholder={"\\documentclass{article}\n\\begin{document}\n  Your resume here...\n\\end{document}"}
                rows={18}
                spellCheck={false} />
            </label>

            {latexError && (
              <div className="latex-error">
                <strong>Compilation Error:</strong>
                <pre>{latexError}</pre>
              </div>
            )}

            <div className="actions">
              <button className="btn-primary" onClick={compileLatex}
                disabled={!latexSource.trim() || compilingLatex}>
                {compilingLatex ? "Compiling..." : "Compile PDF"}
              </button>
              {latexPdfUrl && (
                <button className="btn-send-all" onClick={downloadLatexPdf}>
                  Download PDF
                </button>
              )}
            </div>

            {latexPdfUrl && (
              <div className="latex-preview">
                <iframe src={latexPdfUrl} title="Resume Preview" />
              </div>
            )}
          </div>
        </>
      )}
    </main>
  );
}

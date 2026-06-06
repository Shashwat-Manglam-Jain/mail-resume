/**
 * index.js — Main page for the Email Resume Bulk Sender.
 *
 * Layout:
 *   1. Header — app name and description
 *   2. Profile banner — shows name/email/phone from .env
 *   3. Tabs:
 *      a. Mail Queue — add/edit records, table with per-row Send/Edit/Delete, Send All
 *      b. Resume Preview — role selector, skills, download PDF/LaTeX
 *
 * Workflow:
 *   - User adds records (email, HR name, company, role, message type)
 *   - No file upload — resume PDF is auto-generated per role
 *   - "Send" on a row → sends that one email, removes row on success
 *   - "Edit" on a row → loads record into form for updating
 *   - "Send All" → sends every row, removes all successful ones
 *   - Failed rows stay in the table for retry
 */

import { useEffect, useState } from "react";

/* ── API base URL (configurable via .env.local) ─────────────────────────── */
const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/* ── Default form state for adding a new record ─────────────────────────── */
const EMPTY_FORM = {
  to_email: "",
  hr_name: "",
  company_name: "",
  role_key: "",
  message_type: "job_apply",
};

export default function Home() {

  /* ── State ──────────────────────────────────────────────────────────────── */
  const [profile, setProfile] = useState({});       // user profile from .env
  const [roles, setRoles] = useState([]);            // available role templates
  const [msgTypes, setMsgTypes] = useState([]);       // message template options
  const [records, setRecords] = useState([]);         // queued mail records
  const [form, setForm] = useState(EMPTY_FORM);       // add/edit-record form
  const [roleSkills, setRoleSkills] = useState([]);    // skills for selected role
  const [preview, setPreview] = useState(null);        // message preview
  const [status, setStatus] = useState("");            // status/notification bar
  const [loading, setLoading] = useState(false);       // global loading flag
  const [sending, setSending] = useState({});          // per-row sending state
  const [tab, setTab] = useState("queue");             // active tab
  const [editingId, setEditingId] = useState(null);    // record id being edited (null = add mode)

  /* ── Load initial data on mount ─────────────────────────────────────────── */
  useEffect(() => {
    fetchProfile();
    fetchRoles();
    fetchMsgTypes();
    fetchRecords();
  }, []);

  /* ── Derived counts for the stats bar ───────────────────────────────────── */
  const totalCount = records.length;

  /* ── Data fetching functions ────────────────────────────────────────────── */

  /** Load user profile from backend (.env values). */
  async function fetchProfile() {
    try {
      const res = await fetch(`${API}/profile`);
      if (res.ok) setProfile(await res.json());
    } catch { /* profile display is optional */ }
  }

  /** Load all available role templates. */
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

  /** Load available message template types. */
  async function fetchMsgTypes() {
    try {
      const res = await fetch(`${API}/message-templates`);
      if (res.ok) setMsgTypes(await res.json());
    } catch { /* fallback to empty */ }
  }

  /** Load all queued records from the database. */
  async function fetchRecords() {
    try {
      const res = await fetch(`${API}/records`);
      if (res.ok) setRecords(await res.json());
    } catch {
      setStatus("Cannot load records. Is the backend running?");
    }
  }

  /** Load categorized skills for a selected role. */
  async function fetchSkills(roleKey) {
    if (!roleKey) { setRoleSkills([]); return; }
    try {
      const res = await fetch(`${API}/roles/${roleKey}/skills`);
      if (res.ok) setRoleSkills(await res.json());
    } catch { setRoleSkills([]); }
  }

  /** Preview the composed email message. */
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
        }),
      });
      if (res.ok) setPreview(await res.json());
    } catch { setPreview(null); }
  }

  /* ── Form handlers ──────────────────────────────────────────────────────── */

  /** Update form field and load skills when role changes. */
  function updateForm(field, value) {
    setForm(f => ({ ...f, [field]: value }));
    if (field === "role_key") fetchSkills(value);
  }

  /** Reset form to add mode. */
  function cancelEdit() {
    setEditingId(null);
    setForm(f => ({ ...EMPTY_FORM, role_key: roles.length ? roles[0].key : "", message_type: "job_apply" }));
    setPreview(null);
    setRoleSkills([]);
  }

  /** Load a record's data into the form for editing. */
  function startEdit(record) {
    setEditingId(record.id);
    setForm({
      to_email: record.to_email,
      hr_name: record.hr_name,
      company_name: record.company_name,
      role_key: record.role_key,
      message_type: record.message_type,
    });
    fetchSkills(record.role_key);
    setPreview(null);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  /** Add a new record or update an existing one. */
  async function submitForm(e) {
    e.preventDefault();

    if (!form.to_email) {
      setStatus("Please enter a recipient email address.");
      return;
    }
    if (!form.role_key) {
      setStatus("Please select a target role.");
      return;
    }

    setLoading(true);
    const isEditing = editingId !== null;
    setStatus(isEditing ? "Updating record..." : "Adding record...");

    try {
      const url = isEditing ? `${API}/records/${editingId}` : `${API}/records`;
      const method = isEditing ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          to_email: form.to_email,
          hr_name: form.hr_name,
          company_name: form.company_name,
          role_key: form.role_key,
          message_type: form.message_type,
        }),
      });

      if (!res.ok) {
        let detail = "Request failed.";
        try { detail = (await res.json()).detail || detail; } catch {}
        throw new Error(detail);
      }

      if (isEditing) {
        setEditingId(null);
        setStatus("Record updated.");
      } else {
        setStatus("Record added to queue.");
      }

      setForm(f => ({ ...EMPTY_FORM, role_key: f.role_key, message_type: f.message_type }));
      setPreview(null);
      await fetchRecords();
    } catch (err) {
      setStatus(err.message);
    } finally {
      setLoading(false);
    }
  }

  /* ── Send handlers ──────────────────────────────────────────────────────── */

  /**
   * Send a single record's email.
   * On success: row is removed from the table.
   * On failure: row stays, error message is shown.
   */
  async function sendOne(id) {
    if (sending[id]) return;
    setSending(s => ({ ...s, [id]: true }));
    setStatus("Sending...");
    try {
      const res = await fetch(`${API}/records/${id}/send`, { method: "POST" });

      let result;
      try {
        result = await res.json();
      } catch {
        throw new Error("Invalid response from server.");
      }

      if (!res.ok) {
        throw new Error(result.detail || `Send failed (HTTP ${res.status}).`);
      }

      if (result.failed > 0) {
        const errMsg = result.errors && result.errors[0] && result.errors[0].error
          ? result.errors[0].error
          : "Unknown error";
        setStatus(`Failed: ${errMsg}`);
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

  /**
   * Send ALL queued records.
   * Successful records are auto-deleted. Failed ones stay for retry.
   */
  async function sendAll() {
    if (!totalCount) { setStatus("No records to send."); return; }
    setLoading(true);
    setStatus("Sending all emails...");
    try {
      const res = await fetch(`${API}/send-all`, { method: "POST" });

      let result;
      try {
        result = await res.json();
      } catch {
        throw new Error("Invalid response from server.");
      }

      if (!res.ok) {
        throw new Error(result.detail || "Send failed.");
      }

      let msg = `Done! Sent: ${result.sent}`;
      if (result.failed > 0) msg += `, Failed: ${result.failed} (check table)`;
      setStatus(msg);
      await fetchRecords();
    } catch (err) {
      setStatus(`Send error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  /** Delete a single record without sending. */
  async function deleteRecord(id) {
    if (editingId === id) cancelEdit();
    try {
      await fetch(`${API}/records/${id}`, { method: "DELETE" });
      await fetchRecords();
      setStatus("Record removed.");
    } catch (err) {
      setStatus(err.message);
    }
  }

  /** Clear all records from the queue. */
  async function clearAll() {
    cancelEdit();
    try {
      await fetch(`${API}/records`, { method: "DELETE" });
      await fetchRecords();
      setStatus("All records cleared.");
    } catch (err) {
      setStatus(err.message);
    }
  }

  /* ── Resume download (Preview tab) ──────────────────────────────────────── */

  /** Download the auto-generated PDF resume for a role. */
  function downloadPDF(roleKey) {
    window.open(`${API}/resume/${roleKey}/pdf`, "_blank");
  }

  /** Download the auto-generated LaTeX resume for a role. */
  function downloadLatex(roleKey) {
    window.open(`${API}/resume/${roleKey}/latex`, "_blank");
  }

  /* ── Resume cache status and regeneration ────────────────────────────────── */
  const [cacheStatus, setCacheStatus] = useState(null);

  async function fetchCacheStatus() {
    try {
      const res = await fetch(`${API}/resumes/status`);
      if (res.ok) setCacheStatus(await res.json());
    } catch { /* optional */ }
  }

  useEffect(() => { fetchCacheStatus(); }, []);

  /** Regenerate all resume PDFs (after .env profile update). */
  async function regenerateResumes() {
    setLoading(true);
    setStatus("Regenerating all resume PDFs...");
    try {
      const res = await fetch(`${API}/resumes/generate`, { method: "POST" });
      const data = await res.json();
      setStatus(data.detail);
      fetchCacheStatus();
    } catch (err) {
      setStatus(err.message);
    } finally {
      setLoading(false);
    }
  }

  /* ── Active template for preview tab ────────────────────────────────────── */
  const [previewRole, setPreviewRole] = useState("");
  useEffect(() => {
    if (roles.length && !previewRole) setPreviewRole(roles[0].key);
  }, [roles]);
  const activeRole = roles.find(r => r.key === previewRole);

  /* ── Render ─────────────────────────────────────────────────────────────── */
  return (
    <main>

      {/* ── App header ─────────────────────────────────────────────── */}
      <header className="app-header">
        <h1>Resume Mailer</h1>
        <p>Add HR emails to the table, select a role and message type, then send all with one click.</p>
      </header>

      {/* ── Profile banner — shows who is sending ──────────────────── */}
      {profile.name && (
        <div className="profile-banner">
          <strong>{profile.name}</strong>
          <span>{[profile.email, profile.phone].filter(Boolean).join(" | ")}</span>
          <span className="profile-hint">Edit .env to change your details</span>
        </div>
      )}

      {/* ── Status notification bar ────────────────────────────────── */}
      {status && (
        <div className={`status ${status.startsWith("Send error") || status.startsWith("Failed") ? "status-error" : ""}`}>
          {status}
          <button className="status-close" onClick={() => setStatus("")}>x</button>
        </div>
      )}

      {/* ── Tab navigation ─────────────────────────────────────────── */}
      <nav className="tabs">
        <button
          className={tab === "queue" ? "tab active" : "tab"}
          onClick={() => setTab("queue")}
        >
          Mail Queue
          {totalCount > 0 && <span className="tab-badge">{totalCount}</span>}
        </button>
        <button
          className={tab === "resume" ? "tab active" : "tab"}
          onClick={() => setTab("resume")}
        >
          Resume Preview
        </button>
      </nav>

      {/* ================================================================ */}
      {/* TAB: Mail Queue                                                  */}
      {/* ================================================================ */}
      {tab === "queue" && (
        <>
          {/* ── Add / Edit Record Form ─────────────────────────────── */}
          <div className={`card ${editingId !== null ? "card-editing" : ""}`}>
            <div className="form-header">
              <div>
                <h2>{editingId !== null ? "Edit Record" : "Add Email Record"}</h2>
                <p className="subtitle">
                  {editingId !== null
                    ? "Update the fields below and click Update Record."
                    : "Fill in HR details, pick a role and message template. Resume PDF is auto-generated."}
                </p>
              </div>
              {editingId !== null && (
                <button className="btn-secondary btn-sm" onClick={cancelEdit}>
                  Cancel Edit
                </button>
              )}
            </div>

            <form onSubmit={submitForm}>
              <div className="form-grid">

                {/* Recipient email — required */}
                <label>
                  Recipient Email *
                  <input
                    type="email"
                    value={form.to_email}
                    onChange={e => updateForm("to_email", e.target.value)}
                    placeholder="hr@company.com"
                    required
                  />
                </label>

                {/* HR name — leave empty for "Dear Sir/Madam" */}
                <label>
                  HR / Contact Name
                  <input
                    type="text"
                    value={form.hr_name}
                    onChange={e => updateForm("hr_name", e.target.value)}
                    placeholder="Leave empty for Dear Sir/Madam"
                  />
                </label>

                {/* Company name — optional, omitted from email if empty */}
                <label>
                  Company Name (optional)
                  <input
                    type="text"
                    value={form.company_name}
                    onChange={e => updateForm("company_name", e.target.value)}
                    placeholder="Optional — skipped if empty"
                  />
                </label>

                {/* Role dropdown — determines which resume to generate */}
                <label>
                  Target Role *
                  <select
                    value={form.role_key}
                    onChange={e => updateForm("role_key", e.target.value)}
                  >
                    <option value="">-- Select Role --</option>
                    {roles.map(r => (
                      <option key={r.key} value={r.key}>{r.title}</option>
                    ))}
                  </select>
                </label>

                {/* Message template dropdown */}
                <label>
                  Message Template
                  <select
                    value={form.message_type}
                    onChange={e => updateForm("message_type", e.target.value)}
                  >
                    {msgTypes.map(mt => (
                      <option key={mt.key} value={mt.key}>{mt.label}</option>
                    ))}
                  </select>
                </label>
              </div>

              {/* ── Skills panel — shows top skills for selected role ── */}
              {roleSkills.length > 0 && (
                <div className="skills-panel">
                  <strong>Top Skills for This Role</strong>
                  <div className="skills-grid">
                    {roleSkills.map(cat => (
                      <div key={cat.category} className="skill-category">
                        <span className="cat-label">{cat.category}</span>
                        <div className="skill-chips">
                          {cat.skills.map(s => (
                            <span key={s} className="chip">{s}</span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── Action buttons ────────────────────────────────────── */}
              <div className="actions">
                <button className={editingId !== null ? "btn-update" : "btn-primary"} type="submit" disabled={loading}>
                  {editingId !== null ? "Update Record" : "Add to Queue"}
                </button>
                {editingId !== null && (
                  <button className="btn-secondary" type="button" onClick={cancelEdit}>
                    Cancel
                  </button>
                )}
                <button
                  className="btn-secondary"
                  type="button"
                  onClick={fetchPreview}
                  disabled={loading}
                >
                  Preview Message
                </button>
              </div>
            </form>

            {/* ── Message preview panel ───────────────────────────────── */}
            {preview && (
              <div className="preview-panel">
                <h3>Email Preview</h3>
                <div className="preview-subject">
                  <strong>Subject:</strong> {preview.subject}
                </div>
                <pre className="preview-body">{preview.body}</pre>
                <button
                  className="btn-secondary btn-sm"
                  onClick={() => setPreview(null)}
                >
                  Close Preview
                </button>
              </div>
            )}
          </div>

          {/* ── Mail Queue Table ────────────────────────────────────── */}
          <div className="card">
            <div className="queue-header">
              <div>
                <h2>Mail Queue</h2>
                <p className="subtitle">
                  {totalCount} record(s) waiting.
                  Sent records are auto-removed from this table.
                </p>
              </div>
              <div className="actions">
                <button
                  className="btn-send-all"
                  onClick={sendAll}
                  disabled={loading || !totalCount}
                >
                  Send All ({totalCount})
                </button>
                {totalCount > 0 && (
                  <button
                    className="btn-secondary"
                    onClick={clearAll}
                    disabled={loading}
                  >
                    Clear All
                  </button>
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
                      <th>HR Name</th>
                      <th>Company</th>
                      <th>Role</th>
                      <th>Message</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((r, i) => {
                      const roleName = roles.find(
                        t => t.key === r.role_key
                      )?.title || r.role_key;
                      const msgLabel = msgTypes.find(
                        m => m.key === r.message_type
                      )?.label || r.message_type;
                      const isSending = sending[r.id];
                      const isEditing = editingId === r.id;

                      return (
                        <tr key={r.id} className={isSending ? "row-sending" : isEditing ? "row-editing" : ""}>
                          <td className="cell-num">{i + 1}</td>
                          <td className="cell-email">{r.to_email}</td>
                          <td>{r.hr_name || "Sir/Madam"}</td>
                          <td>{r.company_name || "—"}</td>
                          <td><span className="role-tag">{roleName}</span></td>
                          <td>{msgLabel}</td>
                          <td className="cell-actions">
                            <button
                              className="btn-send"
                              onClick={() => sendOne(r.id)}
                              disabled={isSending || loading}
                            >
                              {isSending ? "Sending..." : "Send"}
                            </button>
                            <button
                              className="btn-edit"
                              onClick={() => startEdit(r)}
                              disabled={isSending || loading}
                            >
                              {isEditing ? "Editing..." : "Edit"}
                            </button>
                            <button
                              className="btn-delete"
                              onClick={() => deleteRecord(r.id)}
                              disabled={isSending || loading}
                            >
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
              <p className="empty-state">
                No records in queue. Add emails above and hit
                &quot;Send All&quot; to deliver.
              </p>
            )}
          </div>
        </>
      )}

      {/* ================================================================ */}
      {/* TAB: Resume Preview                                              */}
      {/* ================================================================ */}
      {tab === "resume" && (
        <div className="card">
          <h2>Resume Preview & Download</h2>
          <p className="subtitle">
            Select a role to see its skills and focus areas.
            Download the auto-generated PDF or LaTeX resume.
            Your details from .env are used automatically.
          </p>

          {/* ── Role selector ─────────────────────────────────────────── */}
          <label>
            Role
            <select
              value={previewRole}
              onChange={e => setPreviewRole(e.target.value)}
            >
              {roles.map(r => (
                <option key={r.key} value={r.key}>{r.title}</option>
              ))}
            </select>
          </label>

          {/* ── Role detail card ──────────────────────────────────────── */}
          {activeRole && (
            <div className="template-detail">
              <strong>{activeRole.title}</strong>
              <p>{activeRole.summary}</p>

              {/* Skills */}
              <div className="skill-chips">
                {activeRole.skills.map(s => (
                  <span key={s} className="chip">{s}</span>
                ))}
              </div>

              {/* Focus areas */}
              {activeRole.focus?.length > 0 && (
                <div className="focus-list">
                  <strong>Interview Focus Areas</strong>
                  <ul>
                    {activeRole.focus.map(f => <li key={f}>{f}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* ── Download buttons ──────────────────────────────────────── */}
          <div className="actions">
            <button
              className="btn-primary"
              onClick={() => downloadPDF(previewRole)}
              disabled={!previewRole}
            >
              Download PDF Resume
            </button>
            <button
              className="btn-secondary"
              onClick={() => downloadLatex(previewRole)}
              disabled={!previewRole}
            >
              Download LaTeX
            </button>
          </div>

          {/* ── Resume cache status + regenerate ──────────────────────── */}
          <div className="cache-panel">
            <div className="cache-info">
              <strong>Resume Cache</strong>
              {cacheStatus ? (
                <span className={cacheStatus.ready ? "cache-ready" : "cache-stale"}>
                  {cacheStatus.cached}/{cacheStatus.total} PDFs cached
                  {cacheStatus.ready ? " (ready)" : " (incomplete)"}
                </span>
              ) : (
                <span>Checking...</span>
              )}
            </div>
            <p className="cache-hint">
              Resumes are pre-generated on server startup using your .env details.
              Click Regenerate after updating your .env file.
            </p>
            <button
              className="btn-secondary"
              onClick={regenerateResumes}
              disabled={loading}
            >
              Regenerate All Resumes
            </button>
          </div>
        </div>
      )}
    </main>
  );
}

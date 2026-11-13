import { useState, useEffect, useRef } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const EMPTY_FORM = {
  to_email: "",
  cc_emails: "",
  hr_name: "",
  company_name: "",
  role_key: "",
  role_title: "",
  experience_years: 4,
  custom_subject: "",
  custom_body: "",
};

export default function Home() {
  const [tab, setTab] = useState("queue");
  const [flash, setFlash] = useState(null);

  const [profile, setProfile] = useState({});
  const [roles, setRoles] = useState([]);
  const [allRoles, setAllRoles] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [roleSkills, setRoleSkills] = useState([]);
  const [validating, setValidating] = useState(false);
  const [validation, setValidation] = useState(null);
  const [showCC, setShowCC] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);

  const [selectedRole, setSelectedRole] = useState(null);
  const [roleDetail, setRoleDetail] = useState(null);
  const [savingRole, setSavingRole] = useState(false);
  const [showProfileEditor, setShowProfileEditor] = useState(false);
  const [profileForm, setProfileForm] = useState({});
  const [newRoleForm, setNewRoleForm] = useState({ key: "", title: "" });
  const [showNewRole, setShowNewRole] = useState(false);
  const [builderExpYears, setBuilderExpYears] = useState(4);
  const [directSending, setDirectSending] = useState(false);
  const [uploadedResume, setUploadedResume] = useState(null);
  const autoLoadRef = useRef(null);

  const hasDbRoles = roles.length > 0;

  function showFlash(msg, err = false) {
    setFlash({ msg, err });
    setTimeout(() => setFlash(null), 4000);
  }

  useEffect(() => {
    fetch(`${API}/profile`).then(r => r.ok ? r.json() : null).then(d => d && setProfile(d)).catch(() => {});
    fetch(`${API}/roles`).then(r => r.ok ? r.json() : []).then(data => {
      const list = Array.isArray(data) ? data : [];
      setRoles(list);
      const defaultRole = list.find(r => r.key === "python_developer") || list[0];
      if (defaultRole) {
        setForm(f => ({ ...f, role_key: f.role_key || defaultRole.key, role_title: f.role_title || defaultRole.title }));
        autoLoadTemplate(defaultRole.key);
      }
    }).catch(() => {});
    fetch(`${API}/roles?all=true`).then(r => r.ok ? r.json() : []).then(data => {
      setAllRoles(Array.isArray(data) ? data : []);
    }).catch(() => {});
  }, []);

  async function fetchSkills(roleKey) {
    if (!roleKey) { setRoleSkills([]); return; }
    fetch(`${API}/roles/${roleKey}/skills`).then(r => r.ok ? r.json() : []).then(data => {
      setRoleSkills(Array.isArray(data) ? data : []);
    }).catch(() => setRoleSkills([]));
  }

  function autoLoadTemplate(roleKey) {
    if (!roleKey) return;
    if (autoLoadRef.current) clearTimeout(autoLoadRef.current);
    autoLoadRef.current = setTimeout(async () => {
      setLoadingPreview(true);
      try {
        const r = await fetch(`${API}/message-preview`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            role_key: roleKey,
            role_title: form.role_title,
            hr_name: form.hr_name,
            company_name: form.company_name,
            experience_years: form.experience_years || 4,
          }),
        });
        if (r.ok) {
          const data = await r.json();
          setForm(f => ({ ...f, custom_subject: data.subject, custom_body: data.body }));
        }
      } catch {}
      finally { setLoadingPreview(false); }
    }, 300);
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
    if (field === "role_key") {
      fetchSkills(value);
      const role = roles.find(r => r.key === value);
      if (role) setForm(f => ({ ...f, [field]: value, role_title: role.title }));
      autoLoadTemplate(value);
    }
    if (field === "to_email") setValidation(null);
  }

  async function sendDirect(e) {
    e.preventDefault();
    if (!form.to_email) { showFlash("Please enter a recipient email.", true); return; }
    if (!form.role_key && !form.role_title) { showFlash("Please select a role.", true); return; }
    if (!form.custom_subject || !form.custom_body) { showFlash("Please wait for the template to load.", true); return; }
    setDirectSending(true);
    try {
      const fd = new FormData();
      fd.append("to_email", form.to_email);
      fd.append("cc_emails", form.cc_emails || "");
      fd.append("hr_name", form.hr_name || "");
      fd.append("company_name", form.company_name || "");
      fd.append("role_key", form.role_key || form.role_title.toLowerCase().replace(/\s+/g, "_"));
      fd.append("experience_years", String(form.experience_years || 4));
      fd.append("custom_subject", form.custom_subject);
      fd.append("custom_body", form.custom_body);
      if (uploadedResume) {
        fd.append("resume_file", uploadedResume);
      }
      const r = await fetch(`${API}/send-direct`, {
        method: "POST",
        body: fd,
      });
      const result = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(result.detail || "Send failed.");
      const resumeType = result.resume === "uploaded" ? " (uploaded resume)" : " (generated resume)";
      showFlash(`Email sent to ${form.to_email}!${resumeType}`);
      setForm(f => ({ ...EMPTY_FORM, role_key: f.role_key, role_title: f.role_title }));
      setValidation(null); setShowCC(false);
      autoLoadTemplate(form.role_key);
    } catch (err) { showFlash(err.message, true); }
    finally { setDirectSending(false); }
  }

  // ── Resume Builder ──────────────────────────────────────────────

  function fetchRolesList() {
    fetch(`${API}/roles?all=true`).then(r => r.ok ? r.json() : []).then(data => {
      const list = Array.isArray(data) ? data : [];
      setAllRoles(list);
    }).catch(() => {});
  }

  async function fetchRoleDetail(key) {
    if (!key) { setRoleDetail(null); return; }
    try {
      const r = await fetch(`${API}/roles/${key}`);
      if (r.ok) {
        const data = await r.json();
        if (data.skills && !Array.isArray(data.skills)) {
          data.skills = Object.entries(data.skills).map(([category, skills]) => ({ category, skills }));
        }
        setRoleDetail(data);
      }
    } catch { showFlash("Failed to load role details.", true); }
  }

  useEffect(() => {
    if (tab === "resume" && roles.length && !selectedRole) {
      setSelectedRole(roles[0].key);
    }
  }, [tab, roles, selectedRole]);

  useEffect(() => {
    if (selectedRole) fetchRoleDetail(selectedRole);
    else setRoleDetail(null);
  }, [selectedRole]);

  function updateRoleField(field, value) {
    setRoleDetail(d => d ? { ...d, [field]: value } : d);
  }

  async function saveBasicInfo() {
    if (!roleDetail) return;
    setSavingRole(true);
    try {
      const r = await fetch(`${API}/roles/${selectedRole}`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: roleDetail.title, summary: roleDetail.summary, previous_title: roleDetail.previous_title, coursework: roleDetail.coursework }),
      });
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || "Save failed.");
      showFlash("Basic info saved.");
      fetchRolesList(); fetchRoleDetail(selectedRole);
    } catch (err) { showFlash(err.message, true); }
    finally { setSavingRole(false); }
  }

  async function saveSkills() {
    if (!roleDetail) return;
    setSavingRole(true);
    try {
      const skills = (roleDetail.skills || []).map(s => ({ category: s.category, skills: Array.isArray(s.skills) ? s.skills : [] }));
      const r = await fetch(`${API}/roles/${selectedRole}/skills`, {
        method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(skills),
      });
      if (!r.ok) throw new Error("Save failed.");
      showFlash("Skills saved.");
      fetchRoleDetail(selectedRole);
    } catch (err) { showFlash(err.message, true); }
    finally { setSavingRole(false); }
  }

  function updateSkillCategory(index, field, value) {
    setRoleDetail(d => {
      if (!d) return d;
      const skills = [...(d.skills || [])];
      skills[index] = { ...skills[index], [field]: value };
      return { ...d, skills };
    });
  }

  function addSkillCategory() {
    setRoleDetail(d => d ? { ...d, skills: [...(d.skills || []), { category: "", skills: [] }] } : d);
  }

  function removeSkillCategory(index) {
    setRoleDetail(d => {
      if (!d) return d;
      const skills = [...(d.skills || [])];
      skills.splice(index, 1);
      return { ...d, skills };
    });
  }

  async function saveClients() {
    if (!roleDetail) return;
    setSavingRole(true);
    try {
      const payload = (roleDetail.clients || []).map(c => ({
        position_index: c.position_index,
        bullets: c.bullets || [],
        client_name: c.client_name,
        client_location: c.client_location,
        min_years: c.min_years,
      }));
      const r = await fetch(`${API}/roles/${selectedRole}/experience`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error("Save failed.");
      showFlash("Client experience saved.");
      fetchRoleDetail(selectedRole);
    } catch (err) { showFlash(err.message, true); }
    finally { setSavingRole(false); }
  }

  function updateClientBullet(clientIndex, bulletIndex, value) {
    setRoleDetail(d => {
      if (!d) return d;
      const clients = [...(d.clients || [])];
      const bullets = [...clients[clientIndex].bullets];
      bullets[bulletIndex] = value;
      clients[clientIndex] = { ...clients[clientIndex], bullets };
      return { ...d, clients };
    });
  }

  function addClientBullet(clientIndex) {
    setRoleDetail(d => {
      if (!d) return d;
      const clients = [...(d.clients || [])];
      clients[clientIndex] = { ...clients[clientIndex], bullets: [...clients[clientIndex].bullets, ""] };
      return { ...d, clients };
    });
  }

  function removeClientBullet(clientIndex, bulletIndex) {
    setRoleDetail(d => {
      if (!d) return d;
      const clients = [...(d.clients || [])];
      const bullets = [...clients[clientIndex].bullets];
      bullets.splice(bulletIndex, 1);
      clients[clientIndex] = { ...clients[clientIndex], bullets };
      return { ...d, clients };
    });
  }

  async function saveAchievements() {
    if (!roleDetail) return;
    setSavingRole(true);
    try {
      const r = await fetch(`${API}/roles/${selectedRole}/achievements`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(roleDetail.achievements || []),
      });
      if (!r.ok) throw new Error("Save failed.");
      showFlash("Achievements saved.");
      fetchRoleDetail(selectedRole);
    } catch (err) { showFlash(err.message, true); }
    finally { setSavingRole(false); }
  }

  function updateAchievement(index, value) {
    setRoleDetail(d => {
      if (!d) return d;
      const achievements = [...(d.achievements || [])];
      achievements[index] = value;
      return { ...d, achievements };
    });
  }

  function addAchievement() {
    setRoleDetail(d => d ? { ...d, achievements: [...(d.achievements || []), ""] } : d);
  }

  function removeAchievement(index) {
    setRoleDetail(d => {
      if (!d) return d;
      const achievements = [...(d.achievements || [])];
      achievements.splice(index, 1);
      return { ...d, achievements };
    });
  }

  async function saveFocus() {
    if (!roleDetail) return;
    setSavingRole(true);
    try {
      const r = await fetch(`${API}/roles/${selectedRole}/focus`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(roleDetail.focus || []),
      });
      if (!r.ok) throw new Error("Save failed.");
      showFlash("Focus areas saved.");
      fetchRoleDetail(selectedRole);
    } catch (err) { showFlash(err.message, true); }
    finally { setSavingRole(false); }
  }

  function updateFocusItem(index, value) {
    setRoleDetail(d => {
      if (!d) return d;
      const focus = [...(d.focus || [])];
      focus[index] = value;
      return { ...d, focus };
    });
  }

  function addFocusItem() {
    setRoleDetail(d => d ? { ...d, focus: [...(d.focus || []), ""] } : d);
  }

  function removeFocusItem(index) {
    setRoleDetail(d => {
      if (!d) return d;
      const focus = [...(d.focus || [])];
      focus.splice(index, 1);
      return { ...d, focus };
    });
  }

  async function createRole() {
    if (!newRoleForm.key || !newRoleForm.title) { showFlash("Key and title are required.", true); return; }
    setSavingRole(true);
    try {
      const r = await fetch(`${API}/roles`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: newRoleForm.key, title: newRoleForm.title, summary: "", previous_title: "", coursework: "" }),
      });
      if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || "Create failed.");
      showFlash("Role created.");
      const createdKey = newRoleForm.key;
      setNewRoleForm({ key: "", title: "" });
      setShowNewRole(false);
      fetchRolesList();
      setSelectedRole(createdKey);
    } catch (err) { showFlash(err.message, true); }
    finally { setSavingRole(false); }
  }

  async function deleteSelectedRole() {
    if (!selectedRole) return;
    if (!confirm(`Delete role "${selectedRole}"? This cannot be undone.`)) return;
    setSavingRole(true);
    try {
      const r = await fetch(`${API}/roles/${selectedRole}`, { method: "DELETE" });
      if (!r.ok) throw new Error("Delete failed.");
      showFlash("Role deleted.");
      const remaining = roles.filter(r => r.key !== selectedRole);
      setSelectedRole(remaining.length ? remaining[0].key : null);
      setRoleDetail(null);
      fetchRolesList();
    } catch (err) { showFlash(err.message, true); }
    finally { setSavingRole(false); }
  }

  async function saveProfileForm() {
    setSavingRole(true);
    try {
      const r = await fetch(`${API}/profile`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profileForm),
      });
      if (!r.ok) throw new Error("Save failed.");
      const data = await r.json();
      setProfile(data);
      setShowProfileEditor(false);
      showFlash("Profile saved.");
    } catch (err) { showFlash(err.message, true); }
    finally { setSavingRole(false); }
  }

  return (
    <main>
      <div className="app-header">
        <h1>Email Resume</h1>
        <p>Send job-application emails with auto-generated templates</p>
      </div>

      <div className="toast-container">
        {flash && (
          <div className={`toast ${flash.err ? "toast-error" : "toast-success"}`}>
            <span className="toast-icon">{flash.err ? "✘" : "✔"}</span>
            <span>{flash.msg}</span>
            <button className="toast-close" onClick={() => setFlash(null)}>&times;</button>
          </div>
        )}
      </div>

      <div className="tabs">
        <button className={`tab${tab === "queue" ? " active" : ""}`} onClick={() => setTab("queue")}>
          Send Email
        </button>
        <button className={`tab${tab === "resume" ? " active" : ""}`} onClick={() => setTab("resume")}>
          Resume Builder
        </button>
      </div>

      {/* ══════════ SEND EMAIL ══════════ */}
      {tab === "queue" && (
        <>
          <div className="card">
            <div className="form-header">
              <div>
                <h2>Send Email</h2>
                <p className="subtitle">Fill in the details — template auto-fills when you select a role.</p>
              </div>
            </div>

            {profile.name && (
              <div className="profile-banner">
                <strong>{profile.name}</strong>
                <span>{[profile.email, profile.phone].filter(Boolean).join(" · ")}</span>
              </div>
            )}

            <form onSubmit={sendDirect}>
              <div className="form-grid">
                <label>
                  To Email *
                  <div className="input-with-btn">
                    <input type="email" value={form.to_email} onChange={e => updateForm("to_email", e.target.value)} placeholder="hr@company.com" required />
                    <button type="button" className="btn-validate" onClick={() => validateEmail(form.to_email)} disabled={!form.to_email || validating}>
                      {validating ? <><span className="spinner" />Checking</> : "Verify"}
                    </button>
                  </div>
                </label>

                {showCC || form.cc_emails ? (
                  <label>
                    CC (comma-separated)
                    <div className="input-with-btn">
                      <input type="text" value={form.cc_emails} onChange={e => updateForm("cc_emails", e.target.value)} placeholder="cc1@company.com, cc2@company.com" />
                      <button type="button" className="btn-cc-remove" onClick={() => { updateForm("cc_emails", ""); setShowCC(false); }}>Remove</button>
                    </div>
                  </label>
                ) : (
                  <label>
                    <span>&nbsp;</span>
                    <button type="button" className="btn-add-cc" onClick={() => setShowCC(true)}>+ Add CC</button>
                  </label>
                )}

                <label>
                  HR / Contact Name
                  <input type="text" value={form.hr_name} onChange={e => updateForm("hr_name", e.target.value)} placeholder="Optional" />
                </label>

                <label>
                  Company Name
                  <input type="text" value={form.company_name} onChange={e => updateForm("company_name", e.target.value)} placeholder="Optional" />
                </label>

                {hasDbRoles ? (
                  <label>
                    Target Role *
                    <select value={form.role_key} onChange={e => updateForm("role_key", e.target.value)}>
                      <option value="">-- Select Role --</option>
                      {roles.map(r => <option key={r.key} value={r.key}>{r.title}</option>)}
                    </select>
                  </label>
                ) : (
                  <label>
                    Target Role *
                    <input type="text" value={form.role_title} onChange={e => updateForm("role_title", e.target.value)} placeholder="e.g. Software Engineer" />
                  </label>
                )}

                <label>
                  Experience (Years)
                  <select value={form.experience_years} onChange={e => updateForm("experience_years", parseInt(e.target.value, 10))}>
                    {[1,2,3,4,5,6,7,8,9,10].map(n => <option key={n} value={n}>{n} {n === 1 ? "Year" : "Years"}</option>)}
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

              {roleSkills.length > 0 && (
                <div className="skills-panel">
                  <strong>Skills for this role</strong>
                  <div className="skills-grid">
                    {roleSkills.map(cat => (
                      <div key={cat.category} className="skill-category">
                        <span className="cat-label">{cat.category}</span>
                        <div className="skill-chips">{(Array.isArray(cat.skills) ? cat.skills : []).map(s => <span key={s} className="chip">{s}</span>)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="message-section">
                <div className="message-section-header">
                  <div>
                    <label style={{ marginBottom: 0 }}>Email Message</label>
                    <p className="subtitle" style={{ marginBottom: 0 }}>
                      Templates auto-fill when you select a role.
                    </p>
                  </div>
                </div>
                {loadingPreview && <div className="template-loading"><span className="spinner" /> Loading template...</div>}
                <label>Subject <input type="text" value={form.custom_subject} onChange={e => updateForm("custom_subject", e.target.value)} placeholder="Subject auto-fills with template" /></label>
                <label>Body <textarea value={form.custom_body} onChange={e => updateForm("custom_body", e.target.value)} placeholder="Template auto-fills when you select a role" rows={10} /></label>
              </div>

              <div className="resume-upload-section">
                <label>Resume Attachment</label>
                <p className="subtitle" style={{ marginTop: 0, marginBottom: 8 }}>
                  {uploadedResume
                    ? `Using uploaded: ${uploadedResume.name}`
                    : `Auto-generated resume for "${roles.find(r => r.key === form.role_key)?.title || form.role_key || "selected role"}" will be attached.`}
                </p>
                <div className="resume-upload-row">
                  <label className="btn-upload-resume">
                    {uploadedResume ? "Change File" : "Upload Resume"}
                    <input type="file" accept=".pdf,.doc,.docx" onChange={e => {
                      const file = e.target.files?.[0];
                      if (file) setUploadedResume(file);
                      e.target.value = "";
                    }} style={{ display: "none" }} />
                  </label>
                  {uploadedResume && (
                    <button type="button" className="btn-remove-resume" onClick={() => setUploadedResume(null)}>
                      Remove &amp; use generated
                    </button>
                  )}
                </div>
              </div>

              <div className="actions">
                <button type="submit" className="btn-send-direct" disabled={directSending || !form.to_email}>
                  {directSending ? <><span className="spinner" />Sending...</> : "Send Email"}
                </button>
              </div>
            </form>
          </div>
        </>
      )}

      {/* ══════════ RESUME BUILDER ══════════ */}
      {tab === "resume" && (
        <div className="resume-builder">
          <div className="role-sidebar">
            <div className="sidebar-header">
              <h3>Roles</h3>
              <button className="btn-primary btn-sm" onClick={() => setShowNewRole(true)}>+ New</button>
            </div>

            {showNewRole && (
              <div className="new-role-form">
                <input placeholder="key (e.g. sde_backend)" value={newRoleForm.key}
                  onChange={e => setNewRoleForm(f => ({ ...f, key: e.target.value }))} />
                <input placeholder="Title" value={newRoleForm.title}
                  onChange={e => setNewRoleForm(f => ({ ...f, title: e.target.value }))} />
                <div className="new-role-actions">
                  <button className="btn-primary btn-sm" onClick={createRole} disabled={savingRole}>Create</button>
                  <button className="btn-secondary btn-sm" onClick={() => { setShowNewRole(false); setNewRoleForm({ key: "", title: "" }); }}>Cancel</button>
                </div>
              </div>
            )}

            <div className="role-list">
              {allRoles.map(r => (
                <div key={r.key} className={`role-item${selectedRole === r.key ? " active" : ""}`}
                  onClick={() => setSelectedRole(r.key)}>
                  <strong>{r.title}</strong>
                  <span className="role-item-key">{r.key}</span>
                </div>
              ))}
              {!allRoles.length && <p className="empty-state">No roles yet. Connect Neon DB to manage roles.</p>}
            </div>
          </div>

          <div className="role-editor">
            {roleDetail ? (
              <>
                <div className="editor-header">
                  <div>
                    <h2>{roleDetail.title}</h2>
                    <span className="role-key-badge">{selectedRole}</span>
                  </div>
                  <div className="editor-actions">
                    <button className="btn-secondary btn-sm" onClick={() => { setProfileForm({ ...profile }); setShowProfileEditor(true); }}>Edit Profile</button>
                    <button className="btn-delete btn-sm" onClick={deleteSelectedRole}>Delete Role</button>
                  </div>
                </div>

                <div className="download-section">
                  <div className="download-row">
                    <label className="download-label">
                      Experience
                      <select value={builderExpYears} onChange={e => setBuilderExpYears(parseInt(e.target.value, 10))} className="exp-select">
                        {[1,2,3,4,5,6,7,8,9,10].map(n => <option key={n} value={n}>{n} {n === 1 ? "Year" : "Years"}</option>)}
                      </select>
                    </label>
                    <div className="download-btns">
                      <button className="btn-primary" onClick={() => window.open(`${API}/resume/${selectedRole}/pdf?experience_years=${builderExpYears}`, "_blank")}>
                        Preview PDF
                      </button>
                      <button className="btn-send" onClick={() => {
                        const a = document.createElement("a");
                        a.href = `${API}/resume/${selectedRole}/pdf?experience_years=${builderExpYears}`;
                        a.download = `${selectedRole}_resume_${builderExpYears}yr.pdf`;
                        document.body.appendChild(a); a.click(); document.body.removeChild(a);
                      }}>
                        Download PDF
                      </button>
                      <button className="btn-secondary" onClick={() => {
                        const a = document.createElement("a");
                        a.href = `${API}/resume/${selectedRole}/latex?experience_years=${builderExpYears}`;
                        a.download = `${selectedRole}_resume_${builderExpYears}yr.tex`;
                        document.body.appendChild(a); a.click(); document.body.removeChild(a);
                      }}>
                        Download LaTeX
                      </button>
                    </div>
                  </div>
                </div>

                <div className="editor-section">
                  <h3>Basic Information</h3>
                  <div className="form-grid">
                    <label>Title <input value={roleDetail.title || ""} onChange={e => updateRoleField("title", e.target.value)} /></label>
                    <label>Previous Title <input value={roleDetail.previous_title || ""} onChange={e => updateRoleField("previous_title", e.target.value)} /></label>
                  </div>
                  <label>Summary <textarea rows={3} value={roleDetail.summary || ""} onChange={e => updateRoleField("summary", e.target.value)} /></label>
                  <label>Coursework <textarea rows={2} value={roleDetail.coursework || ""} onChange={e => updateRoleField("coursework", e.target.value)} /></label>
                  <div className="section-actions">
                    <button className="btn-primary btn-sm" onClick={saveBasicInfo} disabled={savingRole}>{savingRole && <span className="spinner" />}Save Basic Info</button>
                  </div>
                </div>

                <div className="editor-section">
                  <div className="section-header"><h3>Skills</h3><button className="btn-secondary btn-sm" onClick={addSkillCategory}>+ Category</button></div>
                  {(roleDetail.skills || []).map((cat, i) => (
                    <div key={i} className="skill-row">
                      <input className="skill-cat-input" value={cat.category} onChange={e => updateSkillCategory(i, "category", e.target.value)} placeholder="Category" />
                      <input className="skill-values-input" value={(cat.skills || []).join(", ")}
                        onChange={e => updateSkillCategory(i, "skills", e.target.value.split(",").map(s => s.trim()).filter(Boolean))} placeholder="Skill1, Skill2, Skill3" />
                      <button className="btn-delete btn-xs" onClick={() => removeSkillCategory(i)}>X</button>
                    </div>
                  ))}
                  {!(roleDetail.skills || []).length && <p className="empty-state">No skill categories yet.</p>}
                  <div className="section-actions"><button className="btn-primary btn-sm" onClick={saveSkills} disabled={savingRole}>Save Skills</button></div>
                </div>

                <div className="editor-section">
                  <h3>Client Experience</h3>
                  {(roleDetail.clients || []).map((client, i) => (
                    <div key={i} className="experience-block">
                      <h4>{client.client_name} ({client.client_location}) — min {client.min_years}yr</h4>
                      <div className="bullet-list">
                        {(client.bullets || []).map((b, j) => (
                          <div key={j} className="bullet-item">
                            <span className="bullet-marker">&bull;</span>
                            <input value={b} onChange={e => updateClientBullet(i, j, e.target.value)} />
                            <button className="btn-delete btn-xs" onClick={() => removeClientBullet(i, j)}>X</button>
                          </div>
                        ))}
                        <button className="btn-add-bullet" onClick={() => addClientBullet(i)}>+ Bullet</button>
                      </div>
                    </div>
                  ))}
                  {!(roleDetail.clients || []).length && <p className="empty-state">No client entries.</p>}
                  <div className="section-actions"><button className="btn-primary btn-sm" onClick={saveClients} disabled={savingRole}>Save Clients</button></div>
                </div>

                <div className="editor-section">
                  <div className="section-header"><h3>Achievements</h3><button className="btn-secondary btn-sm" onClick={addAchievement}>+ Add</button></div>
                  <div className="bullet-list">
                    {(roleDetail.achievements || []).map((a, i) => (
                      <div key={i} className="bullet-item">
                        <span className="bullet-marker">&bull;</span>
                        <input value={a} onChange={e => updateAchievement(i, e.target.value)} />
                        <button className="btn-delete btn-xs" onClick={() => removeAchievement(i)}>X</button>
                      </div>
                    ))}
                  </div>
                  {!(roleDetail.achievements || []).length && <p className="empty-state">No achievements yet.</p>}
                  <div className="section-actions"><button className="btn-primary btn-sm" onClick={saveAchievements} disabled={savingRole}>Save Achievements</button></div>
                </div>

                <div className="editor-section">
                  <div className="section-header"><h3>Focus Areas</h3><button className="btn-secondary btn-sm" onClick={addFocusItem}>+ Add</button></div>
                  <div className="bullet-list">
                    {(roleDetail.focus || []).map((f, i) => (
                      <div key={i} className="bullet-item">
                        <span className="bullet-marker">&bull;</span>
                        <input value={f} onChange={e => updateFocusItem(i, e.target.value)} />
                        <button className="btn-delete btn-xs" onClick={() => removeFocusItem(i)}>X</button>
                      </div>
                    ))}
                  </div>
                  {!(roleDetail.focus || []).length && <p className="empty-state">No focus areas yet.</p>}
                  <div className="section-actions"><button className="btn-primary btn-sm" onClick={saveFocus} disabled={savingRole}>Save Focus Areas</button></div>
                </div>
              </>
            ) : (
              <div className="editor-empty">
                <p>{roles.length ? "Select a role from the sidebar to start editing." : "Connect Neon DB to manage resume roles, or create a new role."}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ══════════ PROFILE EDITOR MODAL ══════════ */}
      {showProfileEditor && (
        <div className="modal-overlay" onClick={() => setShowProfileEditor(false)}>
          <div className="profile-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Edit Profile</h2>
              <button className="btn-secondary btn-sm" onClick={() => setShowProfileEditor(false)}>Close</button>
            </div>
            <div className="modal-body">
              <h3 className="modal-section-title-first">Personal Information</h3>
              <div className="form-grid">
                <label>Name <input value={profileForm.name || ""} onChange={e => setProfileForm(f => ({ ...f, name: e.target.value }))} /></label>
                <label>Email <input value={profileForm.email || ""} onChange={e => setProfileForm(f => ({ ...f, email: e.target.value }))} /></label>
                <label>Phone <input value={profileForm.phone || ""} onChange={e => setProfileForm(f => ({ ...f, phone: e.target.value }))} /></label>
                <label>Location <input value={profileForm.location || ""} onChange={e => setProfileForm(f => ({ ...f, location: e.target.value }))} /></label>
                <label>LinkedIn <input value={profileForm.linkedin || ""} onChange={e => setProfileForm(f => ({ ...f, linkedin: e.target.value }))} /></label>
                <label>GitHub <input value={profileForm.github || ""} onChange={e => setProfileForm(f => ({ ...f, github: e.target.value }))} /></label>
                <label>Portfolio <input value={profileForm.portfolio || ""} onChange={e => setProfileForm(f => ({ ...f, portfolio: e.target.value }))} /></label>
              </div>
              <h3>Education</h3>
              <div className="form-grid">
                <label>Education <input value={profileForm.education || ""} onChange={e => setProfileForm(f => ({ ...f, education: e.target.value }))} /></label>
                <label>Graduation Year <input value={profileForm.graduation_year || ""} onChange={e => setProfileForm(f => ({ ...f, graduation_year: e.target.value }))} /></label>
                <label>Experience Years <input value={profileForm.experience_years || ""} onChange={e => setProfileForm(f => ({ ...f, experience_years: e.target.value }))} /></label>
              </div>
              <h3>Company 1 (Current)</h3>
              <div className="form-grid">
                <label>Company Name <input value={profileForm.company_1_name || ""} onChange={e => setProfileForm(f => ({ ...f, company_1_name: e.target.value }))} /></label>
                <label>Role <input value={profileForm.company_1_role || ""} onChange={e => setProfileForm(f => ({ ...f, company_1_role: e.target.value }))} /></label>
                <label>Location <input value={profileForm.company_1_location || ""} onChange={e => setProfileForm(f => ({ ...f, company_1_location: e.target.value }))} /></label>
                <label>Duration <input value={profileForm.company_1_duration || ""} onChange={e => setProfileForm(f => ({ ...f, company_1_duration: e.target.value }))} /></label>
              </div>
              <h3>Company 2 (Previous)</h3>
              <div className="form-grid">
                <label>Company Name <input value={profileForm.company_2_name || ""} onChange={e => setProfileForm(f => ({ ...f, company_2_name: e.target.value }))} /></label>
                <label>Role <input value={profileForm.company_2_role || ""} onChange={e => setProfileForm(f => ({ ...f, company_2_role: e.target.value }))} /></label>
                <label>Location <input value={profileForm.company_2_location || ""} onChange={e => setProfileForm(f => ({ ...f, company_2_location: e.target.value }))} /></label>
                <label>Duration <input value={profileForm.company_2_duration || ""} onChange={e => setProfileForm(f => ({ ...f, company_2_duration: e.target.value }))} /></label>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-primary" onClick={saveProfileForm} disabled={savingRole}>{savingRole && <span className="spinner" />}Save Profile</button>
              <button className="btn-secondary" onClick={() => setShowProfileEditor(false)}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

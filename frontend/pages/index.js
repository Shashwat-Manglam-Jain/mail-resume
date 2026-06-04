import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const messageOptions = [
  { value: "initial", label: "Initial Message" },
  { value: "followup", label: "Follow Up" },
  { value: "interview", label: "Interview Invite" },
];

const emptyResumeDetails = {
  name: "",
  email: "",
  phone: "",
  location: "",
  linkedin: "",
  github: "",
  portfolio: "",
  education: "",
  graduation_year: "",
};

export default function Home() {
  const [records, setRecords] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState("");
  const [resumeDetails, setResumeDetails] = useState(emptyResumeDetails);
  const [form, setForm] = useState({ to_email: "", message_type: "initial", resume: null });
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRecords();
    fetchTemplates();
  }, []);

  const activeTemplate = templates.find((template) => template.key === selectedTemplate);

  async function fetchRecords() {
    try {
      const response = await fetch(`${API_URL}/records`);
      const data = await response.json();
      setRecords(data);
    } catch (error) {
      setStatus("Unable to load records. Is the backend running?");
    }
  }

  async function fetchTemplates() {
    try {
      const response = await fetch(`${API_URL}/resume-templates`);
      const data = await response.json();
      setTemplates(data);
      if (data.length) {
        setSelectedTemplate(data[0].key);
      }
    } catch (error) {
      setStatus("Unable to load resume templates. Is the backend running?");
    }
  }

  async function downloadLatexResume(event) {
    event.preventDefault();
    if (!selectedTemplate) {
      setStatus("Please choose a resume role first.");
      return;
    }

    setLoading(true);
    setStatus("Generating LaTeX resume...");
    try {
      const response = await fetch(`${API_URL}/resume-templates/${selectedTemplate}/latex`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(resumeDetails),
      });
      const latex = await response.text();
      if (!response.ok) {
        throw new Error(latex || "Failed to generate LaTeX resume.");
      }
      const blob = new Blob([latex], { type: "application/x-tex" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const fileName = `${selectedTemplate}_resume.tex`;
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setStatus(`Downloaded ${fileName}.`);
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function createRecord(event) {
    event.preventDefault();
    if (!form.to_email || !form.resume) {
      setStatus("Please enter an email and choose a resume file.");
      return;
    }

    const formData = new FormData();
    formData.append("to_email", form.to_email);
    formData.append("message_type", form.message_type);
    formData.append("resume", form.resume);

    setLoading(true);
    setStatus("Creating record...");
    try {
      const response = await fetch(`${API_URL}/records`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || "Failed to create record.");
      }
      setForm({ to_email: "", message_type: "initial", resume: null });
      fetchRecords();
      setStatus("Record created successfully.");
      document.getElementById("resume-file").value = "";
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function executeAll() {
    if (!records.length) {
      setStatus("No records available to execute.");
      return;
    }
    setLoading(true);
    setStatus("Executing bulk send...");
    try {
      const response = await fetch(`${API_URL}/execute`, { method: "POST" });
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Execute request failed.");
      }
      setStatus(`Sent ${result.sent} emails, failed ${result.failed}.`);
      fetchRecords();
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function deleteRecord(id) {
    setLoading(true);
    setStatus("Removing record...");
    try {
      const response = await fetch(`${API_URL}/records/${id}`, { method: "DELETE" });
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || "Failed to delete record.");
      }
      fetchRecords();
      setStatus("Record removed.");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <div className="card">
        <h1>Resume Generator & Bulk Sender</h1>
        <p>Pick a role, fill basic details, download a ready LaTeX resume, then attach any resume file for bulk email sending.</p>
      </div>

      {status ? <div className="status">{status}</div> : null}

      <div className="card">
        <div className="section-heading">
          <div>
            <h2>Create dummy LaTeX resume</h2>
            <p>ATS skills, job-focused projects, summary, experience, certifications, and achievements are already filled for each role.</p>
          </div>
        </div>

        <form onSubmit={downloadLatexResume}>
          <label>
            Resume role
            <select value={selectedTemplate} onChange={(event) => setSelectedTemplate(event.target.value)}>
              {templates.map((template) => (
                <option key={template.key} value={template.key}>
                  {template.title}
                </option>
              ))}
            </select>
          </label>

          {activeTemplate ? (
            <div className="template-preview">
              <strong>{activeTemplate.title}</strong>
              <p>{activeTemplate.summary}</p>
              <div className="skill-list">
                {activeTemplate.skills.map((skill) => (
                  <span key={skill}>{skill}</span>
                ))}
              </div>
              {activeTemplate.focus?.length ? (
                <div className="focus-list">
                  <strong>Selection focus</strong>
                  <ul>
                    {activeTemplate.focus.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </div>
          ) : null}

          <div className="form-grid">
            <label>
              Full name
              <input
                type="text"
                value={resumeDetails.name}
                onChange={(event) => setResumeDetails({ ...resumeDetails, name: event.target.value })}
                placeholder="Your Name"
              />
            </label>

            <label>
              Email
              <input
                type="email"
                value={resumeDetails.email}
                onChange={(event) => setResumeDetails({ ...resumeDetails, email: event.target.value })}
                placeholder="you@example.com"
              />
            </label>

            <label>
              Phone
              <input
                type="tel"
                value={resumeDetails.phone}
                onChange={(event) => setResumeDetails({ ...resumeDetails, phone: event.target.value })}
                placeholder="+91 98765 43210"
              />
            </label>

            <label>
              Location
              <input
                type="text"
                value={resumeDetails.location}
                onChange={(event) => setResumeDetails({ ...resumeDetails, location: event.target.value })}
                placeholder="Bengaluru, India"
              />
            </label>

            <label>
              LinkedIn
              <input
                type="text"
                value={resumeDetails.linkedin}
                onChange={(event) => setResumeDetails({ ...resumeDetails, linkedin: event.target.value })}
                placeholder="linkedin.com/in/your-profile"
              />
            </label>

            <label>
              GitHub
              <input
                type="text"
                value={resumeDetails.github}
                onChange={(event) => setResumeDetails({ ...resumeDetails, github: event.target.value })}
                placeholder="github.com/your-username"
              />
            </label>

            <label>
              Portfolio
              <input
                type="text"
                value={resumeDetails.portfolio}
                onChange={(event) => setResumeDetails({ ...resumeDetails, portfolio: event.target.value })}
                placeholder="yourportfolio.com"
              />
            </label>

            <label>
              Education
              <input
                type="text"
                value={resumeDetails.education}
                onChange={(event) => setResumeDetails({ ...resumeDetails, education: event.target.value })}
                placeholder="B.Tech CSE, Your College"
              />
            </label>

            <label>
              Graduation year
              <input
                type="text"
                value={resumeDetails.graduation_year}
                onChange={(event) => setResumeDetails({ ...resumeDetails, graduation_year: event.target.value })}
                placeholder="2026"
              />
            </label>
          </div>

          <div className="actions">
            <button className="primary" type="submit" disabled={loading || !templates.length}>
              Download LaTeX
            </button>
            <button
              className="secondary"
              type="button"
              disabled={loading}
              onClick={() => setResumeDetails(emptyResumeDetails)}
            >
              Clear details
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <h2>Add a new record</h2>
        <form onSubmit={createRecord}>
          <label>
            Recipient email
            <input
              type="email"
              value={form.to_email}
              onChange={(event) => setForm({ ...form, to_email: event.target.value })}
              placeholder="recipient@example.com"
              required
            />
          </label>

          <label>
            Message type
            <select
              value={form.message_type}
              onChange={(event) => setForm({ ...form, message_type: event.target.value })}
            >
              {messageOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            Resume attachment
            <input
              id="resume-file"
              type="file"
              accept=".pdf,.doc,.docx,.tex"
              onChange={(event) => setForm({ ...form, resume: event.target.files[0] })}
              required
            />
          </label>

          <div>
            <button className="primary" type="submit" disabled={loading}>
              Add record
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <h2>Pending records</h2>
        <p>{records.length} record(s) waiting to execute.</p>
        <button className="primary" type="button" onClick={executeAll} disabled={loading || !records.length}>
          Execute send
        </button>

        {records.length ? (
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>Message type</th>
                <th>Resume</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.id}>
                  <td>{record.to_email}</td>
                  <td>{record.message_type}</td>
                  <td>{record.original_filename}</td>
                  <td>
                    <button className="secondary" type="button" onClick={() => deleteRecord(record.id)} disabled={loading}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No records yet.</p>
        )}
      </div>
    </main>
  );
}

import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function ResumeEditor() {
  const [file, setFile] = useState(null);
  const [sections, setSections] = useState([]);

  // Fetch existing sections on load
  useEffect(() => {
    fetchSections();
  }, []);

  async function fetchSections() {
    try {
      const resp = await axios.get("http://localhost:5000/sections");
      setSections(resp.data);
    } catch (err) {
      console.error(err);
    }
  }

  // Handle PDF selection
  function onFileChange(e) {
    setFile(e.target.files[0]);
  }

  // Upload PDF to backend
  async function uploadResume() {
    if (!file) return alert("Select a PDF first");
    const form = new FormData();
    form.append("file", file);
    try {
      await axios.post("http://localhost:5000/upload", form, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      await fetchSections();
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  }

  // Update a single section
  async function saveSection(id, content) {
    try {
      await axios.put(`http://localhost:5000/sections/${id}`, { content });
      alert("Saved!");
    } catch (err) {
      console.error(err);
      alert("Save failed");
    }
  }

  return (
    <div>
      <h1>Resume Editor</h1>

      <div style={{ marginBottom: 20 }}>
        <input type="file" accept=".pdf" onChange={onFileChange} />
        <button onClick={uploadResume} style={{ marginLeft: 10 }}>
          Upload & Parse
        </button>
      </div>

      {sections.map(sec => (
        <div key={sec.id} style={{
          border: '1px solid #ccc', padding: 15, marginBottom: 15, borderRadius: 4
        }}>
          <h2>{sec.title}</h2>
          <textarea
            style={{ width: '100%', minHeight: 100 }}
            value={sec.content}
            onChange={e =>
              setSections(sections.map(s =>
                s.id === sec.id ? { ...s, content: e.target.value } : s
              ))
            }
          />
          <button onClick={() => saveSection(sec.id, sec.content)}>
            Save Section
          </button>
        </div>
      ))}
    </div>
  );
}

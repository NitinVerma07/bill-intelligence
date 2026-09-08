import React, { useRef, useState } from "react";
import { FileImage, Upload, ShieldCheck } from "lucide-react";

export default function UploadScreen({ onBillUploaded }) {
  const [active, setActive] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const input = useRef(null);

  async function upload(file) {
    if (!file || !file.type.startsWith("image/")) {
      setError("Please select a JPEG, PNG, or WebP bill image.");
      return;
    }
    setError("");
    setBusy(true);
    const form = new FormData();
    form.append("file", file);

    try {
      const response = await fetch("/api/v1/upload", { method: "POST", body: form });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Upload failed.");
      onBillUploaded(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <div style={{textAlign:"center", marginBottom:25}}>
        <h1>Split the actual bill</h1>
        <p className="muted">Upload a real receipt. Local OCR extracts the printed items; you review them before any money is calculated.</p>
      </div>

      {error && <div className="alert">{error}</div>}

      <div
        className={`card drop ${active ? "active" : ""}`}
        onDragEnter={(e)=>{e.preventDefault();setActive(true)}}
        onDragOver={(e)=>e.preventDefault()}
        onDragLeave={()=>setActive(false)}
        onDrop={(e)=>{e.preventDefault();setActive(false);upload(e.dataTransfer.files[0])}}
        onClick={()=>!busy && input.current?.click()}
      >
        <input ref={input} hidden type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>upload(e.target.files[0])}/>
        {busy ? (
          <>
            <div className="big">⏳</div>
            <h2>Reading your receipt...</h2>
            <p className="muted">Preprocessing image → local OCR → structured bill</p>
          </>
        ) : (
          <>
            <FileImage size={54} />
            <h2>Drop bill photo here</h2>
            <p className="muted">or click to browse • JPEG / PNG / WebP</p>
            <button className="btn primary" type="button"><Upload size={16}/> Upload Bill</button>
          </>
        )}
      </div>

      <div className="grid" style={{marginTop:18}}>
        <div className="card"><ShieldCheck size={22}/><h3>No API Key</h3><p className="muted">No Gemini, Claude, OpenAI or cloud API is required.</p></div>
        <div className="card"><h3>Human Review</h3><p className="muted">OCR results are editable before calculation.</p></div>
        <div className="card"><h3>Pure Python Math</h3><p className="muted">Tax, service charge, discount and rounding are calculated locally.</p></div>
      </div>
    </div>
  );
}

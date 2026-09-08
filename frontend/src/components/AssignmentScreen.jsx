import React, { useMemo, useState } from "react";

export default function AssignmentScreen({ bill, people, setPeople, onBack, onCalculated }) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  function addPerson() {
    const clean = name.trim();
    if (!clean) return;
    if (people.length >= 7) return setError("Maximum 7 people for this demo.");
    setPeople([...people, {id:`p${Date.now()}`, name:clean, assigned_item_indices:[]}]);
    setName("");
  }

  function toggle(personId, index) {
    setPeople(people.map(p => p.id !== personId ? p : {
      ...p,
      assigned_item_indices: p.assigned_item_indices.includes(index)
        ? p.assigned_item_indices.filter(x=>x!==index)
        : [...p.assigned_item_indices, index]
    }));
  }

  async function calculate() {
    setError("");
    if (!people.length) return setError("Add at least one person.");
    const unassigned = bill.items.filter((_,i)=>!people.some(p=>p.assigned_item_indices.includes(i)));
    if (unassigned.length) return setError(`Assign: ${unassigned.map(x=>x.name).join(", ")}`);

    try {
      const response = await fetch("/api/v1/calculate", {
        method:"POST", headers:{"Content-Type":"application/json"},
        body:JSON.stringify({bill,people})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Calculation failed.");
      onCalculated(data);
    } catch(e) { setError(e.message); }
  }

  return (
    <div className="card">
      <h2>2. Who ate what?</h2>
      <p className="muted">Select one or more people for each item. Shared items are divided between only those people.</p>

      <div className="row">
        <input placeholder="Person name" value={name} onChange={e=>setName(e.target.value)} onKeyDown={e=>e.key==="Enter"&&addPerson()}/>
        <button className="btn secondary" onClick={addPerson}>+ Add person</button>
      </div>

      {error && <div className="alert" style={{marginTop:15}}>{error}</div>}

      <div className="grid" style={{marginTop:18}}>
        {people.map(p=>(
          <div className="person" key={p.id}>
            <h3>{p.name}</h3>
            {bill.items.map((item,i)=>(
              <label className="check" key={i}>
                <input type="checkbox" checked={p.assigned_item_indices.includes(i)} onChange={()=>toggle(p.id,i)}/>
                <span>{item.name} — ₹{Number(item.total_price).toFixed(2)}</span>
              </label>
            ))}
          </div>
        ))}
      </div>

      <div className="actions">
        <button className="btn secondary" onClick={onBack}>Back</button>
        <button className="btn primary" onClick={calculate}>Calculate split →</button>
      </div>
    </div>
  );
}

import React from "react";

export default function ReviewScreen({ bill, setBill, onConfirm, onBack }) {
  function updateItem(index, key, value) {
    const items = [...bill.items];
    items[index] = {...items[index], [key]: key === "name" ? value : Number(value)};
    if (key === "quantity" || key === "unit_price") {
      items[index].total_price = Number((items[index].quantity * items[index].unit_price).toFixed(2));
    }
    setBill({...bill, items});
  }

  function update(key, value) {
    setBill({...bill, [key]: key === "restaurant_name" ? value : Number(value)});
  }

  async function confirm() {
    try {
      const response = await fetch(`/api/v1/bill/${bill.id}/confirm`, {
        method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({...bill,is_confirmed:true})
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not confirm bill.");
      onConfirm(data);
    } catch (e) {
      alert(e.message);
    }
  }

  return (
    <div className="card">
      <h2>1. Review extracted bill</h2>
      <p className="muted">Correct anything OCR missed. Calculation is locked until you confirm.</p>

      <div className="grid">
        <label>Restaurant<input value={bill.restaurant_name || ""} onChange={e=>update("restaurant_name",e.target.value)}/></label>
        <label>Subtotal<input type="number" step="0.01" value={bill.subtotal} onChange={e=>update("subtotal",e.target.value)}/></label>
        <label>Discount<input type="number" step="0.01" value={bill.discount} onChange={e=>update("discount",e.target.value)}/></label>
        <label>Service charge<input type="number" step="0.01" value={bill.service_charge} onChange={e=>update("service_charge",e.target.value)}/></label>
        <label>CGST<input type="number" step="0.01" value={bill.cgst} onChange={e=>update("cgst",e.target.value)}/></label>
        <label>SGST<input type="number" step="0.01" value={bill.sgst} onChange={e=>update("sgst",e.target.value)}/></label>
        <label>Other tax<input type="number" step="0.01" value={bill.other_tax} onChange={e=>update("other_tax",e.target.value)}/></label>
        <label>Printed total<input type="number" step="0.01" value={bill.printed_total} onChange={e=>update("printed_total",e.target.value)}/></label>
      </div>

      <h3>Line items</h3>
      <div style={{overflowX:"auto"}}>
        <table className="table">
          <thead><tr><th>Item</th><th>Qty</th><th>Unit price</th><th>Total</th><th>Confidence</th></tr></thead>
          <tbody>
            {bill.items.map((item,i)=>(
              <tr key={i}>
                <td><input value={item.name} onChange={e=>updateItem(i,"name",e.target.value)}/></td>
                <td><input type="number" step="0.01" value={item.quantity} onChange={e=>updateItem(i,"quantity",e.target.value)}/></td>
                <td><input type="number" step="0.01" value={item.unit_price} onChange={e=>updateItem(i,"unit_price",e.target.value)}/></td>
                <td>₹{Number(item.total_price).toFixed(2)}</td>
                <td className={item.needs_review ? "warn" : "ok"}>{Math.round(item.confidence*100)}% {item.needs_review ? "• review" : ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="actions">
        <button className="btn secondary" onClick={onBack}>Back</button>
        <button className="btn primary" onClick={confirm}>Confirm bill → Assign people</button>
      </div>
    </div>
  );
}

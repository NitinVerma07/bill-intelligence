import React from "react";

export default function ResultsScreen({ bill, result, onRestart }) {
  return (
    <div>
      <div className="card">
        <h2>3. Final split</h2>
        <div className={result.reconciliation_matched ? "ok" : "warn"}>
          {result.reconciliation_message}
        </div>
        <div className="grid" style={{marginTop:18}}>
          <div><div className="muted">Food base</div><div className="big">₹{result.verified_food_base.toFixed(2)}</div></div>
          <div><div className="muted">Tax</div><div className="big">₹{result.verified_tax_total.toFixed(2)}</div></div>
          <div><div className="muted">Service</div><div className="big">₹{result.verified_service_charge.toFixed(2)}</div></div>
          <div><div className="muted">Grand total</div><div className="big">₹{result.calculated_grand_total.toFixed(2)}</div></div>
        </div>
      </div>

      <div className="grid" style={{marginTop:16}}>
        {result.person_splits.map(p=>(
          <div className="card" key={p.person_id}>
            <h2>{p.person_name}</h2>
            <div className="big">₹{p.final_total.toFixed(2)}</div>
            <p className="muted">Food ₹{p.food_subtotal.toFixed(2)} • Discount -₹{p.discount_allocated.toFixed(2)}</p>
            <p className="muted">Tax ₹{(p.cgst_allocated+p.sgst_allocated+p.other_tax_allocated).toFixed(2)} • Service ₹{p.service_charge_allocated.toFixed(2)}</p>
            <h4>Items</h4>
            {p.item_breakdown.map((x,i)=><div key={i}>{x.item_name}: ₹{x.share_price.toFixed(2)}</div>)}
          </div>
        ))}
      </div>

      <div className="card" style={{marginTop:16}}>
        <button className="btn primary" onClick={onRestart}>Split another bill</button>
      </div>
    </div>
  );
}

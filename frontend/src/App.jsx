import React, { useState } from "react";
import UploadScreen from "./components/UploadScreen";
import ReviewScreen from "./components/ReviewScreen";
import AssignmentScreen from "./components/AssignmentScreen";
import ResultsScreen from "./components/ResultsScreen";

export default function App() {
  const [step, setStep] = useState("upload");
  const [bill, setBill] = useState(null);
  const [people, setPeople] = useState([]);
  const [result, setResult] = useState(null);

  return (
    <div className="app">
      <div className="container">
        <div className="header">
          <div className="logo">🧾 Bill Intelligence</div>
          <div className="badge">LOCAL OCR • NO API KEY</div>
        </div>

        {step === "upload" && (
          <UploadScreen
            onBillUploaded={(data) => { setBill(data); setStep("review"); }}
          />
        )}
        {step === "review" && (
          <ReviewScreen
            bill={bill}
            setBill={setBill}
            onConfirm={(confirmed) => { setBill(confirmed); setStep("assignment"); }}
            onBack={() => setStep("upload")}
          />
        )}
        {step === "assignment" && (
          <AssignmentScreen
            bill={bill}
            people={people}
            setPeople={setPeople}
            onBack={() => setStep("review")}
            onCalculated={(data) => { setResult(data); setStep("results"); }}
          />
        )}
        {step === "results" && (
          <ResultsScreen
            bill={bill}
            result={result}
            onRestart={() => { setBill(null); setPeople([]); setResult(null); setStep("upload"); }}
          />
        )}
      </div>
    </div>
  );
}

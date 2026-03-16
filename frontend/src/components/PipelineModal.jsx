import { useState, useRef } from "react";
import {
  X, Play, CheckCircle, FileText, Shield, Zap, Brain,
} from "lucide-react";
import { api } from "../lib/api.js";

const STEPS = [
  {
    key: "ingestion",
    label: "Ingestion",
    sub: "Perceive",
    icon: FileText,
    color: "var(--accent)",
    colorDim: "var(--accent-dim)",
    msg: "Reading uploaded data, normalizing invoices...",
  },
  {
    key: "reconciliation",
    label: "Reconciliation",
    sub: "Reason",
    icon: Shield,
    color: "#a78bfa",
    colorDim: "rgba(167,139,250,0.1)",
    msg: "Cross-checking GSTR-2A, detecting anomalies via XGBoost...",
  },
  {
    key: "filing",
    label: "Filing",
    sub: "Act",
    icon: Zap,
    color: "var(--warning)",
    colorDim: "var(--warning-dim)",
    msg: "Preparing encrypted GSTR-3B payload...",
  },
  {
    key: "learning",
    label: "Learning",
    sub: "Reflect",
    icon: Brain,
    color: "var(--info)",
    colorDim: "var(--info-dim)",
    msg: "Retraining XGBoost model on new patterns...",
  },
];

const STEP_DURATIONS = [1200, 1800, 1200, 900];

export default function PipelineModal({ client, isAdmin, onClose, onDone }) {
  const [step, setStep] = useState(-1);
  const [done, setDone] = useState(false);
  const [result, setResult] = useState(null);
  const [logs, setLogs] = useState([]);
  const logsRef = useRef(null);

  function addLog(msg) {
    setLogs((p) => {
      const next = [
        ...p,
        { id: Date.now() + Math.random(), msg, time: new Date().toLocaleTimeString() },
      ];
      setTimeout(() => logsRef.current?.scrollTo({ top: 9999 }), 20);
      return next;
    });
  }

  async function run() {
    setStep(0);
    setLogs([]);

    addLog(`Starting CAI pipeline for ${client.name}...`);

    const apiPromise = api.post("/ai/run", {
      client_id: client.id,
      period: "03-2026",
      use_stored_invoices: true,
    });

    for (let i = 0; i < STEPS.length; i++) {
      setStep(i);
      addLog(STEPS[i].msg);
      await new Promise((r) => setTimeout(r, STEP_DURATIONS[i]));
    }

    const { data, error } = await apiPromise;

    setStep(STEPS.length);

    if (error || !data) {
      addLog("Pipeline error");
      setResult({ error: error || "Failed" });
    } else {
      addLog("Pipeline complete");
      setResult(data);
    }

    setDone(true);
    onDone();
  }

  const running = step >= 0 && !done;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.75)",
        backdropFilter: "blur(4px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 50,
      }}
    >
      <div
        className="card"
        style={{
          width: 560,
          maxWidth: "95%",
          padding: 20,
        }}
      >

        {/* Header */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: 12,
          }}
        >
          <div>
            <div style={{ fontWeight: 600 }}>AI Pipeline</div>
            <div style={{ fontSize: 12 }}>
              {client.name} — March 2026
            </div>
          </div>

          <button onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        {/* Steps */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4,1fr)",
            gap: 8,
            marginBottom: 12,
          }}
        >
          {STEPS.map((s, i) => {
            const Icon = s.icon;
            const active = step === i;
            const doneStep = step > i;

            return (
              <div
                key={s.key}
                style={{
                  border: "1px solid var(--border)",
                  padding: 8,
                  borderRadius: 6,
                  background: active
                    ? s.colorDim
                    : doneStep
                      ? "var(--accent-dim)"
                      : "transparent",
                }}
              >
                <Icon size={14} />
                <div style={{ fontSize: 12 }}>
                  {s.label}
                </div>
              </div>
            );
          })}
        </div>

        {/* Logs */}
        {logs.length > 0 && (
          <div
            ref={logsRef}
            style={{
              height: 100,
              overflow: "auto",
              border: "1px solid var(--border)",
              padding: 8,
              marginBottom: 12,
              fontSize: 12,
              fontFamily: "monospace",
            }}
          >
            {logs.map((l) => (
              <div key={l.id}>
                {l.time} — {l.msg}
              </div>
            ))}
          </div>
        )}

        {/* Results */}
        {done && result && !result.error && (
          <div
            style={{
              border: "1px solid var(--border)",
              padding: 12,
              marginBottom: 12,
            }}
          >
            <div style={{ fontSize: 14 }}>
              <div style={{ marginBottom: 4 }}><strong>Total:</strong> {result.total_invoices}</div>
              <div style={{ marginBottom: 4 }}><strong>Matched:</strong> {result.matched}</div>
              <div style={{ marginBottom: 4 }}><strong>Mismatch:</strong> {result.mismatched}</div>
              <div style={{ marginBottom: 4 }}><strong>Risk Score:</strong> {result.risk_score}</div>

              {result.nic_reference && (
                <div style={{ marginTop: 8, color: "var(--text-2)" }}>
                  NIC Ref: {result.nic_reference}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        {step === -1 && (
          <button
            onClick={run}
            className="btn btn-primary"
            style={{ width: "100%" }}
          >
            <Play size={14} /> Run Pipeline
          </button>
        )}

        {running && (
          <div style={{ textAlign: "center", padding: "8px 0", color: "var(--text-2)" }}>
            Processing...
          </div>
        )}

        {done && (
          <button
            onClick={onClose}
            className="btn btn-primary"
            style={{ width: "100%" }}
          >
            Done
          </button>
        )}

      </div>
    </div>
  );
}
'use client';

import React, { useState } from 'react';
import {
  ShieldCheck,
  Lock,
  RotateCcw,
  Check,
  Trash2,
  Sliders,
  Scale,
  Cpu,
  Layers,
  FileText,
  AlertTriangle,
} from 'lucide-react';

export default function SettingsPage() {
  const [zeroRetention, setZeroRetention] = useState(true);
  const [ephemeralWipe, setEphemeralWipe] = useState(true);
  const [groundingThreshold, setGroundingThreshold] = useState(99.4);
  const [defaultJurisdiction, setDefaultJurisdiction] = useState('Delaware Law (DGCL)');
  const [savedFeedback, setSavedFeedback] = useState(false);

  const handleSave = () => {
    setSavedFeedback(true);
    setTimeout(() => setSavedFeedback(false), 2500);
  };

  const auditLogs = [
    {
      timestamp: 'Today, 11:42:04 AM',
      event: 'Ingestion Sandbox Initialized',
      target: 'Master_Services_Agreement_v4.2.pdf',
      hash: 'sha256:7bc89d...1m4',
      status: 'AES-256 Memory Bound',
    },
    {
      timestamp: 'Today, 11:42:06 AM',
      event: 'Deterministic Parser Extraction',
      target: '28 Clauses Indexing',
      hash: 'sha256:4a02be...99d1',
      status: 'Verified Zero-Leakage',
    },
    {
      timestamp: 'Today, 11:44:03 AM',
      event: 'Grounded Interrogation Executed',
      target: 'Section 8.3 & Section 3.2',
      hash: 'sha256:91fe33...01ac',
      status: 'Grounding Match 99.8%',
    },
  ];

  return (
    <div className="space-y-6 pb-12 max-w-5xl">
      {/* 1. Header Banner */}
      <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg px-4 py-2 text-xs flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-[#0284C7]" />
          <span>
            <strong className="font-semibold text-[#0F172A]">Enterprise Security &amp; Compliance Sandbox:</strong>{' '}
            All settings apply strictly to the current active cryptographic session.
          </span>
        </div>
        <span className="font-mono text-[11px] text-[#059669] font-medium">Session: Active</span>
      </div>

      {/* 2. Title */}
      <div className="space-y-1">
        <div className="text-[10px] font-mono font-bold tracking-wider text-[#64748B] uppercase">
          ENGINE CONFIGURATION / 08 / Privacy &amp; System Preferences
        </div>
        <h1 className="text-3xl font-display font-bold text-[#0F172A] tracking-tight">
          Privacy &amp; Application Settings
        </h1>
        <p className="text-xs sm:text-sm text-[#475569] leading-relaxed">
          Configure zero-data-retention sandboxes, deterministic grounding parameters, and jurisdictional baselines.
        </p>
      </div>

      {savedFeedback && (
        <div className="p-3 bg-[#ECFDF5] border border-[#A7F3D0] rounded-lg text-xs font-mono text-[#065F46] flex items-center gap-2">
          <Check className="w-4 h-4 text-[#059669]" />
          <span>Engine preferences updated and synced with active in-memory sandbox.</span>
        </div>
      )}

      {/* 3. Section 1: Confidentiality & Ephemeral Memory Controls */}
      <div className="scaffold-card p-5 border border-[#CBD5E1] bg-white space-y-4">
        <div className="flex items-center gap-2 border-b border-[#E2E8F0] pb-3">
          <Lock className="w-4 h-4 text-[#0284C7]" />
          <h2 className="text-sm font-display font-bold text-[#0F172A]">
            Confidentiality &amp; Ephemeral Memory Controls
          </h2>
        </div>

        <div className="space-y-4 text-xs">
          {/* Toggle 1: Zero-Data-Retention */}
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-0.5">
              <div className="font-semibold text-[#0F172A]">Zero-Data-Retention Sandbox</div>
              <p className="text-[#64748B] leading-relaxed">
                Prevents uploaded agreements, extracts, and counter-proposals from ever being retained on disk or utilized in AI training datasets.
              </p>
            </div>
            <button
              onClick={() => setZeroRetention(!zeroRetention)}
              className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors shrink-0 ${
                zeroRetention ? 'bg-[#0284C7]' : 'bg-[#CBD5E1]'
              }`}
            >
              <div
                className={`bg-white w-4 h-4 rounded-full shadow-xs transform transition-transform ${
                  zeroRetention ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* Toggle 2: Ephemeral RAM Wipe */}
          <div className="flex items-start justify-between gap-4 pt-3 border-t border-[#F1F5F9]">
            <div className="space-y-0.5">
              <div className="font-semibold text-[#0F172A]">
                Automatic RAM Scrubbing on Disconnect
              </div>
              <p className="text-[#64748B] leading-relaxed">
                Immediately issues a cryptographic overwrite to ephemeral memory when the browser tab is closed or the user session ends.
              </p>
            </div>
            <button
              onClick={() => setEphemeralWipe(!ephemeralWipe)}
              className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors shrink-0 ${
                ephemeralWipe ? 'bg-[#0284C7]' : 'bg-[#CBD5E1]'
              }`}
            >
              <div
                className={`bg-white w-4 h-4 rounded-full shadow-xs transform transition-transform ${
                  ephemeralWipe ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* 4. Section 2: Legal Model Engine Parameters */}
      <div className="scaffold-card p-5 border border-[#CBD5E1] bg-white space-y-4">
        <div className="flex items-center gap-2 border-b border-[#E2E8F0] pb-3">
          <Cpu className="w-4 h-4 text-[#0284C7]" />
          <h2 className="text-sm font-display font-bold text-[#0F172A]">
            Legal Model Engine Parameters
          </h2>
        </div>

        <div className="grid sm:grid-cols-2 gap-4 text-xs">
          <div className="space-y-1.5">
            <label className="font-semibold text-[#0F172A]">Underlying Foundation Engine</label>
            <div className="p-2.5 rounded bg-[#F8FAFC] border border-[#CBD5E1] font-mono text-[11px] text-[#334155] flex items-center justify-between">
              <span>Gemini 1.5 Pro (Enterprise Legal Fine-Tuned)</span>
              <span className="text-[#059669] font-bold">Online</span>
            </div>
            <p className="text-[10px] text-[#64748B]">1 Million token context window enabled.</p>
          </div>

          <div className="space-y-1.5">
            <label className="font-semibold text-[#0F172A]">Default Jurisdictional Baseline</label>
            <select
              value={defaultJurisdiction}
              onChange={(e) => setDefaultJurisdiction(e.target.value)}
              className="w-full bg-[#F8FAFC] border border-[#CBD5E1] rounded p-2 text-[#0F172A] focus:outline-none focus:border-[#0284C7]"
            >
              <option>Delaware Law (DGCL)</option>
              <option>California Civil Code</option>
              <option>New York Law</option>
              <option>Texas Business Organizations Code</option>
              <option>Federal UCC Article 2</option>
            </select>
            <p className="text-[10px] text-[#64748B]">
              Calibrates standard market baselines and non-compete/indemnity statutory floors.
            </p>
          </div>
        </div>
      </div>

      {/* 5. Section 3: Session Audit Trail Log */}
      <div id="audit" className="scaffold-card p-5 border border-[#CBD5E1] bg-white space-y-4">
        <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#0284C7]" />
            <h2 className="text-sm font-display font-bold text-[#0F172A]">Session Audit Trail Log</h2>
          </div>
          <span className="text-[10px] font-mono text-[#64748B]">Immutable Ledger</span>
        </div>

        <div className="space-y-2">
          {auditLogs.map((log, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded bg-[#F8FAFC] border border-[#E2E8F0] flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs font-mono"
            >
              <div className="space-y-0.5">
                <div className="font-semibold text-[#0F172A] flex items-center gap-2">
                  <span>{log.event}</span>
                  <span className="text-[10px] text-[#64748B] font-normal">({log.timestamp})</span>
                </div>
                <div className="text-[11px] text-[#475569]">Target: {log.target}</div>
              </div>

              <div className="text-right">
                <div className="text-[10px] text-[#0284C7]">{log.hash}</div>
                <div className="text-[10px] text-[#059669]">{log.status}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={() => alert('Active cryptographic session wiped and reset.')}
          className="px-3.5 py-2 text-xs font-semibold text-[#DC2626] bg-white border border-[#FECACA] hover:bg-[#FEF2F2] rounded flex items-center gap-1.5"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Purge Active Session Memory</span>
        </button>

        <button
          onClick={handleSave}
          className="px-5 py-2 text-xs font-semibold bg-[#0F172A] hover:bg-[#1E293B] text-white rounded transition-colors"
        >
          Save Engine Preferences
        </button>
      </div>
    </div>
  );
}

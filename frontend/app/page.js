"use client";

import React, { useState, useEffect } from "react";
import { useFeynmanStream } from "../hooks/useFeynmanStream";

export default function FeynmanLaboratoryDashboard() {
  const sessionId = "feynman_shared_lab_01";
  const { messages, isStreaming, askFeynman } = useFeynmanStream("http://127.0.0.1:8000");
  const [inputQuery, setInputQuery] = useState("");
  const [dashboardMemories, setDashboardMemories] = useState([]);
  const [isResetting, setIsResetting] = useState(false);

  // Pull latest memory records to sync our visualization matrix
  const refreshMemoryDashboard = async () => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/memory/dashboard`);
      const data = await res.json();
      if (data?.status === "success") {
        setDashboardMemories(data.memories);
      }
    } catch (err) {
      console.error("Failed to sync up memory dashboard view:", err);
    }
  };

  // Triggers a complete system-wide purge across Neon database engines and current dashboard instances
  const handleResetBrainStorage = async () => {
    const isConfirmed = window.confirm(
      "☢️ WARNING: Are you absolutely sure? This will permanently delete all short-term chat logs, conversation messages, and synthesized long-term memory streams from your Neon database storage and reset your tracking state indices."
    );

    if (!isConfirmed) return;

    setIsResetting(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/api/memory/reset", {
        method: "DELETE",
      });

      if (response.ok) {
        // Clear UI states immediately
        setDashboardMemories([]);
        // Force fully reload or empty internal streaming arrays if necessary
        alert("💥 Memory core completely wiped. All short-term and long-term profiles purged.");
      } else {
        const errData = await response.json().catch(() => ({}));
        alert(`Failed to complete purge operation: ${errData?.detail || response.statusText}`);
      }
    } catch (err) {
      console.error("Network configuration failure running database purge query:", err);
      alert("Network error: Verification failed while contacting the API gateway reset route.");
    } finally {
      setIsResetting(false);
    }
  };

  // Sync visualization items on initialization
  useEffect(() => {
    refreshMemoryDashboard();
  }, []);

  // When streaming finishes, refresh long-term storage automatically to catch new insights
  useEffect(() => {
    if (!isStreaming && messages.length > 0) {
      const delayTimer = setTimeout(() => {
        refreshMemoryDashboard();
      }, 1200); // 1.2s buffer to let the background worker finish processing
      return () => clearTimeout(delayTimer);
    }
  }, [isStreaming, messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputQuery.trim() || isStreaming) return;
    askFeynman(sessionId, inputQuery);
    setInputQuery("");
  };

  // Maps distinct memory categories to responsive visual border/background tones
  const getCategoryColor = (cat) => {
    switch (cat) {
      case "User Profile": return "border-emerald-500 bg-emerald-950/40 text-emerald-300";
      case "Physics Concept": return "border-cyan-500 bg-cyan-950/40 text-cyan-300";
      case "Timeline Anchor": return "border-amber-500 bg-amber-950/40 text-amber-300";
      default: return "border-slate-500 bg-slate-900 text-slate-300";
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* LEFT COMPONENT: Interactive Quantum Chat Interface (7 Columns) */}
      <section className="lg:col-span-7 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden h-[calc(100vh-3rem)]">
        <header className="p-4 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-cyan-400">Richard Feynman Digital Twin</h1>
            <p className="text-xs text-slate-400">RAG Context Amplified • Unified Short-Term Memory Streams</p>
          </div>
          {isStreaming && (
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
            </span>
          )}
        </header>

        {/* Dynamic Message Feed Window */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-900/50">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-2 text-center p-8">
              <p className="text-lg italic">"The first principle is that you must not fool yourself..."</p>
              <p className="text-sm max-w-sm">Ask Richard about quantum frameworks, physics history, or his 1965 insights.</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`max-w-[85%] rounded-lg p-4 leading-relaxed shadow-md border ${
                  msg.role === "user"
                    ? "ml-auto bg-cyan-600/10 border-cyan-500/30 text-cyan-100"
                    : "mr-auto bg-slate-950 border-slate-800 text-slate-200"
                }`}
              >
                <div className="text-xs font-semibold mb-1 opacity-60 uppercase tracking-wider">
                  {msg.role === "user" ? "You" : "Feynman"}
                </div>
                <p className="whitespace-pre-wrap text-sm md:text-base">{msg.content || "..."}</p>
              </div>
            ))
          )}
        </div>

        {/* Input Interface Entry Form */}
        <form onSubmit={handleSubmit} className="p-4 bg-slate-950 border-t border-slate-800 flex gap-3">
          <input
            type="text"
            className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-cyan-500 text-slate-100 placeholder-slate-500"
            placeholder="Introduce yourself or ask a conceptual challenge..."
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            disabled={isStreaming}
          />
          <button
            type="submit"
            disabled={isStreaming || !inputQuery.trim()}
            className="bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 disabled:text-slate-600 text-slate-950 font-bold px-6 py-3 rounded-lg text-sm transition-colors duration-200"
          >
            {isStreaming ? "Streaming..." : "Transmit"}
          </button>
        </form>
      </section>

      {/* RIGHT COMPONENT: Memory Visualization Dashboard Panel (5 Columns) */}
      <section className="lg:col-span-5 flex flex-col bg-slate-900 border border-slate-800 rounded-xl overflow-hidden h-[calc(100vh-3rem)]">
        <header className="p-4 bg-slate-950 border-b border-slate-800 flex justify-between items-center">
          <div>
            <h2 className="text-md font-bold text-emerald-400 tracking-wide uppercase">Memory Visualization Dashboard</h2>
            <p className="text-xs text-slate-400">Synthesized Long-Term Insights inside Cloud Neon</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleResetBrainStorage}
              disabled={isResetting}
              className="text-xs bg-red-950/60 hover:bg-red-900 border border-red-800 text-red-400 px-3 py-1.5 rounded-md font-medium transition-colors disabled:opacity-50"
            >
              {isResetting ? "Wiping..." : "Reset Memory"}
            </button>
            <button
              onClick={refreshMemoryDashboard}
              className="text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 px-3 py-1.5 rounded-md text-slate-300 font-medium transition-colors"
            >
              Sync Matrix
            </button>
          </div>
        </header>

        {/* Live Visual Memory Matrix Layout Container */}
        <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-950/30">
          {dashboardMemories.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-600 text-center p-6 text-sm">
              <p>No high-level consolidated facts stored in Neon database yet.</p>
              <p className="text-xs text-slate-500 mt-1">Converse with Feynman first. The background loop will extract facts here automatically!</p>
            </div>
          ) : (
            dashboardMemories.map((mem) => (
              <div
                key={mem.id}
                className={`border p-3.5 rounded-lg shadow-sm transition-all duration-300 hover:scale-[1.01] ${getCategoryColor(
                  mem.category
                )}`}
              >
                <div className="flex justify-between items-center mb-1.5">
                  <span className="text-xs font-bold uppercase tracking-widest px-2 py-0.5 rounded-md bg-slate-950/60 border border-white/5">
                    {mem.category}
                  </span>
                  <span className="text-xs opacity-75 font-mono">
                    Importance: <span className="font-bold text-white">{mem.importance_score}/5</span>
                  </span>
                </div>
                <p className="text-sm font-medium text-slate-100">{mem.fact_summary}</p>
                <div className="text-[10px] opacity-40 text-right mt-2 font-mono">
                  Log Sync: {new Date(mem.created_at).toLocaleTimeString()}
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  );
}
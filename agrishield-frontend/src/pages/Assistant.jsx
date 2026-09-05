import React, { useEffect, useRef, useState } from "react";
import { Send, Bot, User, Loader2, Sparkles, Sprout, Bug, Wind } from "lucide-react";
import * as assistantService from "../services/assistantService";

const WELCOME = {
  role: "assistant",
  content:
    "Hello! I am the AgriShield AI Agronomic Assistant. I can assist you with integrated pest management (IPM), chemical dosage calibrations, crop nutrition strategies, or real-time spray timing guidance.",
};

const SUGGESTIONS = [
  "How do I control Brown Planthopper in rice without resurgence?",
  "What is the recommended fertilizer schedule for Cotton at flowering?",
  "What biological controls work best for American Bollworm?",
  "When is it unsafe to perform pesticide foliar sprays?",
];

export default function Assistant() {
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (textToSend) => {
    const text = (textToSend || input).trim();
    if (!text || sending) return;

    const nextMessages = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setSending(true);

    try {
      const history = nextMessages.map((m) => ({ role: m.role, content: m.content }));
      const { reply } = await assistantService.sendMessage(text, history);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I'm temporarily unable to reach the agronomic AI model. For pest emergencies, please consult your regional Krishi Vigyan Kendra (KVK).",
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col md:h-[calc(100vh-6rem)] max-w-5xl mx-auto space-y-4">
      <div>
        <h1 className="font-display text-2xl md:text-3xl font-bold text-slate-100 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-emerald-400" />
          Agronomic AI Assistant
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Intelligent conversational advisor for crop protection, fertilizer planning, and pest diagnosis.
        </p>
      </div>

      <div className="bg-slate-900/80 rounded-2xl border border-slate-800 flex flex-1 flex-col overflow-hidden shadow-2xl">
        {/* Messages List */}
        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          {messages.map((m, i) => (
            <div key={i} className={`flex gap-3 ${m.role === "user" ? "flex-row-reverse" : ""}`}>
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl text-xs font-bold ${
                  m.role === "user"
                    ? "bg-emerald-500 text-slate-950"
                    : "bg-slate-800 text-emerald-400 border border-slate-700"
                }`}
              >
                {m.role === "user" ? <User size={15} /> : <Bot size={15} />}
              </div>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-xs md:text-sm leading-relaxed ${
                  m.role === "user"
                    ? "bg-emerald-500 text-slate-950 font-medium"
                    : "bg-slate-950/80 border border-slate-800/80 text-slate-200"
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex items-center gap-2 text-xs text-emerald-400 py-2">
              <Loader2 size={14} className="animate-spin" /> Analyzing agronomic research intelligence…
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Quick Suggestion Pills */}
        {messages.length <= 2 && (
          <div className="px-4 py-2 border-t border-slate-800/60 bg-slate-950/40 flex flex-wrap gap-1.5">
            {SUGGESTIONS.map((s, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(s)}
                className="text-[11px] px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 transition"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 border-t border-slate-800 p-4 bg-slate-950/60"
        >
          <input
            className="flex-1 px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
            placeholder="Ask about pests, fertilizer schedules, or spray weather conditions…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            disabled={sending || !input.trim()}
            className="py-2.5 px-4 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm shadow-md shadow-emerald-500/20 transition-all flex items-center justify-center disabled:opacity-40"
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}

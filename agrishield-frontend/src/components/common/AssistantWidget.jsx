import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Bot, Send, Sparkles, X } from "lucide-react";
import toast from "react-hot-toast";
import assistantService from "../../services/assistantService";

const EXAMPLE_QUESTIONS = [
  "What pest is affecting cotton?",
  "How can I reduce pest attack?",
  "What pesticide should I use?",
];

export default function AssistantWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi, I'm the AgriShield assistant. Ask me about pest risk, prevention, or how to read a prediction.",
    },
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, typing]);

  async function sendMessage(text) {
    const question = text ?? input;
    if (!question.trim()) return;

    const nextMessages = [...messages, { role: "user", content: question }];
    setMessages(nextMessages);
    setInput("");
    setTyping(true);

    try {
      const { reply } = await assistantService.sendMessage(question, nextMessages);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err) {
      toast.error(err.message || "The assistant is unavailable right now.");
    } finally {
      setTyping(false);
    }
  }

  return (
    <>
      <motion.button
        onClick={() => setOpen((v) => !v)}
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.94 }}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-primary-600 text-white shadow-lg shadow-primary-600/30"
        aria-label="Open AI assistant"
      >
        {open ? <X size={22} /> : <Bot size={22} />}
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="glass-card fixed bottom-24 right-6 z-50 flex h-[28rem] w-[22rem] flex-col overflow-hidden"
          >
            <div className="flex items-center gap-2 border-b border-surface-border bg-primary-600 px-4 py-3 text-white dark:border-surface-darkBorder">
              <Sparkles size={16} />
              <p className="text-sm font-semibold">AgriShield Assistant</p>
            </div>

            <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${
                    msg.role === "user"
                      ? "ml-auto bg-primary-600 text-white"
                      : "bg-slate-100 text-slate-700 dark:bg-white/5 dark:text-slate-200"
                  }`}
                >
                  {msg.content}
                </div>
              ))}
              {typing && (
                <div className="flex w-fit gap-1 rounded-2xl bg-slate-100 px-3 py-2 dark:bg-white/5">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    />
                  ))}
                </div>
              )}

              {messages.length === 1 && (
                <div className="space-y-2 pt-2">
                  {EXAMPLE_QUESTIONS.map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="block w-full rounded-xl border border-surface-border px-3 py-2 text-left text-xs text-slate-500 hover:border-primary-400 hover:text-primary-700 dark:border-surface-darkBorder dark:text-slate-400"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
              className="flex items-center gap-2 border-t border-surface-border p-3 dark:border-surface-darkBorder"
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about pests, weather, prevention..."
                className="input-field !py-2 text-sm"
              />
              <button type="submit" className="btn-primary !px-3 !py-2" aria-label="Send">
                <Send size={16} />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

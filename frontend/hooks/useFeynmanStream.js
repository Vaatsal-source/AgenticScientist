import { useState } from "react";

export function useFeynmanStream(baseUrl) {
  // Safe fallback hierarchy check
  const activeUrl = baseUrl || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const askFeynman = async (sessionId, query) => {
    if (!query.trim()) return;

    // 1. Immediately append user's query locally to update chat feed
    const userMsg = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);

    // 2. Initialize an empty model response message slot
    let currentResponse = "";
    setMessages((prev) => [...prev, { role: "model", content: "" }]);

    try {
      // Fetch request pointing to the verified dynamic activeUrl location
      const response = await fetch(`${activeUrl}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, query: query }),
      });

      if (!response.body) throw new Error("No response body available from backend.");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const token = line.replace("data: ", "").trim();
            if (token && !token.includes("[ERROR]")) {
              currentResponse += token + " "; // Keep spacing clean
              
              setMessages((prev) => {
                const updated = [...prev];
                if (updated.length > 0) {
                  updated[updated.length - 1] = { role: "model", content: currentResponse };
                }
                return updated;
              });
            }
          }
        }
      }
    } catch (err) {
      console.error("SSE stream collection failure:", err);
    } finally {
      setIsStreaming(false);
    }
  };

  return { messages, setMessages, isStreaming, askFeynman };
}
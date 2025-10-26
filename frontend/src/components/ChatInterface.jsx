import React, { useEffect } from "react";
import { useWakeWord } from "../hooks/useWakeWord";

export default function ChatInterface() {
  const handleWakeWord = () => {
    console.log("✅ Wake word detected! Activating chat input...");
    // focus chat input, start listening, or open mic
  };

  useEffect(() => {
    console.log("🟢 ChatInterface mounted, initializing wake word...");
    const key = import.meta.env.VITE_PORCUPINE_KEY;
    console.log("Porcupine key:", key);

    if (key) {
      useWakeWord(key, handleWakeWord);
    } else {
      console.error("❌ Porcupine key not found!");
    }
  }, []);

  return (
    <div className="p-6 text-center">
      <h1 className="text-lg font-semibold mb-2">💬 Chat Interface</h1>
      <p>Say “Hey Zed” to activate!</p>
    </div>
  );
}

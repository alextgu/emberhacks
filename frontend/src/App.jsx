import React, { useState, useEffect } from "react";
import { useWakeWord } from "./hooks/useWakeWord"; // adjust path if needed

export default function App() {
  const [textQuery, setTextQuery] = useState("");

  // Callback when wake word is detected
  const handleWakeWord = () => {
    console.log("✅ Wake word detected! You can focus input or trigger voice commands.");
    // Example: focus the input field
    const input = document.querySelector("input");
    if (input) input.focus();
  };

  // Initialize Porcupine wake word - call hook at top level
  const key = import.meta.env.VITE_PORCUPINE_KEY;
  
  useEffect(() => {
    console.log("🟢 App mounted, initializing wake word...");
    if (!key) {
      console.error("❌ Porcupine key not found!");
    }
  }, [key]);

  // Call the hook at the top level (not inside useEffect)
  useWakeWord(key, handleWakeWord);

  return (
    <div className="h-screen w-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#0a0a0f] via-[#161630] to-[#2a0f55] text-white font-[Poppins] overflow-hidden">
      
      {/* ZED Title */}
      <h1 className="text-8xl font-bold tracking-[0.25em] mb-16 text-[#b3b8ff] drop-shadow-[0_0_25px_#7a5cff] animate-pulse">
        ZED
      </h1>

      {/* Input + Voice Button */}
      <div className="flex flex-col md:flex-row gap-6 w-full max-w-3xl justify-center px-8">
        <input
          type="text"
          value={textQuery}
          onChange={(e) => setTextQuery(e.target.value)}
          placeholder="Type your command..."
          className="flex-1 px-6 py-4 bg-[#1a1a1f] border border-[#5f5f80]/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-[#7a5cff] text-[#cfd2ff] placeholder-[#8a8ba3] backdrop-blur-md transition-all duration-300"
        />

        <button className="px-8 py-4 bg-[#1a1a1f] border border-[#5f5f80]/30 rounded-2xl text-[#cfd2ff] font-semibold hover:bg-[#29293d] hover:border-[#7a5cff]/60 transition-all duration-300">
          🎤
        </button>
      </div>
    </div>
  );
}

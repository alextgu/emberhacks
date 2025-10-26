import React, { useState, useCallback } from "react";
import { useWakeWord } from "./hooks/useWakeWord";

export default function App() {
  const [textQuery, setTextQuery] = useState("");
  const [detectionCount, setDetectionCount] = useState(0);
  const [lastDetection, setLastDetection] = useState(null);

  const handleWakeWord = useCallback(() => {
    console.log("✅✅✅ WAKE WORD DETECTED IN APP! ✅✅✅");
    const now = new Date().toLocaleTimeString();
    setLastDetection(now);
    setDetectionCount(prev => prev + 1);
    
    // Flash the screen
    document.body.style.backgroundColor = "#00ff00";
    setTimeout(() => {
      document.body.style.backgroundColor = "";
    }, 200);
    
    // Focus the input field
    const input = document.querySelector("input");
    if (input) {
      input.focus();
      console.log("📝 Input field focused!");
    }
  }, []);

  const key = import.meta.env.VITE_PORCUPINE_KEY;
  const micStatus = useWakeWord(key, handleWakeWord);

  return (
    <div className="h-screen w-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#0a0a0f] via-[#161630] to-[#2a0f55] text-white font-[Poppins] overflow-hidden">
      
      {/* Microphone Status Indicator */}
      <div className="absolute top-8 right-8 flex items-center gap-3 px-4 py-2 bg-[#1a1a1f]/80 backdrop-blur-md rounded-full border border-[#5f5f80]/30">
        <div className={`w-3 h-3 rounded-full ${micStatus === 'active' ? 'bg-green-500 animate-pulse' : micStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'}`}></div>
        <span className="text-sm text-[#cfd2ff]">
          {micStatus === 'active' ? '🎤 Listening for "Hey Zed"' : micStatus === 'error' ? '❌ Mic Error' : '⏳ Initializing...'}
        </span>
      </div>

      {/* Detection Counter */}
      {detectionCount > 0 && (
        <div className="absolute top-24 right-8 px-6 py-3 bg-green-500/90 backdrop-blur-md rounded-xl border-2 border-green-300 animate-bounce">
          <div className="text-white font-bold text-lg">🎉 Detected: {detectionCount}x</div>
          <div className="text-white/80 text-xs">Last: {lastDetection}</div>
        </div>
      )}

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

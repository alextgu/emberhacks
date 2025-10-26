import React, { useState, useCallback } from "react";
import { useWakeWord } from "./hooks/useWakeWord";
import "./index.css";

export default function App() {
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const [showInput, setShowInput] = useState(false);
  const [query, setQuery] = useState("");
  const [detectionCount, setDetectionCount] = useState(0);
  const [lastDetection, setLastDetection] = useState(null);

  const handleWakeWord = useCallback(() => {
    console.log("✅✅✅ WAKE WORD DETECTED IN APP! ✅✅✅");
    const now = new Date().toLocaleTimeString();
    setLastDetection(now);
    setDetectionCount((prev) => prev + 1);

    document.body.style.backgroundColor = "#00ff00";
    setTimeout(() => {
      document.body.style.backgroundColor = "";
    }, 200);

    const input = document.querySelector("input");
    if (input) {
      input.focus();
      console.log("📝 Input field focused!");
    }
  }, []);

  const key = import.meta.env.VITE_PORCUPINE_KEY;
  const micStatus = useWakeWord(key, handleWakeWord);

  const handleMouseMove = (e) => {
    const { innerWidth, innerHeight } = window;
    const x = ((e.clientY - innerHeight / 2) / innerHeight) * 4;
    const y = ((e.clientX - innerWidth / 2) / innerWidth) * 4;
    setRotation({ x, y });
  };

  const handleMouseLeave = () => setRotation({ x: 0, y: 0 });
  const handleButtonClick = () => setShowInput(!showInput);
  const handleInputSubmit = (e) => {
    e.preventDefault();
    console.log("User asked:", query);
    setQuery("");
  };

  return (
    <div
      className="relative h-screen w-screen flex items-center justify-center text-white font-[Inter] overflow-hidden"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div className="liquid-bg"></div>

      <div
        className="absolute top-8 right-8 flex items-center gap-3 px-5 py-2.5 rounded-2xl border border-white/20 backdrop-blur-xl z-20"
        style={{
          background:
            "linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05))",
          boxShadow:
            "0 8px 25px rgba(0,0,0,0.4), inset 0 0 25px rgba(255,255,255,0.08)",
        }}
      >
        <div
          className={`w-3.5 h-3.5 rounded-full ${
            micStatus === "active"
              ? "bg-green-500"
              : micStatus === "error"
              ? "bg-red-500"
              : "bg-yellow-500"
          }`}
        ></div>
        <span className="flex items-center gap-2 text-sm sm:text-base font-medium text-white/90">
          🎤{" "}
          {micStatus === "active"
            ? "Listening active"
            : micStatus === "error"
            ? "Mic Error"
            : "Initializing..."}
        </span>
      </div>

      {detectionCount > 0 && (
        <div className="absolute top-24 right-8 px-6 py-3 bg-green-500/90 backdrop-blur-md rounded-xl border-2 border-green-300 animate-bounce z-20">
          <div className="text-white font-bold text-lg">
            🎉 Detected: {detectionCount}x
          </div>
          <div className="text-white/80 text-xs">Last: {lastDetection}</div>
        </div>
      )}

      <div
        className="relative z-10 w-[90%] max-w-2xl p-14 rounded-3xl border border-white/20 backdrop-blur-2xl text-center space-y-10 transition-transform duration-300 ease-out"
        style={{
          transform: `perspective(1000px) rotateX(${rotation.x}deg) rotateY(${rotation.y}deg) scale(1.02)`,
          background:
            "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02))",
          boxShadow:
            "0 20px 60px rgba(0,0,0,0.5), inset 0 0 40px rgba(255,255,255,0.05)",
        }}
      >
        <div
          className="absolute inset-0 rounded-3xl pointer-events-none"
          style={{
            background: `radial-gradient(circle at ${50 + rotation.y * 3}% ${
              50 - rotation.x * 3
            }%, rgba(255,255,255,0.15), transparent 60%)`,
            mixBlendMode: "overlay",
          }}
        ></div>

        <h1 className="text-[6rem] sm:text-[7rem] font-extrabold tracking-[0.25em] text-white/95 drop-shadow-[0_0_10px_rgba(255,255,255,0.25)] -mt-6">
          ZED
        </h1>

        <p className="text-lg text-gray-200 leading-relaxed max-w-lg mx-auto">
          Meet your personal AI assistant — a sophisticated digital companion
          designed to streamline your workflow, deliver precise insights, and
          anticipate your needs with intuitive intelligence.
          <br />
          <span className="text-gray-200">
            Say <span className="text-[#ff6b6b] font-semibold">"Hey ZED"</span>{" "}
            to get your conversation started.
          </span>
        </p>

        <div className="mt-8">
          <button
            onClick={handleButtonClick}
            className="px-8 py-3 bg-white/10 border border-white/20 rounded-xl text-white font-medium hover:bg-white/20 transition-all backdrop-blur-md"
          >
            Click to Type
          </button>
        </div>

        <div
          className={`transition-all duration-700 ease-[cubic-bezier(0.25,1,0.3,1)] overflow-hidden ${
            showInput ? "max-h-32 opacity-100 mt-6" : "max-h-0 opacity-0"
          }`}
        >
          <form
            onSubmit={handleInputSubmit}
            className="flex items-center justify-center"
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask ZED anything..."
              className="w-3/4 sm:w-2/3 px-5 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 backdrop-blur-lg transition"
            />
          </form>
        </div>
      </div>
    </div>
  );
}

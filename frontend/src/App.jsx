import React, { useState, useEffect, useCallback } from "react";
import { AnimatePresence, motion } from "framer-motion";
import LoginScene from "./components/LoginScene";
import MainScene from "./components/MainScene";
import { useWakeWord } from "./hooks/useWakeWord";
import { useRecorder } from "./hooks/useRecorder";

export default function App() {
  const [phase, setPhase] = useState("intro");
  const [introText, setIntroText] = useState("");
  const [welcomeText, setWelcomeText] = useState("");
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const [showInput, setShowInput] = useState(false);
  const [query, setQuery] = useState("");

  const [micStatus, setMicStatus] = useState("initializing");
  const [detectionCount, setDetectionCount] = useState(0);
  const [lastDetection, setLastDetection] = useState("");

  const { recording, transcribedText, isTranscribing, startRecording, stopRecording } =
    useRecorder();

  const handleMouseMove = (e) => {
    const x = (window.innerHeight / 2 - e.clientY) / 200;
    const y = (e.clientX - window.innerWidth / 2) / 200;
    setRotation({ x, y });
  };
  const handleMouseLeave = () => setRotation({ x: 0, y: 0 });

  const recordingRef = React.useRef(recording);
  useEffect(() => {
    recordingRef.current = recording;
  }, [recording]);

  const handleWakeWord = useCallback(() => {
    console.log("🎤 WAKE WORD DETECTED!");
    const now = new Date().toLocaleTimeString();
    setLastDetection(now);
    setDetectionCount((prev) => prev + 1);

    document.body.style.backgroundColor = "rgba(0,255,0,0.1)";
    setTimeout(() => {
      document.body.style.backgroundColor = "";
    }, 200);

    if (!recordingRef.current) {
      console.log("🎙️ Auto-starting recording after wake word...");
      startRecording();
    } else {
      console.log("⚠️ Already recording, ignoring wake word");
    }
  }, [startRecording]);

  const shouldListen = phase === "main";
  const status = useWakeWord(
    shouldListen ? import.meta.env.VITE_PORCUPINE_KEY : null,
    handleWakeWord
  );
  useEffect(() => setMicStatus(status), [status]);

  useEffect(() => {
    if (phase !== "intro") return;
    let i = 0;
    const text = "Meet ZED, your personalized study buddy.";
    const timer = setInterval(() => {
      setIntroText(text.slice(0, i + 1));
      i++;
      if (i === text.length) {
        clearInterval(timer);
        setTimeout(() => setPhase("login"), 1400);
      }
    }, 70);
    return () => clearInterval(timer);
  }, [phase]);

  useEffect(() => {
    if (phase !== "welcome") return;
    let i = 0;
    const message = "Welcome, Alex 👋 Good luck studying.";
    const timer = setInterval(() => {
      setWelcomeText(message.slice(0, i + 1));
      i++;
      if (i === message.length) {
        clearInterval(timer);
        setTimeout(() => setPhase("main"), 1800);
      }
    }, 55);
    return () => clearInterval(timer);
  }, [phase]);

  useEffect(() => {
    if (transcribedText) {
      console.log("📤 Sending transcribed text to backend:", transcribedText);
      fetch("http://localhost:8000/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: transcribedText }),
      }).catch((err) => console.error("⚠️ Failed to send command:", err));
    }
  }, [transcribedText]);

  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    try {
      const response = await fetch("http://localhost:8000/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: query }),
      });
      const data = await response.json();
      if (data.status === "queued") console.log("✅ Sent:", data.command);
    } catch (err) {
      console.error("⚠️ Failed to send command:", err);
    }
    setQuery("");
  };

  return (
    <AnimatePresence mode="wait">
      {/* INTRO */}
      {phase === "intro" && (
        <motion.div
          key="intro"
          className="h-screen w-screen flex items-center justify-center text-white bg-gradient-to-br from-[#0a0a0f] via-[#161630] to-[#2a0f55] font-sans text-3xl sm:text-5xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 1.05 }}
          transition={{ duration: 1 }}
        >
          {introText}
          <span className="animate-pulse">|</span>
        </motion.div>
      )}

      {/* LOGIN */}
      {phase === "login" && (
        <motion.div
          key="login"
          initial={{ opacity: 0, scale: 1.05 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, y: -40 }}
          transition={{ duration: 1, ease: "easeInOut" }}
        >
          <LoginScene onLoginSuccess={() => setPhase("welcome")} />
        </motion.div>
      )}

      {/* WELCOME */}
      {phase === "welcome" && (
        <motion.div
          key="welcome"
          className="h-screen w-screen flex items-center justify-center text-white bg-gradient-to-br from-[#0a0a0f] via-[#161630] to-[#2a0f55] font-sans text-3xl sm:text-5xl"
          initial={{ opacity: 0, scale: 1.1 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.2 }}
        >
          {welcomeText}
        </motion.div>
      )}

      {/* MAIN */}
      {phase === "main" && (
        <motion.div
          key="main"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -40 }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
        >
          <div
            className="relative h-screen w-screen flex items-center justify-center text-white font-sans overflow-hidden"
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
          >
            <div className="liquid-bg"></div>

            {/* --- Mic indicator --- */}
            {micStatus !== "inactive" && (
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
                  className={`w-3.5 h-3.5 rounded-full transition-all duration-500 ${
                    micStatus === "active"
                      ? "bg-green-500 shadow-[0_0_8px_2px_rgba(34,197,94,0.7)] animate-pulse"
                      : micStatus === "error"
                      ? "bg-red-500"
                      : micStatus === "loading_model"
                      ? "bg-purple-500"
                      : micStatus === "requesting_mic"
                      ? "bg-orange-400"
                      : "bg-yellow-500"
                  }`}
                ></div>

                {/* --- Animated Text --- */}
                <span
                  className="text-sm sm:text-base font-semibold bg-gradient-to-r from-[#8cffb1] via-[#4ee6ff] to-[#ff7ce0] bg-[length:200%_200%] text-transparent bg-clip-text animate-gradientFlow"
                >
                  {micStatus === "active"
                    ? "Listening active"
                    : micStatus === "error"
                    ? "Mic Error"
                    : micStatus === "loading_model"
                    ? "Loading model..."
                    : micStatus === "requesting_mic"
                    ? "Requesting mic..."
                    : "Initializing..."}
                </span>
              </div>
            )}

            {/* --- Main Glass --- */}
            <div
              className="relative z-10 w-[90%] max-w-2xl p-14 rounded-3xl border border-white/20 backdrop-blur-2xl text-center space-y-10 transition-transform duration-300 ease-out"
              style={{
                transform: `perspective(1000px) rotateX(${rotation.x}deg) rotateY(${rotation.y}deg) scale(1.01)`,
                background:
                  "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02))",
                boxShadow:
                  "0 15px 45px rgba(0,0,0,0.45), inset 0 0 25px rgba(255,255,255,0.05)",
              }}
            >
              <h1 className="text-[6rem] sm:text-[7rem] font-extrabold tracking-[0.18em] text-white/95 drop-shadow-[0_0_15px_rgba(255,255,255,0.25)] -mt-6">
                <span className="text-[#ff6b6b]">ZED</span>
                <span className="text-white/90">.AI</span>
              </h1>

              <p className="text-lg text-gray-200 leading-relaxed max-w-lg mx-auto">
                Meet your personal AI assistant — designed to streamline your
                workflow, deliver precise insights, and anticipate your needs.
                <br />
                <span className="text-gray-200">
                  Say{" "}
                  <span className="text-[#ff6b6b] font-semibold">"Hey ZED"</span>{" "}
                  to start.
                </span>
              </p>

              <div className="flex justify-center gap-6">
                <button
                  onClick={() => setShowInput(!showInput)}
                  className="px-8 py-3 bg-white/10 border border-white/20 rounded-xl text-white font-medium hover:bg-white/20 transition-all backdrop-blur-md"
                >
                  Click to Type
                </button>

                <button
                  onMouseDown={startRecording}
                  onMouseUp={stopRecording}
                  className={`px-8 py-3 rounded-xl font-medium border border-white/20 backdrop-blur-md transition-all ${
                    recording
                      ? "bg-red-500/30 text-red-300"
                      : "bg-white/10 text-white hover:bg-white/20"
                  }`}
                >
                  {recording ? "Recording..." : "Hold to Speak"}
                </button>
              </div>

              <AnimatePresence>
                {showInput && (
                  <motion.form
                    initial={{ opacity: 0, y: -10, height: 0 }}
                    animate={{ opacity: 1, y: 0, height: "auto" }}
                    exit={{ opacity: 0, y: -10, height: 0 }}
                    transition={{ duration: 0.4, ease: "easeOut" }}
                    onSubmit={handleTextSubmit}
                    className="flex items-center justify-center"
                  >
                    <input
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Ask ZED anything..."
                      className="w-2/3 px-5 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 backdrop-blur-lg transition"
                    />
                  </motion.form>
                )}
              </AnimatePresence>

              {transcribedText && (
                <p className="text-gray-300 mt-4 text-sm italic">
                  You said: “{transcribedText}”
                </p>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* --- Floating ZED logo --- */}
      <div
        className="fixed bottom-6 right-6 z-50 flex items-center justify-center w-14 h-14 rounded-full backdrop-blur-xl border border-white/20 bg-white/10 floating-logo"
        style={{
          background:
            "linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05))",
          boxShadow:
            "0 8px 25px rgba(0,0,0,0.3), inset 0 0 25px rgba(255,255,255,0.05)",
        }}
      >
        <img
          src="/zed.png"
          alt="ZED Logo"
          className="w-8 h-8 object-contain opacity-90 hover:opacity-100 transition-opacity duration-300"
        />
      </div>
    </AnimatePresence>
  );
}

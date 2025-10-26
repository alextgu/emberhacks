import React, { useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import LoginScene from "./components/LoginScene";
import MainScene from "./components/MainScene";

export default function App() {
  const [phase, setPhase] = useState("intro");
  const [introText, setIntroText] = useState("");
  const [welcomeText, setWelcomeText] = useState("");
  const fullText = "Meet ZED, your personalized study buddy.";

  // Typewriter intro
  useEffect(() => {
    if (phase !== "intro") return;
    let i = 0;
    const timer = setInterval(() => {
      setIntroText(fullText.slice(0, i + 1));
      i++;
      if (i === fullText.length) {
        clearInterval(timer);
        setTimeout(() => setPhase("login"), 1200);
      }
    }, 50);
    return () => clearInterval(timer);
  }, [phase]);

  // Welcome screen text
  useEffect(() => {
    if (phase !== "welcome") return;
    let i = 0;
    const message = "Welcome, Alex 👋 Good luck studying.";
    const timer = setInterval(() => {
      setWelcomeText(message.slice(0, i + 1));
      i++;
      if (i === message.length) {
        clearInterval(timer);
        setTimeout(() => setPhase("main"), 1500);
      }
    }, 40);
    return () => clearInterval(timer);
  }, [phase]);

  return (
    <AnimatePresence mode="wait">
      {phase === "intro" && (
        <motion.div
          key="intro"
          className="h-screen w-screen flex items-center justify-center text-white bg-gradient-to-br from-[#0a0a0f] via-[#161630] to-[#2a0f55] font-[Inter] text-3xl sm:text-5xl"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, scale: 1.05 }}
          transition={{ duration: 1 }}
        >
          {introText}
          <span className="animate-pulse">|</span>
        </motion.div>
      )}

      {phase === "login" && (
        <motion.div
          key="login"
          initial={{ opacity: 0, scale: 1.05 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, y: -40 }}
          transition={{ duration: 0.9, ease: "easeInOut" }}
        >
          <LoginScene onLoginSuccess={() => setPhase("welcome")} />
        </motion.div>
      )}

      {phase === "welcome" && (
        <motion.div
          key="welcome"
          className="h-screen w-screen flex items-center justify-center text-white bg-gradient-to-br from-[#0a0a0f] via-[#161630] to-[#2a0f55] font-[Inter] text-3xl sm:text-5xl"
          initial={{ opacity: 0, scale: 1.1 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1 }}
        >
          {welcomeText}
        </motion.div>
      )}

      {phase === "main" && (
        <motion.div
          key="main"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -40 }}
          transition={{ duration: 0.8, ease: "easeInOut" }}
        >
          <MainScene />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

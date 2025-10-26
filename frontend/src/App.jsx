import React from "react";

export default function App() {
  return (
    <div className="relative h-screen w-screen overflow-hidden bg-gradient-to-br from-[#09091f] via-[#14142f] to-[#2a0f55] text-white font-[Poppins] perspective-[1000px]">
      
      {/* 3D glowing background orbs */}
      <div className="absolute w-[1200px] h-[1200px] bg-gradient-to-tr from-purple-500/30 via-pink-500/20 to-indigo-500/30 rounded-full blur-[200px] animate-slow-spin -top-80 -left-80" />
      <div className="absolute w-[900px] h-[900px] bg-gradient-to-bl from-indigo-400/30 via-purple-400/20 to-pink-400/20 rounded-full blur-[180px] animate-slow-spin reverse bottom-[-400px] right-[-200px]" />

      {/* Main floating glass card */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="relative z-10 p-10 rounded-3xl bg-white/10 backdrop-blur-2xl shadow-[0_0_40px_rgba(255,255,255,0.1)] transform transition-transform duration-700 hover:rotate-x-6 hover:rotate-y-6 hover:scale-[1.03]">
          <h1 className="text-6xl font-bold bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent animate-fade-in">
            ZED Voice Assistant
          </h1>
          <p className="mt-4 text-lg opacity-80 animate-fade-in">
            Your intelligent desktop companion powered by AI 🔥
          </p>

          {/* Glowing button */}
          <button className="mt-8 px-8 py-3 rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white font-semibold shadow-[0_0_25px_rgba(168,85,247,0.6)] hover:shadow-[0_0_50px_rgba(236,72,153,0.9)] transition-all duration-300 animate-pulse-glow">
            Activate ZED
          </button>
        </div>
      </div>
    </div>
  );
}

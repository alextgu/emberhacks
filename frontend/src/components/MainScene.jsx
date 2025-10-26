import React, { useState } from "react";

export default function MainScene() {
  const [showInput, setShowInput] = useState(false);
  const [query, setQuery] = useState("");

  return (
    <div className="relative h-screen w-screen flex items-center justify-center text-white font-[Inter] overflow-hidden">
      <div className="liquid-bg"></div>

      <div className="relative z-10 w-[90%] max-w-2xl p-14 glass-hover text-center space-y-10">
        <h1 className="text-[6rem] sm:text-[7rem] font-extrabold tracking-[0.25em] text-white/95 -mt-6">
          ZED
        </h1>

        <p className="text-lg text-gray-200 leading-relaxed max-w-lg mx-auto">
          Meet your personal AI assistant — designed to streamline your workflow
          and anticipate your needs.
          <br />
          <span className="text-gray-200">
            Say <span className="text-[#ff6b6b] font-semibold">“Hey ZED”</span>{" "}
            to start.
          </span>
        </p>

        <button
          onClick={() => setShowInput(!showInput)}
          className="px-8 py-3 bg-white/10 border border-white/20 rounded-xl text-white font-medium hover:bg-white/20 transition-all backdrop-blur-md"
        >
          Click to Type
        </button>

        {showInput && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              console.log("User asked:", query);
              setQuery("");
            }}
          >
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask ZED anything..."
              className="w-2/3 px-5 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 backdrop-blur-lg transition"
            />
          </form>
        )}
      </div>
    </div>
  );
}

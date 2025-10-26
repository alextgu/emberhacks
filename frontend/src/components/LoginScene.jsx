import React, { useState } from "react";
import { motion } from "framer-motion";

export default function LoginScene({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === "Alex" && password === "EmberHacks") {
      setError("");
      onLoginSuccess();
    } else {
      setError("Incorrect username or password");
    }
  };

  return (
    <div className="relative h-screen w-screen flex items-center justify-center text-white font-[Inter] overflow-hidden">
      <div className="liquid-bg"></div>

      <motion.div
        className="relative z-10 w-[90%] max-w-md p-10 glass-hover text-center space-y-8"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, ease: "easeOut" }}
      >
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-wide">
          Sign In to ZED
        </h1>
        <p className="text-gray-300 text-lg">
          Access your personal AI dashboard
        </p>

        <form onSubmit={handleLogin} className="flex flex-col space-y-5">
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            className="px-5 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 backdrop-blur-lg transition"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="px-5 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 backdrop-blur-lg transition"
          />
          {error && (
            <p className="text-red-400 text-sm font-medium">{error}</p>
          )}
          <button
            type="submit"
            className="w-full px-6 py-3 bg-white/10 border border-white/20 rounded-xl hover:bg-white/20 transition-all backdrop-blur-md"
          >
            Log In
          </button>
        </form>
      </motion.div>
    </div>
  );
}

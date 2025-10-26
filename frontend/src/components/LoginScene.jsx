import { useState } from "react";
import { FiEye, FiEyeOff } from "react-icons/fi"; // 👁️ icons

export default function LoginScene({ onLoginSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === "Alex" && password === "EmberHacks") {
      setError("");
      onLoginSuccess();
    } else {
      setError("Invalid username or password");
    }
  };

  return (
    <div className="h-screen w-screen flex items-center justify-center text-white font-[Inter]">
      <div className="glass-hover relative w-[90%] max-w-md p-10 rounded-3xl border border-white/20 backdrop-blur-2xl text-center space-y-8">
        <h1 className="text-5xl font-extrabold tracking-tight text-white">Sign In to ZED</h1>
        <p className="text-gray-300">
          Access your{" "}
          <span className="relative font-black text-[1.25em] bg-gradient-to-r from-[#ff006a] via-[#ff9900] to-[#3fa9ff] bg-[length:350%_auto] text-transparent bg-clip-text animate-gradient-strong drop-shadow-[0_0_20px_rgba(255,120,0,0.5)]">
            personalized
          </span>{" "}
          AI dashboard
        </p>

        <form onSubmit={handleLogin} className="flex flex-col space-y-5">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-5 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-500/50 transition-all backdrop-blur-lg"
          />

          <div className="relative w-full">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-5 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-500/50 transition-all backdrop-blur-lg pr-12"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-4 flex items-center text-gray-300 hover:text-white transition"
            >
              {showPassword ? <FiEyeOff size={20} /> : <FiEye size={20} />}
            </button>
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            type="submit"
            className="w-full px-6 py-3 bg-white/10 border border-white/20 rounded-xl text-white font-semibold hover:bg-white/20 transition-all backdrop-blur-lg"
          >
            Log In
          </button>
        </form>
      </div>
    </div>
  );
}

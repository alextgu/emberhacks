import React, { useState, useEffect } from "react";

export default function IntroScene({ onComplete }) {
  const [text, setText] = useState("");
  const message = "Meet ZED, your personalized study buddy.";

  useEffect(() => {
    let i = 0;
    const timer = setInterval(() => {
      setText(message.slice(0, i + 1));
      i++;
      if (i === message.length) {
        clearInterval(timer);
        setTimeout(() => onComplete(), 1000);
      }
    }, 60);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="h-screen w-screen flex items-center justify-center text-white bg-gradient-to-br from-[#0a0a0f] via-[#161630] to-[#2a0f55] font-[Inter] text-3xl sm:text-5xl">
      {text}
      <span className="animate-pulse">|</span>
    </div>
  );
}

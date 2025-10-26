import { useState, useCallback, useRef } from "react";

export function useTextToSpeech() {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  const speak = useCallback(async (text, voiceId = "JBFqnCBsd6RMkjVDRZzb") => {
    if (!text) return;

    try {
      setIsPlaying(true);
      console.log("🔊 Generating speech for:", text.substring(0, 50) + "...");

      const response = await fetch("http://localhost:8000/text_to_speech", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, voice_id: voiceId }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get audio blob
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      // Stop any currently playing audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      // Create and play new audio
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        audioRef.current = null;
        console.log("✅ Speech playback complete");
      };

      audio.onerror = (e) => {
        console.error("❌ Audio playback error:", e);
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        audioRef.current = null;
      };

      await audio.play();
      console.log("🎵 Playing speech...");
    } catch (err) {
      console.error("❌ Text-to-speech failed:", err);
      setIsPlaying(false);
    }
  }, []);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
      console.log("⏹️ Speech playback stopped");
    }
  }, []);

  return { speak, stop, isPlaying };
}


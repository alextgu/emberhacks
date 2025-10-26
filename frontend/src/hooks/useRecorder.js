import { useState, useRef } from "react";

export function useRecorder() {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcribedText, setTranscribedText] = useState("");
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        setAudioBlob(blob);

        // 🧠 Send audio to backend for transcription
        const formData = new FormData();
        formData.append("file", blob, "recording.wav");

        try {
          const response = await fetch("http://localhost:8000/transcribe_audio", {
            method: "POST",
            body: formData,
          });

          const data = await response.json();
          if (data.text) {
            setTranscribedText(data.text);
            console.log("✅ Transcription:", data.text);
          } else {
            console.error("❌ Backend error:", data.error || "Unknown");
          }
        } catch (err) {
          console.error("⚠️ Failed to upload audio:", err);
        }
      };

      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (err) {
      console.error("🎤 Microphone access error:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return { recording, audioBlob, transcribedText, startRecording, stopRecording };
}

import { useState, useRef, useCallback } from "react";

export function useRecorder() {
  const [recording, setRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcribedText, setTranscribedText] = useState("");
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const silenceTimeoutRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const silenceStartRef = useRef(null);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      console.log("⏹️ Stopping recording");
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  }, []);

  const startRecording = useCallback(async () => {
    if (recording) {
      console.log("⚠️ Already recording, ignoring start request");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      // Set up audio analysis for silence detection
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 2048;

      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      // Monitor audio levels for silence detection
      const checkAudioLevel = () => {
        if (!analyserRef.current) return;

        analyserRef.current.getByteTimeDomainData(dataArray);
        
        // Calculate average volume
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          const value = Math.abs(dataArray[i] - 128);
          sum += value;
        }
        const average = sum / bufferLength;

        // Threshold for silence (higher = more tolerant of background noise)
        const SILENCE_THRESHOLD = 10; // High threshold to avoid cutting off speech
        const SILENCE_DURATION = 3000; // 3 seconds of silence to be safe

        // Log volume level occasionally for debugging
        if (Math.random() < 0.05) { // 5% of the time
          console.log(`🎚️ Volume level: ${average.toFixed(2)}`);
        }

        if (average < SILENCE_THRESHOLD) {
          if (!silenceStartRef.current) {
            silenceStartRef.current = Date.now();
            console.log(`🔇 Silence detected (${average.toFixed(2)} < ${SILENCE_THRESHOLD}), starting timer...`);
          } else {
            const silenceDuration = Date.now() - silenceStartRef.current;
            if (silenceDuration >= SILENCE_DURATION) {
              console.log("⏹️ Silence threshold reached, stopping recording");
              if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
                mediaRecorderRef.current.stop();
                setRecording(false);
              }
              return;
            }
          }
        } else {
          // Reset silence timer if sound detected
          if (silenceStartRef.current) {
            console.log(`🔊 Sound detected (${average.toFixed(2)} >= ${SILENCE_THRESHOLD}), resetting silence timer`);
          }
          silenceStartRef.current = null;
        }

        // Continue monitoring
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
          silenceTimeoutRef.current = setTimeout(checkAudioLevel, 100);
        }
      };

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        // Cleanup silence detection
        if (silenceTimeoutRef.current) {
          clearTimeout(silenceTimeoutRef.current);
          silenceTimeoutRef.current = null;
        }
        silenceStartRef.current = null;

        // Cleanup audio context
        if (audioContextRef.current) {
          audioContextRef.current.close();
          audioContextRef.current = null;
        }
        analyserRef.current = null;

        // Stop and cleanup stream
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }

        const blob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        setAudioBlob(blob);

        console.log(`🎵 Audio blob created: ${blob.size} bytes, ${audioChunksRef.current.length} chunks`);

        // Check if blob has data
        if (blob.size === 0) {
          console.log("⚠️ No audio data recorded");
          return;
        }

        // 🧠 Send audio to backend for transcription
        const formData = new FormData();
        formData.append("file", blob, "recording.wav");

        setIsTranscribing(true);
        console.log("📤 Sending audio to backend for transcription...");
        console.log("🔗 Backend URL: http://localhost:8000/transcribe_audio");

        try {
          // Try to connect to backend
          const response = await fetch("http://localhost:8000/transcribe_audio", {
            method: "POST",
            body: formData,
          });

          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const data = await response.json();
          if (data.text) {
            setTranscribedText(data.text);
            console.log("✅ Transcription:", data.text);
          } else {
            console.error("❌ Backend returned no text:", data.error || "Unknown");
            setTranscribedText("");
          }
        } catch (err) {
          console.error("❌ Backend connection failed:", err.message);
          
          // Check if it's a connection error
          if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
            console.error("🔴 Backend is not running!");
            console.error("👉 Start it with: cd backend && python main.py");
            alert("⚠️ Backend server is not running!\n\nPlease start it:\n1. Open terminal\n2. cd to backend folder\n3. Run: python main.py");
          }
          
          setTranscribedText("");
        } finally {
          setIsTranscribing(false);
        }
      };

      mediaRecorderRef.current.start();
      setRecording(true);
      console.log("🎙️ Recording started (will stop after 2s of silence or manual stop)");

      // Start monitoring audio levels
      checkAudioLevel();
    } catch (err) {
      console.error("🎤 Microphone access error:", err);
    }
  }, [recording]);

  return { recording, audioBlob, transcribedText, isTranscribing, startRecording, stopRecording };
}

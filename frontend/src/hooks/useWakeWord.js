import { useEffect, useRef, useState } from "react";
import { PorcupineWorker } from "@picovoice/porcupine-web";

/**
 * Custom hook for wake-word detection using Porcupine.
 * @param {string} accessKey - Porcupine Access Key from Picovoice Console.
 * @param {Function} onDetected - Callback when wake word ("Hey ZED") is heard.
 * @returns {string} status - current microphone/model state ("initializing", "active", "error" etc.)
 */
export const useWakeWord = (accessKey, onDetected) => {
  const porcupineRef = useRef(null);
  const [status, setStatus] = useState("initializing");
  const onDetectedRef = useRef(onDetected);

  // Update the ref when callback changes, but don't reinitialize
  useEffect(() => {
    onDetectedRef.current = onDetected;
  }, [onDetected]);

  useEffect(() => {
    let mounted = true;
    let audioContext = null;
    let micStream = null;

    const init = async () => {
      try {
        if (!accessKey) {
          // If no key provided, stay inactive (not an error)
          setStatus("inactive");
          return;
        }

        console.log("🎙 Requesting microphone...");
        setStatus("requesting_mic");
        micStream = await navigator.mediaDevices.getUserMedia({
          audio: {
            sampleRate: 16000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          },
        });

        const track = micStream.getAudioTracks()[0];
        console.log("✅ Microphone access granted:", track.label);

        setStatus("loading_model");
        console.log("🧠 Loading Hey Zed model...");

        const keywordModel = {
          publicPath: "/models/Hey-Zed_en_wasm_v3_0_0.ppn",
          label: "hey zed",
          sensitivity: 0.5,
          customWritePath: "hey_zed_keyword",
          forceWrite: true,
          version: 1,
        };

        const porcupineModel = {
          publicPath: "/models/porcupine_params.pv",
          customWritePath: "porcupine_model",
          forceWrite: true,
          version: 1,
        };

        const porcupine = await PorcupineWorker.create(
          accessKey,
          [keywordModel],
          (keyword) => {
            if (!mounted) return;
            console.log("🎉 Wake word detected:", keyword);
            onDetectedRef.current && onDetectedRef.current();
          },
          porcupineModel
        );

        porcupineRef.current = porcupine;

        // Audio processing setup
        audioContext = new (window.AudioContext || window.webkitAudioContext)({
          sampleRate: porcupine.sampleRate,
        });
        const source = audioContext.createMediaStreamSource(micStream);
        const processor = audioContext.createScriptProcessor(porcupine.frameLength, 1, 1);

        processor.onaudioprocess = (event) => {
          if (!mounted || !porcupineRef.current) return;

          const inputData = event.inputBuffer.getChannelData(0);
          const pcm = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcm[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
          }

          porcupineRef.current.process(pcm);
        };

        source.connect(processor);
        processor.connect(audioContext.destination);

        setStatus("active");
        console.log("🔊 Listening for 'Hey ZED'...");
      } catch (err) {
        console.error("❌ Porcupine init failed:", err);
        setStatus("error");
      }
    };

    init();

    return () => {
      mounted = false;
      if (audioContext) audioContext.close();
      if (micStream) micStream.getTracks().forEach((t) => t.stop());
      if (porcupineRef.current) {
        porcupineRef.current.release();
        porcupineRef.current = null;
      }
    };
  }, [accessKey]); // Only reinitialize if accessKey changes

  return status;
};

import { useEffect, useRef, useState } from "react";
import { PorcupineWorker } from "@picovoice/porcupine-web";

export const useWakeWord = (accessKey, onDetected) => {
  const porcupineRef = useRef(null);
  const [status, setStatus] = useState("initializing");

  useEffect(() => {
    let mounted = true;
    let audioContext = null;
    let micStream = null;

    const init = async () => {
      try {
        if (!accessKey) {
          console.error("❌ No Porcupine access key provided!");
          setStatus("error");
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
            autoGainControl: true
          } 
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
            console.log("🎉🎉🎉 WAKE WORD DETECTED! 🎉🎉🎉");
            console.log("Detected keyword:", keyword);
            onDetected();
          },
          porcupineModel
        );

        porcupineRef.current = porcupine;
        
        // Set up audio processing
        audioContext = new (window.AudioContext || window.webkitAudioContext)({
          sampleRate: porcupine.sampleRate
        });
        
        const source = audioContext.createMediaStreamSource(micStream);
        const processor = audioContext.createScriptProcessor(porcupine.frameLength, 1, 1);
        
        console.log("🎵 Audio context created:");
        console.log("  - Sample rate:", audioContext.sampleRate);
        console.log("  - Frame length:", porcupine.frameLength);
        
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
        console.log("🔊 Porcupine initialized and listening for 'Hey Zed'!");
        console.log("💡 Try saying: 'Hey Zed' clearly into your microphone");
      } catch (err) {
        console.error("❌ Porcupine init failed:", err);
        setStatus("error");
      }
    };

    init();

    return () => {
      mounted = false;
      if (audioContext) {
        audioContext.close();
      }
      if (micStream) {
        micStream.getTracks().forEach(track => track.stop());
      }
      if (porcupineRef.current) {
        porcupineRef.current.release();
      }
    };
  }, [accessKey, onDetected]);

  return status;
};

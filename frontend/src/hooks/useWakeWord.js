import { useEffect, useRef, useState } from "react";
import { PorcupineWorker } from "@picovoice/porcupine-web";

export const useWakeWord = (accessKey, onDetected) => {
  const porcupineRef = useRef(null);
  const [status, setStatus] = useState("initializing");

  useEffect(() => {
    let mounted = true;

    const init = async () => {
      try {
        if (!accessKey) {
          console.error("❌ No Porcupine access key provided!");
          console.error("📝 Create a .env file with: VITE_PORCUPINE_KEY=your_key");
          console.error("🔗 Get a free key at: https://console.picovoice.ai/");
          setStatus("error");
          return;
        }

        console.log("🎙 Requesting microphone...");
        setStatus("requesting_mic");
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log("✅ Microphone access granted:", stream.getAudioTracks()[0].label);
        setStatus("loading_model");

        console.log("🧠 Loading Hey Zed model...");
        
        // Define the custom keyword model
        const keywordModel = {
          publicPath: "/models/Hey-Zed_en_wasm_v3_0_0.ppn",
          label: "hey zed",
          sensitivity: 0.5, // Lowered sensitivity for easier detection (0.0 = most sensitive, 1.0 = least sensitive)
          customWritePath: "hey_zed_keyword",
          forceWrite: true,
          version: 1,
        };

        // Define the Porcupine model
        const porcupineModel = {
          publicPath: "/models/porcupine_params.pv",
          customWritePath: "porcupine_model",
          forceWrite: true,
          version: 1,
        };

        const porcupine = await PorcupineWorker.create(
          accessKey,
          [keywordModel],
          (keywordIndex) => {
            if (!mounted) return;
            console.log("🎉🎉🎉 WAKE WORD DETECTED! 🎉🎉🎉");
            console.log("Keyword index:", keywordIndex);
            onDetected();
          },
          porcupineModel
        );

        porcupineRef.current = porcupine;
        setStatus("active");
        console.log("🔊 Porcupine initialized and actively listening for 'Hey Zed'...");
        console.log("💡 Try saying: 'Hey Zed' clearly into your microphone");
        console.log("🎚️ Sensitivity set to 0.5 (lower = more sensitive)");
      } catch (err) {
        console.error("❌ Porcupine init failed:", err);
        setStatus("error");
      }
    };

    init();

    return () => {
      mounted = false;
      if (porcupineRef.current) porcupineRef.current.release();
    };
  }, [accessKey, onDetected]);

  return status;
};

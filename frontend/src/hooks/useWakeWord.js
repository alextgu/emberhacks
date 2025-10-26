import { useEffect, useRef } from "react";
import { PorcupineWorker } from "@picovoice/porcupine-web";

export const useWakeWord = (accessKey, onDetected) => {
  const porcupineRef = useRef(null);

  useEffect(() => {
    let mounted = true;

    const init = async () => {
      try {
        if (!accessKey) {
          console.error("❌ No Porcupine access key provided!");
          console.error("📝 Create a .env file with: VITE_PORCUPINE_KEY=your_key");
          console.error("🔗 Get a free key at: https://console.picovoice.ai/");
          return;
        }

        console.log("🎙 Requesting microphone...");
        await navigator.mediaDevices.getUserMedia({ audio: true });

        console.log("🧠 Loading Hey Zed model...");
        const porcupine = await PorcupineWorker.create(
          accessKey,
          [
            {
              publicPath: "/models/Hey-Zed_en_mac_v3_0_0.ppn",
              label: "hey zed",
              sensitivity: 0.65,
            },
          ],
          () => {
            if (!mounted) return;
            console.log("✅ Wake word detected!");
            onDetected();
          },
          {
            publicPath: "/models/porcupine_params.pv",
            forceWrite: true,
          }
        );

        porcupineRef.current = porcupine;
        await porcupine.start();
        console.log("🔊 Porcupine initialized, listening for wake word...");
      } catch (err) {
        console.error("❌ Porcupine init failed:", err);
      }
    };

    init();

    return () => {
      mounted = false;
      if (porcupineRef.current) porcupineRef.current.release();
    };
  }, [accessKey, onDetected]);
};

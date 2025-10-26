// hooks/useWakeWord.js
import { useEffect, useRef } from 'react';
import { PorcupineWorker } from '@picovoice/porcupine-web';

export const useWakeWord = (accessKey, onDetected) => {
  const porcupineRef = useRef(null);

  useEffect(() => {
    const init = async () => {
      const porcupine = await PorcupineWorker.create(
        accessKey,
        [{ builtin: "hey google", sensitivity: 0.5 }], // temp placeholder
        () => onDetected() // callback when detected
      );
      
      porcupineRef.current = porcupine;
      await porcupine.start();
    };

    init();

    return () => {
      if (porcupineRef.current) {
        porcupineRef.current.release();
      }
    };
  }, [accessKey, onDetected]);
};
// hooks/useWakeWord.js
import { useEffect, useRef } from 'react';
import { PorcupineWorker } from '@picovoice/porcupine-web';

export const useWakeWord = (accessKey, onDetected) => {
  const porcupineRef = useRef(null);

  useEffect(() => {
    const init = async () => {
      const porcupine = await PorcupineWorker.create(
        accessKey,
        [{ 
          custom: `${process.env.PUBLIC_URL}/models/Hey-Zed.ppn`,  // Your custom wake word
          sensitivity: 0.5 
        }],
        () => onDetected()
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
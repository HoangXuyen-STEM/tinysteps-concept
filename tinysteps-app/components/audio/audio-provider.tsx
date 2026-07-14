"use client";

import React, { createContext, useContext, useRef, useCallback } from "react";

type AudioContextType = {
  play: (audioElement: HTMLAudioElement) => void;
  stopAll: () => void;
};

const AudioContext = createContext<AudioContextType | null>(null);

export function AudioProvider({ children }: { children: React.ReactNode }) {
  const currentAudioRef = useRef<HTMLAudioElement | null>(null);

  const stopAll = useCallback(() => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }
  }, []);

  const play = useCallback(
    (audioElement: HTMLAudioElement) => {
      if (currentAudioRef.current && currentAudioRef.current !== audioElement) {
        currentAudioRef.current.pause();
        currentAudioRef.current.currentTime = 0;
      }
      currentAudioRef.current = audioElement;
      
      // We don't call audioElement.play() here because browsers often require
      // the play() call to be directly in the click event handler.
      // We just register it as the active audio.
    },
    []
  );

  return (
    <AudioContext.Provider value={{ play, stopAll }}>
      {children}
    </AudioContext.Provider>
  );
}

export function useAudio() {
  const context = useContext(AudioContext);
  if (!context) {
    throw new Error("useAudio must be used within an AudioProvider");
  }
  return context;
}

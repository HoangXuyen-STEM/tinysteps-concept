"use client";

import React, { useRef, useState, useEffect } from "react";
import { useAudio } from "./audio-provider";
import { labels } from "@/lib/i18n/labels";

type AudioButtonProps = {
  src: string | null;
  label?: string;
  compact?: boolean;
};

export function AudioButton({ src, label, compact = false }: AudioButtonProps) {
  const { play } = useAudio();
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onPlay = () => setIsPlaying(true);
    const onPause = () => setIsPlaying(false);
    const onEnded = () => setIsPlaying(false);

    audio.addEventListener("play", onPlay);
    audio.addEventListener("pause", onPause);
    audio.addEventListener("ended", onEnded);

    return () => {
      audio.removeEventListener("play", onPlay);
      audio.removeEventListener("pause", onPause);
      audio.removeEventListener("ended", onEnded);
    };
  }, [src]); // Re-bind if src changes, though unlikely in our case

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      play(audio); // Register with context to pause any other playing audio
      audio.play().catch((e) => console.error("Playback failed:", e));
    }
  };

  const isDisabled = src === null;

  return (
    <div
      className={`inline-flex items-center gap-2 ${
        isDisabled ? "opacity-50" : ""
      }`}
    >
      {src && <audio ref={audioRef} src={src} preload="none" />}
      <button
        type="button"
        disabled={isDisabled}
        onClick={togglePlay}
        title={isDisabled ? "Audio not available" : label || labels.NGHE}
        aria-label={label || labels.NGHE}
        className={`flex shrink-0 items-center justify-center rounded-full bg-teal-100 text-teal-700 transition-colors hover:bg-teal-200 disabled:cursor-not-allowed ${
          compact ? "size-8" : "size-10"
        }`}
      >
        {isPlaying ? (
          // Pause Icon
          <svg className={compact ? "size-4" : "size-5"} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        ) : (
          // Play Icon
          <svg className={compact ? "size-4" : "size-5"} fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
          </svg>
        )}
      </button>
      {!compact && label && (
        <span className="text-sm font-semibold text-teal-800">{label}</span>
      )}
    </div>
  );
}

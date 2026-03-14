"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import type { ConversationStep } from "@/types/conversation";

type Status = "idle" | "playing" | "finished";

export function useConversationPlayer(
  steps: ConversationStep[],
  isActive: boolean
) {
  const [visibleSteps, setVisibleSteps] = useState<ConversationStep[]>([]);
  const [status, setStatus] = useState<Status>("idle");
  const indexRef = useRef(0);
  const timeoutsRef = useRef<Set<ReturnType<typeof setTimeout>>>(new Set());
  const mountedRef = useRef(true);
  const pausedRef = useRef(false);
  const advanceRef = useRef<() => void>(() => {});

  const clearAll = useCallback(() => {
    timeoutsRef.current.forEach((t) => clearTimeout(t));
    timeoutsRef.current.clear();
  }, []);

  const track = useCallback((cb: () => void, ms: number) => {
    const id = setTimeout(() => {
      timeoutsRef.current.delete(id);
      if (mountedRef.current && !pausedRef.current) cb();
    }, ms);
    timeoutsRef.current.add(id);
    return id;
  }, []);

  const reset = useCallback(() => {
    clearAll();
    indexRef.current = 0;
    setVisibleSteps([]);
    setStatus("idle");
  }, [clearAll]);

  const advance = useCallback(() => {
    if (!mountedRef.current || pausedRef.current) return;

    const i = indexRef.current;
    if (i >= steps.length) {
      setStatus("finished");
      track(() => {
        reset();
        // Small delay for state to settle, then restart
        track(() => {
          if (!mountedRef.current) return;
          setStatus("playing");
          indexRef.current = 0;
          advanceRef.current();
        }, 100);
      }, 4000);
      return;
    }

    const step = steps[i];
    const delay =
      step.type === "typing" ? 0 : "delay" in step ? step.delay : 0;

    track(() => {
      if (step.type === "typing") {
        setVisibleSteps((prev) => [...prev, step]);
        track(() => {
          setVisibleSteps((prev) => prev.filter((s) => s !== step));
          indexRef.current = i + 1;
          advanceRef.current();
        }, step.duration);
      } else if (step.type === "tap") {
        setVisibleSteps((prev) => [...prev, step]);
        indexRef.current = i + 1;
        advanceRef.current();
      } else {
        setVisibleSteps((prev) => [...prev, step]);
        indexRef.current = i + 1;
        advanceRef.current();
      }
    }, delay);
  }, [steps, reset, track]);

  // Keep advanceRef always pointing to the latest advance
  advanceRef.current = advance;

  useEffect(() => {
    if (isActive && status === "idle") {
      pausedRef.current = false;
      setStatus("playing");
      advance();
    } else if (!isActive && status === "playing") {
      pausedRef.current = true;
      clearAll();
    } else if (isActive && pausedRef.current && status === "playing") {
      pausedRef.current = false;
      advance();
    }
  }, [isActive, status, advance, clearAll]);

  // Cleanup on unmount
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      clearAll();
    };
  }, [clearAll]);

  return { visibleSteps, status };
}

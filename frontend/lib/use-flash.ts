'use client';

import { useEffect, useRef, useState } from 'react';

/** Returns true for ~1.6s whenever `dep` changes (not on first render). */
export function useFlash(dep: unknown): boolean {
  const [on, setOn] = useState(false);
  const prev = useRef(dep);

  useEffect(() => {
    if (prev.current === dep) return;
    prev.current = dep;
    setOn(true);
    const t = setTimeout(() => setOn(false), 1600);
    return () => clearTimeout(t);
  }, [dep]);

  return on;
}

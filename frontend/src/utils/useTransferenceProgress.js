import { useState, useEffect } from 'react';

export default function useTransferenceProgress(containerRef) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    function handleScroll() {
      if (!containerRef.current) return;
      const scrollY = window.scrollY;
      const viewportHeight = window.innerHeight;
      // Complete transference by 75% of viewport height
      const currentProgress = Math.min(Math.max(scrollY / (viewportHeight * 0.75), 0), 1);
      setProgress(currentProgress);
    }

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', handleScroll);
  }, [containerRef]);

  return progress;
}

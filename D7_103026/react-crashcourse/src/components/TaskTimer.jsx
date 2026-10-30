import { useState, useEffect } from 'react';

export function TaskTimer({ isTracking }) {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    let interval = null;

    if (isTracking) {
      // Setup interval timer
      interval = setInterval(() => {
        setSeconds((prevSeconds) => prevSeconds + 1);
      }, 1000);
    }

    // CLEANUP FUNCTION: Prevents memory leaks when component unmounts or deps change
    return () => {
      if (interval) clearInterval(interval);
    }
  }, [isTracking]); // Dependency array: Effect runs when 'isTracking' changes

  return (
    <div className="p-4 border rounded bg-slate-800 text-white">
      <p className="text-sm">Active Session Duration: {seconds}s</p>
    </div>
  );
}

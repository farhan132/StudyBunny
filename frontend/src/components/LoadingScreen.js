import React, { useState, useEffect } from 'react';
import './LoadingScreen.css';

function LoadingScreen({ onComplete }) {
  const [progress, setProgress] = useState(0);
  const [isFading, setIsFading] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(timer);
          setIsFading(true);
          setTimeout(onComplete, 500); // Fade out duration
          return 100;
        }
        return prev + 1.6;
      });
    }, 40); // 2.5 seconds total (100 * 40ms / 1.6 = 2.5 seconds)

    return () => clearInterval(timer);
  }, [onComplete]);

  return (
    <div className={`loading-screen ${isFading ? 'fade-out' : ''}`}>
      <div className="bunny" style={{ left: `${progress}%` }}>
      </div>
    </div>
  );
}

export default LoadingScreen;

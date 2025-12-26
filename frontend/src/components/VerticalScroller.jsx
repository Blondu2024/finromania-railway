import React, { useRef, useEffect, useState } from 'react';
import './VerticalScroller.css';

export default function VerticalScroller({ children, speed = 30, pauseOnHover = true }) {
  const scrollerRef = useRef(null);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    const scroller = scrollerRef.current;
    if (!scroller) return;

    const scrollerContent = scroller.querySelector('.scroller-content');
    if (!scrollerContent) return;

    // Duplicate content for seamless loop
    const scrollerContentClone = scrollerContent.cloneNode(true);
    scroller.appendChild(scrollerContentClone);

    let scrollPosition = 0;
    let lastTime = Date.now();

    const scroll = () => {
      const now = Date.now();
      const deltaTime = (now - lastTime) / 1000; // Convert to seconds
      lastTime = now;

      if (!isPaused) {
        scrollPosition += speed * deltaTime;
        const contentHeight = scrollerContent.offsetHeight;
        
        if (scrollPosition >= contentHeight) {
          scrollPosition = 0;
        }
        
        scroller.scrollTop = scrollPosition;
      }
      
      requestAnimationFrame(scroll);
    };

    // Start scroll immediately
    requestAnimationFrame(scroll);

    return () => {
      // Cleanup handled by RAF loop ending
    };
  }, [isPaused, speed]);

  return (
    <div
      ref={scrollerRef}
      className="vertical-scroller"
      style={{ maxHeight: '600px', overflow: 'hidden', position: 'relative' }}
      onMouseEnter={() => pauseOnHover && setIsPaused(true)}
      onMouseLeave={() => pauseOnHover && setIsPaused(false)}
    >
      <div className="scroller-content">
        {children}
      </div>
    </div>
  );
}

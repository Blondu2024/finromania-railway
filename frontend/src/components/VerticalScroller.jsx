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

    let animationId;
    let scrollPosition = 0;
    const contentHeight = scrollerContent.offsetHeight;

    const scroll = () => {
      if (!isPaused) {
        scrollPosition += 0.5;
        if (scrollPosition >= contentHeight) {
          scrollPosition = 0;
        }
        scroller.scrollTop = scrollPosition;
      }
      animationId = requestAnimationFrame(scroll);
    };

    animationId = requestAnimationFrame(scroll);

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
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

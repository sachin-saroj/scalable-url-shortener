import { useState, useEffect } from 'react';

export default function AnimatedHeading({ text, className = "", style = {} }) {
  const [animate, setAnimate] = useState(false);
  const initialDelay = 200; // ms
  const charDelay = 30; // ms
  const transitionDuration = 500; // ms

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimate(true);
    }, initialDelay);
    return () => clearTimeout(timer);
  }, []);

  const lines = text.split('\n');

  return (
    <h1 className={className} style={{ ...style, display: 'block' }}>
      {lines.map((line, lineIndex) => {
        const lineLength = line.length;
        return (
          <span key={lineIndex} className="block" style={{ display: 'block' }}>
            {line.split('').map((char, charIndex) => {
              const delay = (lineIndex * lineLength * charDelay) + (charIndex * charDelay);
              const isSpace = char === ' ';
              
              return (
                <span
                  key={charIndex}
                  className="inline-block"
                  style={{
                    display: 'inline-block',
                    opacity: animate ? 1 : 0,
                    transform: animate ? 'translateX(0)' : 'translateX(-18px)',
                    transition: `opacity ${transitionDuration}ms ease-out, transform ${transitionDuration}ms ease-out`,
                    transitionDelay: `${delay}ms`,
                  }}
                >
                  {isSpace ? '\u00A0' : char}
                </span>
              );
            })}
          </span>
        );
      })}
    </h1>
  );
}

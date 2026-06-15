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
        const words = line.split(' ');
        const lineLength = line.length;
        let charGlobalIndex = 0;

        return (
          <span key={lineIndex} className="block" style={{ display: 'block' }}>
            {words.map((word, wordIndex) => {
              const chars = word.split('');
              return (
                <span key={wordIndex} className="inline-block" style={{ display: 'inline-block', whiteSpace: 'nowrap' }}>
                  {chars.map((char, charIndex) => {
                    const delay = (lineIndex * lineLength * charDelay) + (charGlobalIndex * charDelay);
                    charGlobalIndex++;

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
                        {char}
                      </span>
                    );
                  })}
                  
                  {wordIndex < words.length - 1 && (
                    <span
                      className="inline-block"
                      style={{
                        display: 'inline-block',
                        opacity: animate ? 1 : 0,
                        transform: animate ? 'translateX(0)' : 'translateX(-18px)',
                        transition: `opacity ${transitionDuration}ms ease-out, transform ${transitionDuration}ms ease-out`,
                        transitionDelay: `${(lineIndex * lineLength * charDelay) + (charGlobalIndex * charDelay)}ms`,
                      }}
                    >
                      {'\u00A0'}
                    </span>
                  )}
                  
                  {(() => {
                    if (wordIndex < words.length - 1) {
                      charGlobalIndex++;
                    }
                    return null;
                  })()}
                </span>
              );
            })}
          </span>
        );
      })}
    </h1>
  );
}

import { useEffect, useRef, useState } from 'react';

export default function ScribbleSilhouette() {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const [isHovered, setIsHovered] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 150, y: 120 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set high-DPI canvas resolution
    const width = 300;
    const height = 300;
    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // Initialize scribble points
    const numPoints = 8;
    const points = [];
    
    // Silhouette center
    const centerX = 150;
    const centerY = 120;

    for (let i = 0; i < numPoints; i++) {
      points.push({
        x: centerX + (Math.random() - 0.5) * 50,
        y: centerY + (Math.random() - 0.5) * 50,
        vx: (Math.random() - 0.5) * 4,
        vy: (Math.random() - 0.5) * 4,
        history: []
      });
    }

    let animationFrameId;

    function animate() {
      // Draw semi-transparent background to fade older scribbles slowly
      // Matches our brutalist card's background color (#ffffff)
      ctx.fillStyle = 'rgba(255, 255, 255, 0.12)';
      ctx.fillRect(0, 0, width, height);

      // Scribble lines styling
      ctx.strokeStyle = '#000000';
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';

      points.forEach((p, idx) => {
        // Random walk forces
        const speedMultiplier = isHovered ? 2.5 : 1.2;
        p.vx += (Math.random() - 0.5) * 2 * speedMultiplier;
        p.vy += (Math.random() - 0.5) * 2 * speedMultiplier;

        // Apply friction
        p.vx *= 0.92;
        p.vy *= 0.92;

        // Pull toward center (gravity)
        const dx = centerX - p.x;
        const dy = centerY - p.y;
        p.vx += dx * 0.012;
        p.vy += dy * 0.012;

        // If hovered, pull slightly toward mouse
        if (isHovered) {
          const mdx = mousePos.x - p.x;
          const mdy = mousePos.y - p.y;
          p.vx += mdx * 0.025;
          p.vy += mdy * 0.025;
        }

        // Update positions
        const prevX = p.x;
        const prevY = p.y;
        p.x += p.vx;
        p.y += p.vy;

        // Draw line with varying thickness for raw hand-drawn style
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        ctx.lineTo(p.x, p.y);
        ctx.lineWidth = 1 + Math.random() * 1.5;
        ctx.stroke();

        // Overlapping scribble connections for a chaotic tangled look
        if (idx > 0 && Math.random() < 0.25) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(points[idx - 1].x, points[idx - 1].y);
          ctx.lineWidth = 0.5;
          ctx.strokeStyle = 'rgba(0, 0, 0, 0.15)';
          ctx.stroke();
          ctx.strokeStyle = '#000000'; // Reset
        }
      });

      animationFrameId = requestAnimationFrame(animate);
    }

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isHovered, mousePos]);

  function handleMouseMove(e) {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setMousePos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  }

  // Silhouette Path Coordinates
  const silhouettePath = "M 110,250 C 110,195 80,175 80,130 C 80,75 110,40 150,40 C 195,40 220,70 220,100 C 220,108 232,114 238,118 C 244,122 238,127 232,129 C 224,132 220,138 225,144 C 230,150 225,156 220,159 C 214,162 208,164 212,172 C 217,182 208,192 196,195 C 180,199 170,210 170,250 Z";

  return (
    <div 
      ref={containerRef}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onMouseMove={handleMouseMove}
      style={{
        position: 'relative',
        width: '300px',
        height: '300px',
        background: '#ffffff',
        border: '2px solid #000000',
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-flat)',
        cursor: 'crosshair',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
      className="scribble-silhouette-card"
    >
      {/* Background blueprint grid dots */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: 'radial-gradient(#e4e4e7 1px, transparent 1px)',
        backgroundSize: '12px 12px',
        opacity: 0.8,
        pointerEvents: 'none'
      }} />

      {/* SVG Container for the Clip Path and Outline */}
      <svg 
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          zIndex: 2
        }}
        viewBox="0 0 300 300"
      >
        <defs>
          <clipPath id="head-clip">
            <path d={silhouettePath} />
          </clipPath>
        </defs>

        {/* Outer silhouette outline */}
        <path 
          d={silhouettePath} 
          fill="none" 
          stroke="#000000" 
          strokeWidth="3.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Technical crosshair overlays */}
        <line x1="150" y1="10" x2="150" y2="30" stroke="#000000" strokeWidth="1" />
        <line x1="150" y1="270" x2="150" y2="290" stroke="#000000" strokeWidth="1" />
        <line x1="10" y1="150" x2="30" y2="150" stroke="#000000" strokeWidth="1" />
        <line x1="270" y1="150" x2="290" y2="150" stroke="#000000" strokeWidth="1" />
      </svg>

      {/* Clipped Canvas for scribbling */}
      <canvas 
        ref={canvasRef}
        style={{
          clipPath: 'url(#head-clip)',
          WebkitClipPath: 'url(#head-clip)',
          zIndex: 1
        }}
      />

      {/* Hover scanner active overlay indicator */}
      {isHovered && (
        <div style={{
          position: 'absolute',
          bottom: '12px',
          left: '12px',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.65rem',
          background: '#000000',
          color: '#ffffff',
          padding: '2px 6px',
          borderRadius: '2px',
          zIndex: 3,
          animation: 'pulse 1s infinite alternate'
        }}>
          LIVE_CONSCIOUSNESS_STREAM: TRUE
        </div>
      )}
    </div>
  );
}

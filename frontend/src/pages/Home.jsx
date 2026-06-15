import { useRef } from 'react';
import { Link } from 'react-router-dom';
import ShortenForm from '../components/ShortenForm';
import { useAuth } from '../context/AuthContext';
import AnimatedHeading from '../components/AnimatedHeading';
import FadeIn from '../components/FadeIn';
import useTransferenceProgress from '../utils/useTransferenceProgress';

export default function Home() {
  const { isAuthenticated } = useAuth();
  const heroRef = useRef(null);
  const progress = useTransferenceProgress(heroRef);

  // Hero transference math: fades out and translates upwards
  const heroOpacity = Math.max(1 - progress / 0.6, 0);
  const heroTranslateY = -progress * 32;
  const heroScale = 1 - progress * 0.02;

  // Shorten transference math: materializes from bottom
  const shortenOpacity = progress < 0.35 ? 0 : Math.min((progress - 0.35) / 0.65, 1);
  const shortenTranslateY = 48 - progress * 48;
  const shortenScale = 0.97 + progress * 0.03;

  return (
    <div className="w-full min-h-screen text-white selection:bg-white/10 selection:text-white relative" ref={heroRef}>
      
      {/* Fixed Full-screen Background Video */}
      <div className="fixed inset-0 -z-10 w-full h-full">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260403_050628_c4e32401-fab4-4a27-b7a8-6e9291cd5959.mp4"
        />
      </div>

      {/* ── HERO SECTION ── */}
      <section className="relative w-full min-h-screen flex flex-col justify-end px-6 md:px-12 lg:px-16 pb-12 lg:pb-16">
        <div 
          className="transference-panel w-full lg:grid lg:grid-cols-2 lg:items-end gap-12 z-10"
          style={{
            opacity: heroOpacity,
            transform: `translateY(${heroTranslateY}px) scale(${heroScale})`,
            pointerEvents: progress > 0.5 ? 'none' : 'auto',
          }}
        >
          {/* Left Column: Main Content */}
          <div className="flex flex-col items-start">
            <AnimatedHeading 
              text={"Routing the web\nwith speed and precision."}
              className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-normal mb-4 text-white leading-tight tracking-tight"
              style={{ letterSpacing: '-0.04em' }}
            />

            <FadeIn delay={800} duration={1000}>
              <p className="text-base md:text-lg text-gray-300 mb-5 max-w-[520px]">
                Sub-50ms Redis-backed redirects, custom aliases, analytics, and QR.
              </p>
            </FadeIn>

            <FadeIn delay={1200} duration={1000} className="w-full">
              <div className="flex flex-wrap gap-4">
                {isAuthenticated ? (
                  <Link to="/dashboard" className="bg-white !text-black px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors no-underline text-center">
                    Launch Console
                  </Link>
                ) : (
                  <a href="#shorten" className="bg-white !text-black px-8 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors no-underline text-center">
                    Shorten Now
                  </a>
                )}
                <Link to="/platform" className="liquid-glass border border-white/20 text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:!text-black transition-colors no-underline text-center">
                  Explore Platform
                </Link>
              </div>
            </FadeIn>
          </div>

          {/* Right Column: Tag */}
          <div className="flex items-end justify-start lg:justify-end mt-8 lg:mt-0">
            <FadeIn delay={1400} duration={1000}>
              <div className="liquid-glass border border-white/20 px-6 py-3 rounded-xl">
                <span className="text-lg md:text-xl lg:text-2xl font-light text-white">
                  Shorten. Track. Scale.
                </span>
              </div>
            </FadeIn>
          </div>
        </div>
      </section>

      {/* ── SHORTEN SECTION ── */}
      <section 
        id="shorten" 
        className="relative w-full min-h-screen flex flex-col justify-center items-center px-6 md:px-12 lg:px-16"
      >
        <div 
          className="transference-panel w-full max-w-[800px] z-10 flex flex-col items-center"
          style={{
            opacity: shortenOpacity,
            transform: `translateY(${shortenTranslateY}px) scale(${shortenScale})`,
            pointerEvents: progress > 0.4 ? 'auto' : 'none',
          }}
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-normal text-white mb-2 text-center tracking-tight" style={{ letterSpacing: '-0.03em' }}>
            Create your link
          </h2>
          <p className="text-gray-300 text-sm md:text-base mb-8 text-center max-w-[500px]">
            Generate clean, secure redirects instantly.
          </p>
          <ShortenForm minimal={true} />
        </div>
      </section>
      
    </div>
  );
}

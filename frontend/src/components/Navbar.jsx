import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const isMarketingPage = location.pathname === '/' || location.pathname === '/platform';

  return (
    <div className={`w-full px-6 md:px-12 lg:px-16 pt-6 z-50 ${isMarketingPage ? 'fixed top-0 left-0 right-0' : 'relative'}`}>
      <nav 
        className="liquid-glass rounded-xl px-4 py-2 flex items-center justify-between"
        id="main-navbar" 
        role="navigation" 
        aria-label="Main navigation"
      >
        {/* Left: Brand logo */}
        <Link to="/" className="text-2xl font-semibold tracking-tight !text-white hover:!text-gray-300 transition-colors no-underline">
          LinkForge
        </Link>

        {/* Center: Navigation links (hidden on mobile, visible md+) */}
        <div className="hidden md:flex items-center gap-8">
          <a href="/#shorten" className="text-sm !text-white hover:!text-gray-300 transition-colors duration-200 no-underline font-medium">
            Shorten
          </a>
          <Link to="/platform" className="text-sm !text-white hover:!text-gray-300 transition-colors duration-200 no-underline font-medium">
            Platform
          </Link>
          <a href="/platform#architecture" className="text-sm !text-white hover:!text-gray-300 transition-colors duration-200 no-underline font-medium">
            Architecture
          </a>
          {isAuthenticated && (
            <Link to="/dashboard" className="text-sm !text-white hover:!text-gray-300 transition-colors duration-200 no-underline font-medium">
              Console
            </Link>
          )}
        </div>

        {/* Right: Call to Action and Auth state */}
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <>
              <span className="hidden sm:inline-block text-xs font-mono text-gray-400 px-2 py-1 border border-white/10 rounded-lg">
                {user?.username}
              </span>
              <button 
                onClick={logout} 
                className="text-sm !text-white hover:!text-gray-300 transition-colors bg-transparent border-none cursor-pointer no-underline"
                id="logout-btn"
              >
                Logout
              </button>
              <Link 
                to="/dashboard" 
                className="bg-white !text-black px-6 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors no-underline"
                id="console-btn"
              >
                Console
              </Link>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm !text-white hover:!text-gray-300 transition-colors no-underline">
                Login
              </Link>
              <Link 
                to="/register" 
                className="bg-white !text-black px-6 py-2 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors no-underline"
                id="register-nav-btn"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </nav>
    </div>
  );
}

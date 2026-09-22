import { useEffect, useState } from 'react';
import { BrandPanel } from '@/components/BrandPanel';
import { SignInForm } from '@/components/SignInForm';
import { DashboardShell } from '@/components/dashboard/DashboardShell';
import { SessionProvider, useSession, MOCK_USER } from '@/auth/session';

function AppContent() {
  const { user, signIn } = useSession();
  const [showSuccess, setShowSuccess] = useState(false);

  // When the sign-in form reports success, show the confirmation card briefly
  // then transition into the dashboard. This keeps the login page unchanged
  // while bridging into the authenticated shell.
  const handleSignInSuccess = () => {
    setShowSuccess(true);
  };

  useEffect(() => {
    if (!showSuccess) return;
    const timer = setTimeout(() => {
      signIn(MOCK_USER);
    }, 1600);
    return () => clearTimeout(timer);
  }, [showSuccess, signIn]);

  if (user) {
    return <DashboardShell />;
  }

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center bg-gradient-to-br from-canvas via-navy-50 to-canvas p-3 sm:p-6 lg:p-8">
      {/* Ambient background accents */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -top-24 -left-24 h-72 w-72 rounded-full bg-royal-200/30 blur-3xl" />
        <div className="absolute -bottom-32 -right-16 h-80 w-80 rounded-full bg-navy-200/30 blur-3xl" />
        <div className="absolute inset-0 bg-grid opacity-50" />
      </div>

      {/* Main container — split 58/42 on desktop, stacked on mobile */}
      <div className="relative z-10 grid h-[100svh] w-full max-w-6xl overflow-hidden rounded-[20px] bg-white shadow-container sm:h-[640px] sm:rounded-[24px] lg:h-[680px] lg:rounded-[28px] lg:grid-cols-[58fr_42fr]">
        {/* Left — brand panel (hidden on small screens) */}
        <div className="hidden lg:block">
          <BrandPanel />
        </div>

        {/* Right — sign-in form */}
        <div className="min-h-0">
          <SignInForm onSuccess={handleSignInSuccess} />
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <SessionProvider>
      <AppContent />
    </SessionProvider>
  );
}

export default App;

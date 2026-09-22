import { useState, type FormEvent } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  GraduationCap,
  Mail,
  Lock,
  Eye,
  EyeOff,
  Loader2,
  AlertCircle,
  CheckCircle2,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '@/auth/useAuth';

function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1Z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23Z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.1a6.6 6.6 0 0 1 0-4.2V7.06H2.18a11 11 0 0 0 0 9.88l3.66-2.84Z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38Z"
      />
    </svg>
  );
}

export function SignInForm({ onSuccess }: { onSuccess?: () => void }) {
  const { state, errorMessage, signIn, reset, isSuccess } = useAuth({ onSuccess });
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [showPassword, setShowPassword] = useState(false);

  const isLoading = state === 'loading';
  const isError = state === 'error';

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (isLoading || isSuccess) return;
    await signIn({ email, password, remember });
  };

  const handleInputChange = (setter: (v: string) => void) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setter(e.target.value);
    if (isError) reset();
  };

  return (
    <div className="flex h-full w-full flex-col bg-white px-6 py-7 sm:px-10 sm:py-9 lg:px-12 lg:py-10">
      {/* Top — back link */}
      <div className="flex justify-end animate-fade-in">
        <a
          href="#"
          onClick={(e) => e.preventDefault()}
          className="group inline-flex items-center gap-1.5 text-sm font-600 text-navy-500 transition-colors hover:text-royal-600"
        >
          <ArrowLeft className="h-4 w-4 transition-transform duration-200 group-hover:-translate-x-0.5" />
          Back to Home
        </a>
      </div>

      {/* Center — form area */}
      <div className="flex flex-1 items-center justify-center">
        <div className="w-full max-w-sm">
          {/* Logo + heading */}
          <div className="mb-7 text-center animate-scale-in">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-royal-500 to-royal-700 shadow-card">
              <GraduationCap className="h-7 w-7 text-white" strokeWidth={2.2} />
            </div>
            <h2 className="font-display text-2xl font-700 tracking-tight text-navy-900">
              Smart Campus <span className="text-royal-600">Data Hub</span>
            </h2>
            <p className="mt-2 text-sm text-navy-400">
              Sign in to access your campus analytics
            </p>
          </div>

          {/* Success state */}
          {isSuccess ? (
            <div className="rounded-2xl border border-green-200 bg-green-50 p-6 text-center animate-scale-in">
              <CheckCircle2 className="mx-auto mb-3 h-10 w-10 text-green-500" />
              <p className="font-display text-lg font-700 text-green-700">Signed In</p>
              <p className="mt-1 text-sm text-green-600">{errorMessage}</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              {/* Error banner */}
              {isError && (
                <div className="flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 px-3.5 py-3 animate-shake">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
                  <p className="text-[13px] font-500 leading-snug text-red-600">{errorMessage}</p>
                </div>
              )}

              {/* Email */}
              <div>
                <label
                  htmlFor="email"
                  className="mb-1.5 block text-[13px] font-600 text-navy-700"
                >
                  Email
                </label>
                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-navy-300" />
                  <input
                    id="email"
                    type="email"
                    autoComplete="email"
                    placeholder="you@university.edu"
                    value={email}
                    onChange={handleInputChange(setEmail)}
                    disabled={isLoading}
                    className="w-full rounded-xl border border-navy-200 bg-navy-50/40 py-3 pl-11 pr-4 text-sm font-500 text-navy-900 placeholder:text-navy-300 transition-all duration-200 hover:border-navy-300 focus:border-royal-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-royal-500/15 disabled:opacity-60"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label
                  htmlFor="password"
                  className="mb-1.5 block text-[13px] font-600 text-navy-700"
                >
                  Password
                </label>
                <div className="relative">
                  <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-navy-300" />
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={handleInputChange(setPassword)}
                    disabled={isLoading}
                    className="w-full rounded-xl border border-navy-200 bg-navy-50/40 py-3 pl-11 pr-11 text-sm font-500 text-navy-900 placeholder:text-navy-300 transition-all duration-200 hover:border-navy-300 focus:border-royal-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-royal-500/15 disabled:opacity-60"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    tabIndex={-1}
                    className="absolute right-3 top-1/2 -translate-y-1/2 rounded-md p-1 text-navy-400 transition-colors hover:text-navy-700"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="h-[18px] w-[18px]" /> : <Eye className="h-[18px] w-[18px]" />}
                  </button>
                </div>
              </div>

              {/* Remember + forgot */}
              <div className="flex items-center justify-between pt-0.5">
                <label className="flex cursor-pointer items-center gap-2 select-none">
                  <button
                    type="button"
                    role="switch"
                    aria-checked={remember}
                    onClick={() => setRemember((r) => !r)}
                    className={`relative h-5 w-9 rounded-full transition-colors duration-200 ${
                      remember ? 'bg-royal-500' : 'bg-navy-200'
                    }`}
                  >
                    <span
                      className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200 ${
                        remember ? 'translate-x-[18px]' : 'translate-x-0.5'
                      }`}
                    />
                  </button>
                  <span className="text-[13px] font-500 text-navy-600">Remember me</span>
                </label>
                <a
                  href="#"
                  onClick={(e) => e.preventDefault()}
                  className="text-[13px] font-600 text-royal-600 transition-colors hover:text-royal-700"
                >
                  Forgot password?
                </a>
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={isLoading}
                className="group relative mt-1 flex w-full items-center justify-center gap-2 overflow-hidden rounded-xl bg-gradient-to-r from-royal-600 to-royal-700 py-3.5 text-sm font-700 text-white shadow-card transition-all duration-300 hover:shadow-glow hover:brightness-110 focus:outline-none focus:ring-4 focus:ring-royal-500/25 disabled:cursor-not-allowed disabled:opacity-80"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-[18px] w-[18px] animate-spin" />
                    Signing in…
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="h-[18px] w-[18px] transition-transform duration-200 group-hover:translate-x-1" />
                  </>
                )}
              </button>

              {/* Divider */}
              <div className="flex items-center gap-3 py-1">
                <div className="h-px flex-1 bg-navy-100" />
                <span className="text-[12px] font-500 uppercase tracking-wider text-navy-300">
                  Or continue with
                </span>
                <div className="h-px flex-1 bg-navy-100" />
              </div>

              {/* Google */}
              <button
                type="button"
                disabled={isLoading}
                className="flex w-full items-center justify-center gap-2.5 rounded-xl border border-navy-200 bg-white py-3 text-sm font-600 text-navy-700 transition-all duration-200 hover:border-navy-300 hover:bg-navy-50 focus:outline-none focus:ring-4 focus:ring-navy-200/50 disabled:opacity-60"
              >
                <GoogleIcon className="h-5 w-5" />
                Continue with Google
              </button>
            </form>
          )}

          {/* Bottom — new user */}
          {isSuccess ? (
            <div className="mt-6 flex items-center justify-center gap-1.5 text-[13px] text-navy-500 animate-fade-in">
              <ShieldCheck className="h-4 w-4 text-green-500" />
              <span>Secure session established.</span>
            </div>
          ) : (
            <p className="mt-6 text-center text-[13px] text-navy-400">
              New to the system?{' '}
              <a
                href="#"
                onClick={(e) => e.preventDefault()}
                className="font-600 text-royal-600 transition-colors hover:text-royal-700"
              >
                Contact your administrator.
              </a>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

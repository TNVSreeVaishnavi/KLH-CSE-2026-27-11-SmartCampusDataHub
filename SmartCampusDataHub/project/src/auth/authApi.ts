/**
 * Authentication logic for Smart Campus Data Hub.
 *
 * This is a UI-only mock that simulates realistic auth states so the
 * interface can be developed and demoed independently of the backend.
 *
 * To connect a real backend later, replace the body of `signIn` with a
 * fetch/Supabase call to your API and keep the same return shape.
 */

export type AuthState = 'idle' | 'loading' | 'error' | 'success';

export interface SignInPayload {
  email: string;
  password: string;
  remember: boolean;
}

export interface SignInResult {
  state: 'success' | 'error';
  message: string;
}

export interface AuthApi {
  signIn(payload: SignInPayload): Promise<SignInResult>;
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const isValidCampusEmail = (email: string) =>
  /^[^\s@]+@(?:[^\s@]+\.)?edu$|[^\s@]+@university\.edu$/i.test(email.trim());

/**
 * Mock implementation. Simulates network latency and validates credentials
 * against a small hardcoded set. Swap for a real API call later.
 */
export const mockAuthApi: AuthApi = {
  async signIn({ email, password }) {
    await delay(1400);

    const normalized = email.trim().toLowerCase();

    if (!normalized || !password) {
      return {
        state: 'error',
        message: 'Please enter both your university email and password.',
      };
    }

    if (!isValidCampusEmail(normalized)) {
      return {
        state: 'error',
        message: 'Use your university (.edu) email address to sign in.',
      };
    }

    // Demo credentials — replace with real authentication.
    if (password.length < 6) {
      return {
        state: 'error',
        message: 'Incorrect email or password. Please try again.',
      };
    }

    return {
      state: 'success',
      message: 'Welcome back! Redirecting to your dashboard…',
    };
  },
};

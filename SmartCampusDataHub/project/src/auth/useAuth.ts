import { useCallback, useRef, useState } from 'react';
import {
  mockAuthApi,
  type AuthApi,
  type SignInPayload,
  type AuthState,
} from './authApi';

export interface UseAuthOptions {
  api?: AuthApi;
  onSuccess?: () => void;
}

export interface UseAuthReturn {
  state: AuthState;
  errorMessage: string;
  signIn: (payload: SignInPayload) => Promise<void>;
  reset: () => void;
  isSuccess: boolean;
}

/**
 * Encapsulates sign-in flow state so the form component stays presentational.
 * Defaults to the mock API; pass a real `api` once the backend is wired up.
 */
export function useAuth({ api = mockAuthApi, onSuccess }: UseAuthOptions = {}): UseAuthReturn {
  const [state, setState] = useState<AuthState>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const requestLock = useRef(false);

  const signIn = useCallback(
    async (payload: SignInPayload) => {
      if (requestLock.current) return;
      requestLock.current = true;

      setState('loading');
      setErrorMessage('');

      try {
        const result = await api.signIn(payload);
        if (result.state === 'success') {
          setState('success');
          onSuccess?.();
        } else {
          setState('error');
          setErrorMessage(result.message);
        }
      } catch {
        setState('error');
        setErrorMessage('Something went wrong. Please try again in a moment.');
      } finally {
        requestLock.current = false;
      }
    },
    [api, onSuccess],
  );

  const reset = useCallback(() => {
    setState('idle');
    setErrorMessage('');
  }, []);

  const isSuccess = state === 'success';

  return { state, errorMessage, signIn, reset, isSuccess };
}

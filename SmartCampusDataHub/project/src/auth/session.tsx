import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

export interface SessionUser {
  name: string;
  role: string;
  email: string;
}

interface SessionContextValue {
  user: SessionUser | null;
  signIn: (user: SessionUser) => void;
  signOut: () => void;
}

const SessionContext = createContext<SessionContextValue | null>(null);

export const MOCK_USER: SessionUser = {
  name: 'Vaishnavi',
  role: 'Student',
  email: 'vaishnavi@university.edu',
};

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(null);

  const value = useMemo<SessionContextValue>(
    () => ({
      user,
      signIn: (u) => setUser(u),
      signOut: () => setUser(null),
    }),
    [user],
  );

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession must be used within SessionProvider');
  return ctx;
}

import { useEffect, useRef, useState } from 'react';
import {
  Search,
  Bell,
  Settings,
  Menu,
  LogOut,
  ChevronDown,
  UserCircle,
  HelpCircle,
} from 'lucide-react';
import { useSession } from '@/auth/session';

interface HeaderProps {
  onOpenMobileNav: () => void;
}

const NOTIFICATIONS = [
  { title: 'Pipeline sync completed', time: '2 min ago', unread: true },
  { title: 'New student record imported', time: '1 hour ago', unread: true },
  { title: 'Data quality check passed', time: '3 hours ago', unread: false },
];

export function Header({ onOpenMobileNav }: HeaderProps) {
  const { user, signOut } = useSession();
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false);
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) setProfileOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const initials = (user?.name ?? 'U')
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="sticky top-0 z-20 flex items-center gap-3 border-b border-navy-100 bg-white/80 px-4 py-3 backdrop-blur-md sm:px-6 lg:px-8">
      {/* Mobile menu toggle */}
      <button
        onClick={onOpenMobileNav}
        className="rounded-lg p-2 text-navy-600 transition-colors hover:bg-navy-50 lg:hidden"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Search */}
      <div className="relative hidden flex-1 sm:block sm:max-w-md">
        <Search className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-navy-300" />
        <input
          type="search"
          placeholder="Search students, events, datasets…"
          className="w-full rounded-xl border border-navy-200 bg-navy-50/50 py-2.5 pl-11 pr-4 text-sm font-500 text-navy-900 placeholder:text-navy-300 transition-all duration-200 hover:border-navy-300 focus:border-royal-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-royal-500/10"
        />
      </div>

      <div className="flex flex-1 items-center justify-end gap-1.5 sm:flex-none">
        {/* Notifications */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => {
              setNotifOpen((o) => !o);
              setProfileOpen(false);
            }}
            className="relative rounded-xl p-2.5 text-navy-600 transition-all duration-200 hover:bg-navy-50 hover:text-navy-900"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute right-2 top-2 flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-royal-500 opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-royal-500" />
            </span>
          </button>

          {notifOpen && (
            <div className="absolute right-0 mt-2 w-80 origin-top-right rounded-2xl border border-navy-100 bg-white p-2 shadow-container animate-scale-in">
              <div className="flex items-center justify-between px-3 py-2">
                <p className="text-sm font-700 text-navy-900">Notifications</p>
                <span className="rounded-full bg-royal-100 px-2 py-0.5 text-[11px] font-600 text-royal-700">
                  2 new
                </span>
              </div>
              <div className="space-y-1">
                {NOTIFICATIONS.map((n) => (
                  <div
                    key={n.title}
                    className="flex gap-3 rounded-xl px-3 py-2.5 transition-colors hover:bg-navy-50"
                  >
                    <span
                      className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${
                        n.unread ? 'bg-royal-500' : 'bg-navy-200'
                      }`}
                    />
                    <div className="min-w-0">
                      <p className="text-[13px] font-600 text-navy-800">{n.title}</p>
                      <p className="text-[12px] text-navy-400">{n.time}</p>
                    </div>
                  </div>
                ))}
              </div>
              <button className="mt-1 w-full rounded-xl py-2 text-center text-[13px] font-600 text-royal-600 transition-colors hover:bg-royal-50">
                View all notifications
              </button>
            </div>
          )}
        </div>

        {/* Settings */}
        <button
          className="rounded-xl p-2.5 text-navy-600 transition-all duration-200 hover:bg-navy-50 hover:text-navy-900"
          aria-label="Settings"
        >
          <Settings className="h-5 w-5" />
        </button>

        {/* Profile */}
        <div className="relative ml-1" ref={profileRef}>
          <button
            onClick={() => {
              setProfileOpen((o) => !o);
              setNotifOpen(false);
            }}
            className="flex items-center gap-2.5 rounded-xl py-1.5 pl-1.5 pr-2 transition-all duration-200 hover:bg-navy-50"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-royal-500 to-royal-700 text-[13px] font-700 text-white shadow-card">
              {initials}
            </div>
            <div className="hidden text-left sm:block">
              <p className="text-[13px] font-700 leading-tight text-navy-900">{user?.name}</p>
              <p className="text-[11px] font-500 leading-tight text-navy-400">{user?.role}</p>
            </div>
            <ChevronDown className="hidden h-4 w-4 text-navy-400 sm:block" />
          </button>

          {profileOpen && (
            <div className="absolute right-0 mt-2 w-60 origin-top-right rounded-2xl border border-navy-100 bg-white p-2 shadow-container animate-scale-in">
              <div className="flex items-center gap-3 rounded-xl px-3 py-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-royal-500 to-royal-700 text-sm font-700 text-white">
                  {initials}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-700 text-navy-900">{user?.name}</p>
                  <p className="truncate text-[12px] text-navy-400">{user?.email}</p>
                </div>
              </div>
              <div className="my-1 h-px bg-navy-100" />
              <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-600 text-navy-700 transition-colors hover:bg-navy-50">
                <UserCircle className="h-[18px] w-[18px] text-navy-400" />
                My Profile
              </button>
              <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-600 text-navy-700 transition-colors hover:bg-navy-50">
                <HelpCircle className="h-[18px] w-[18px] text-navy-400" />
                Help & Support
              </button>
              <div className="my-1 h-px bg-navy-100" />
              <button
                onClick={signOut}
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-600 text-red-600 transition-colors hover:bg-red-50"
              >
                <LogOut className="h-[18px] w-[18px]" />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

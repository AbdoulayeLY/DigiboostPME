/**
 * Header principal de l'application
 */
import { User, LogOut, Wifi, WifiOff, Menu } from 'lucide-react';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useNetworkStatus } from '@/hooks/useNetworkStatus';
import { APP_NAME } from '@/lib/constants';

interface HeaderProps {
  onMenuClick?: () => void;
}

export const Header = ({ onMenuClick }: HeaderProps) => {
  const { user, logout } = useAuth();
  const { isOnline } = useNetworkStatus();

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6">
        {/* Logo + Menu Burger */}
        <div className="flex items-center gap-3">
          {/* Menu burger (visible sur mobile seulement) */}
          <button
            onClick={onMenuClick}
            className="md:hidden p-2 hover:bg-gray-100 rounded-md transition-colors"
            aria-label="Toggle menu"
          >
            <Menu className="w-6 h-6 text-gray-700" />
          </button>
          <h1 className="text-lg sm:text-xl font-bold text-indigo-600">{APP_NAME}</h1>
        </div>

        {/* Right side: Network status + User info + Logout */}
        <div className="flex items-center gap-4">
          {/* Network indicator */}
          <div className="flex items-center gap-2">
            {isOnline ? (
              <div className="flex items-center gap-1 text-green-600">
                <Wifi size={18} />
                <span className="text-sm hidden sm:inline">En ligne</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-red-600">
                <WifiOff size={18} />
                <span className="text-sm hidden sm:inline">Hors ligne</span>
              </div>
            )}
          </div>

          {/* User info */}
          <div className="flex items-center gap-2 text-gray-700">
            <User size={18} />
            <div className="hidden sm:block">
              <p className="text-sm font-medium">
                {user?.full_name || user?.email}
              </p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
          </div>

          {/* Logout button */}
          <button
            onClick={logout}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:text-red-600 hover:bg-gray-100 rounded-md transition-colors"
            title="Se deconnecter"
          >
            <LogOut size={18} />
            <span className="hidden sm:inline">Deconnexion</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;

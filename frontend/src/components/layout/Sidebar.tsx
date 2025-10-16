/**
 * Sidebar avec navigation principale
 */
import { NavLink } from 'react-router-dom';
import { X } from 'lucide-react';
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Users,
  TrendingUp,
  AlertCircle,
  Settings,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
  badge?: number;
}

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

const navigationItems: NavItem[] = [
  {
    name: 'Dashboard',
    path: '/dashboard',
    icon: <LayoutDashboard size={20} />,
  },
  {
    name: 'Produits',
    path: '/produits',
    icon: <Package size={20} />,
  },
  {
    name: 'Ventes',
    path: '/ventes',
    icon: <ShoppingCart size={20} />,
  },
  {
    name: 'Fournisseurs',
    path: '/fournisseurs',
    icon: <Users size={20} />,
  },
  {
    name: 'Previsions',
    path: '/previsions',
    icon: <TrendingUp size={20} />,
  },
  {
    name: 'Alertes',
    path: '/alertes',
    icon: <AlertCircle size={20} />,
  },
  {
    name: 'Parametres',
    path: '/parametres',
    icon: <Settings size={20} />,
  },
];

export const Sidebar = ({ isOpen = false, onClose }: SidebarProps) => {
  return (
    <>
      {/* Overlay pour mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'bg-white border-r border-gray-200 h-[calc(100vh-4rem)] overflow-y-auto transition-transform duration-300 ease-in-out z-30',
          // Desktop: toujours visible
          'md:w-64 md:relative md:translate-x-0',
          // Mobile: drawer depuis la gauche
          'fixed left-0 top-16 w-64',
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        )}
      >
        {/* Bouton fermer (mobile seulement) */}
        <div className="md:hidden flex justify-end p-4">
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-md"
            aria-label="Close menu"
          >
            <X className="w-5 h-5 text-gray-700" />
          </button>
        </div>

        <nav className="p-4 space-y-1">
          {navigationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-indigo-50 text-indigo-600'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-indigo-600'
                )
              }
            >
              {item.icon}
              <span>{item.name}</span>
              {item.badge !== undefined && (
                <span className="ml-auto bg-red-500 text-white text-xs rounded-full px-2 py-0.5">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;

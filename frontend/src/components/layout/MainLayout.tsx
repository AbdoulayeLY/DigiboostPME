/**
 * Layout principal de l'application
 * Combine Header + Sidebar + Zone de contenu
 */
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export const MainLayout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header fixe en haut */}
      <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      {/* Container flex pour Sidebar + Content */}
      <div className="flex relative">
        {/* Sidebar */}
        <Sidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Zone de contenu principale */}
        <main className="flex-1 p-3 sm:p-4 md:p-6 overflow-auto w-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default MainLayout;

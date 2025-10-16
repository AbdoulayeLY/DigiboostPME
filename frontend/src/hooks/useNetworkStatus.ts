/**
 * Hook pour detecter le statut de la connexion reseau
 */
import { useEffect, useState } from 'react';

export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState<boolean>(
    typeof navigator !== 'undefined' ? navigator.onLine : true
  );

  useEffect(() => {
    // Gestionnaires d'evenements
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    // Ecouter les changements de statut reseau
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Nettoyage
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return { isOnline };
};

export default useNetworkStatus;

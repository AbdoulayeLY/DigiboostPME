/**
 * ImportProgressTracker - Composant de suivi de progression d'import
 *
 * Sprint 3: Polling status avec affichage progression temps réel
 */
import { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, XCircle, Package, ShoppingCart } from 'lucide-react';
import { getImportStatus, type ImportStatusResponse } from '@/api/onboarding';

interface ImportProgressTrackerProps {
  importJobId: string;
  onComplete: (productsCount: number, salesCount: number) => void;
  onError: (error: string) => void;
}

export const ImportProgressTracker = ({
  importJobId,
  onComplete,
  onError,
}: ImportProgressTrackerProps) => {
  const [status, setStatus] = useState<ImportStatusResponse | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval> | null = null;

    const pollStatus = async () => {
      try {
        const response = await getImportStatus(importJobId);
        setStatus(response);

        // Arrêter le polling si terminé ou échoué
        if (response.status === 'success' || response.status === 'failed') {
          setIsPolling(false);

          if (response.status === 'success') {
            onComplete(
              response.stats.products_imported || 0,
              response.stats.sales_imported || 0
            );
          } else {
            const errorMsg =
              response.error_details?.errors?.[0]?.message ||
              "L'import a échoué";
            onError(errorMsg);
          }
        }
      } catch (error) {
        console.error('Erreur polling status:', error);
        setIsPolling(false);
        onError('Erreur lors de la récupération du statut');
      }
    };

    // Polling toutes les 2 secondes
    if (isPolling) {
      pollStatus(); // Appel initial immédiat
      intervalId = setInterval(pollStatus, 2000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [importJobId, isPolling, onComplete, onError]);

  if (!status) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="animate-spin h-8 w-8 text-indigo-600" />
      </div>
    );
  }

  const isRunning = status.status === 'running' || status.status === 'pending';
  const isSuccess = status.status === 'success';
  const isFailed = status.status === 'failed';

  return (
    <div className="space-y-6">
      {/* Header Status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {isRunning && (
            <Loader2 className="animate-spin h-6 w-6 text-indigo-600" />
          )}
          {isSuccess && <CheckCircle2 className="h-6 w-6 text-green-600" />}
          {isFailed && <XCircle className="h-6 w-6 text-red-600" />}

          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {isRunning && 'Import en cours...'}
              {isSuccess && 'Import terminé avec succès!'}
              {isFailed && "Échec de l'import"}
            </h3>
            <p className="text-sm text-gray-600">{status.file_name}</p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-2xl font-bold text-indigo-600">
            {status.progress_percent}%
          </div>
          <div className="text-xs text-gray-500">Progression</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="relative">
        <div className="overflow-hidden h-4 text-xs flex rounded-full bg-gray-200">
          <div
            style={{ width: `${status.progress_percent}%` }}
            className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center transition-all duration-500 ${
              isSuccess
                ? 'bg-green-500'
                : isFailed
                ? 'bg-red-500'
                : 'bg-indigo-600'
            }`}
          ></div>
        </div>
      </div>

      {/* Current Message */}
      {status.stats.current_message && isRunning && (
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
          <p className="text-sm text-indigo-900 flex items-center gap-2">
            <Loader2 className="animate-spin h-4 w-4" />
            {status.stats.current_message}
          </p>
        </div>
      )}

      {/* Statistics */}
      {(status.stats.products_imported !== undefined ||
        status.stats.sales_imported !== undefined) && (
        <div className="grid grid-cols-2 gap-4">
          {/* Produits */}
          {status.stats.products_imported !== undefined && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Package className="h-6 w-6 text-indigo-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {status.stats.products_imported}
                  </div>
                  <div className="text-sm text-gray-600">Produits importés</div>
                </div>
              </div>
            </div>
          )}

          {/* Ventes */}
          {status.stats.sales_imported !== undefined && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <ShoppingCart className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {status.stats.sales_imported}
                  </div>
                  <div className="text-sm text-gray-600">Ventes importées</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error Details */}
      {isFailed && status.error_details && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-red-900 mb-2">
            Erreurs détectées:
          </h4>

          {status.error_details.errors && status.error_details.errors.length > 0 && (
            <div className="space-y-2">
              {status.error_details.errors.slice(0, 5).map((error, index) => (
                <div key={index} className="text-sm text-red-800">
                  <div className="font-medium">
                    {error.sheet && `[${error.sheet}`}
                    {error.row && ` - Ligne ${error.row}`}
                    {error.column && ` - Colonne ${error.column}`}
                    {error.sheet && ']'}
                  </div>
                  <div className="ml-2">• {error.message}</div>
                  {error.value !== undefined && (
                    <div className="ml-4 text-xs text-red-600">
                      Valeur: {String(error.value)}
                    </div>
                  )}
                </div>
              ))}

              {status.error_details.errors.length > 5 && (
                <p className="text-xs text-red-600 mt-2">
                  ... et {status.error_details.errors.length - 5} autre(s)
                  erreur(s)
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Timestamps */}
      <div className="text-xs text-gray-500 space-y-1">
        {status.started_at && (
          <div>
            Démarré:{' '}
            {new Date(status.started_at).toLocaleString('fr-FR', {
              dateStyle: 'short',
              timeStyle: 'medium',
            })}
          </div>
        )}
        {status.completed_at && (
          <div>
            Terminé:{' '}
            {new Date(status.completed_at).toLocaleString('fr-FR', {
              dateStyle: 'short',
              timeStyle: 'medium',
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default ImportProgressTracker;

/**
 * Composant Historique des Alertes
 * Affiche timeline des déclenchements avec filtres et statistiques
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAlertHistory } from '../hooks/useAlertHistory';
import { Bell, CheckCircle, XCircle, Clock, ArrowLeft } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export const AlertHistory = () => {
  const navigate = useNavigate();
  const [filterType, setFilterType] = useState<string>('');
  const [filterSeverity, setFilterSeverity] = useState<string>('');

  const { data: history, isLoading } = useAlertHistory();

  // Filtrer l'historique
  const filteredHistory = history?.filter((item) => {
    if (filterType && item.alert_type !== filterType) return false;
    if (filterSeverity && item.severity !== filterSeverity) return false;
    return true;
  });

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      LOW: 'bg-blue-100 text-blue-800',
      MEDIUM: 'bg-amber-100 text-amber-800',
      HIGH: 'bg-orange-100 text-orange-800',
      CRITICAL: 'bg-red-100 text-red-800',
    };
    return colors[severity] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return '🚨';
      case 'HIGH':
        return '⚠️';
      case 'MEDIUM':
        return '⚡';
      default:
        return 'ℹ️';
    }
  };

  const getAlertTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      RUPTURE_STOCK: 'Rupture Stock',
      LOW_STOCK: 'Stock Faible',
      BAISSE_TAUX_SERVICE: 'Baisse Taux Service',
    };
    return labels[type] || type;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <button
              onClick={() => navigate('/alertes')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Retour aux alertes"
            >
              <ArrowLeft className="w-5 h-5 text-gray-600" />
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Historique des Alertes</h1>
          </div>
          <p className="text-gray-600 ml-14">
            Consultez l'historique de tous les déclenchements d'alertes
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Déclenchements</p>
              <p className="text-3xl font-bold text-gray-900">{history?.length || 0}</p>
            </div>
            <Bell className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Envoyés WhatsApp</p>
              <p className="text-3xl font-bold text-green-600">
                {history?.filter((h) => h.sent_whatsapp).length || 0}
              </p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alertes Critiques</p>
              <p className="text-3xl font-bold text-red-600">
                {history?.filter((h) => h.severity === 'CRITICAL').length || 0}
              </p>
            </div>
            <XCircle className="w-10 h-10 text-red-500" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Dernière Alerte</p>
              <p className="text-lg font-medium text-gray-900">
                {history?.[0]
                  ? format(new Date(history[0].triggered_at), 'HH:mm', { locale: fr })
                  : '-'}
              </p>
            </div>
            <Clock className="w-10 h-10 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Filtres */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label htmlFor="filter-type" className="block text-sm font-medium text-gray-700 mb-1">
              Type d'alerte
            </label>
            <select
              id="filter-type"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Tous les types</option>
              <option value="RUPTURE_STOCK">Rupture Stock</option>
              <option value="LOW_STOCK">Stock Faible</option>
              <option value="BAISSE_TAUX_SERVICE">Baisse Taux Service</option>
            </select>
          </div>

          <div className="flex-1">
            <label htmlFor="filter-severity" className="block text-sm font-medium text-gray-700 mb-1">
              Sévérité
            </label>
            <select
              id="filter-severity"
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Toutes sévérités</option>
              <option value="LOW">Faible</option>
              <option value="MEDIUM">Moyenne</option>
              <option value="HIGH">Élevée</option>
              <option value="CRITICAL">Critique</option>
            </select>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="space-y-4">
        {filteredHistory && filteredHistory.length > 0 ? (
          filteredHistory.map((item) => (
            <div key={item.id} className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                {/* Icône sévérité */}
                <div className="text-4xl flex-shrink-0">{getSeverityIcon(item.severity)}</div>

                {/* Contenu principal */}
                <div className="flex-1">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg text-gray-900">{item.message}</h3>
                      <div className="flex items-center gap-4 mt-2">
                        <p className="text-sm text-gray-600">
                          {format(new Date(item.triggered_at), "dd MMM yyyy 'à' HH:mm", {
                            locale: fr,
                          })}
                        </p>
                        <span className="text-sm text-gray-400">•</span>
                        <span className="text-sm text-gray-600">{getAlertTypeLabel(item.alert_type)}</span>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ${getSeverityColor(item.severity)}`}>
                      {item.severity}
                    </span>
                  </div>

                  {/* Détails */}
                  {item.details && Object.keys(item.details).length > 0 && (
                    <div className="mt-4 bg-gray-50 p-4 rounded-lg">
                      <p className="text-sm font-medium text-gray-700 mb-3">Détails:</p>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                        {item.details.product_count !== undefined && (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">Produits affectés:</span>
                            <span className="font-semibold text-gray-900">
                              {item.details.product_count}
                            </span>
                          </div>
                        )}
                        {item.details.taux_service !== undefined && (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">Taux service:</span>
                            <span className="font-semibold text-gray-900">
                              {item.details.taux_service}%
                            </span>
                          </div>
                        )}
                        {item.details.total_orders !== undefined && (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">Total commandes:</span>
                            <span className="font-semibold text-gray-900">
                              {item.details.total_orders}
                            </span>
                          </div>
                        )}
                        {item.details.delivered_orders !== undefined && (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-600">Commandes livrées:</span>
                            <span className="font-semibold text-gray-900">
                              {item.details.delivered_orders}
                            </span>
                          </div>
                        )}
                        {item.details.product_names && item.details.product_names.length > 0 && (
                          <div className="col-span-2">
                            <span className="text-gray-600 block mb-2">Produits:</span>
                            <div className="flex flex-wrap gap-2">
                              {item.details.product_names.map((name: string, idx: number) => (
                                <span
                                  key={idx}
                                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                                >
                                  {name}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Statut envoi */}
                  <div className="flex gap-6 mt-4 text-sm">
                    <div className="flex items-center gap-2">
                      {item.sent_whatsapp ? (
                        <>
                          <CheckCircle className="w-5 h-5 text-green-600" />
                          <span className="text-green-600 font-medium">WhatsApp envoyé</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-5 h-5 text-gray-400" />
                          <span className="text-gray-500">WhatsApp non envoyé</span>
                        </>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {item.sent_email ? (
                        <>
                          <CheckCircle className="w-5 h-5 text-green-600" />
                          <span className="text-green-600 font-medium">Email envoyé</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="w-5 h-5 text-gray-400" />
                          <span className="text-gray-500">Email non envoyé</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          /* Empty State */
          <div className="bg-white p-12 rounded-lg shadow text-center">
            <Bell className="w-20 h-20 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun historique</h3>
            <p className="text-gray-600">
              Aucune alerte n'a été déclenchée avec ces filtres
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

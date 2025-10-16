/**
 * Composant principal de gestion des alertes
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, BellOff, Edit, Plus, Trash2, Clock } from 'lucide-react';
import { useAlerts } from '../hooks/useAlerts';
import { AlertConfigDialog } from './AlertConfigDialog';
import type { Alert } from '@/api/alerts';

export const AlertsList = () => {
  const navigate = useNavigate();
  const { alerts, isLoading, deleteAlert, toggleAlert } = useAlerts();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState<Alert | null>(null);

  const getAlertTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      RUPTURE_STOCK: 'Rupture Stock',
      LOW_STOCK: 'Stock Faible',
      BAISSE_TAUX_SERVICE: 'Baisse Taux Service',
    };
    return labels[type] || type;
  };

  const getAlertTypeBadgeClass = (type: string) => {
    const colors: Record<string, string> = {
      RUPTURE_STOCK: 'bg-red-100 text-red-800 border-red-200',
      LOW_STOCK: 'bg-amber-100 text-amber-800 border-amber-200',
      BAISSE_TAUX_SERVICE: 'bg-blue-100 text-blue-800 border-blue-200',
    };
    return colors[type] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const handleEdit = (alert: Alert) => {
    setEditingAlert(alert);
    setIsDialogOpen(true);
  };

  const handleCreate = () => {
    setEditingAlert(null);
    setIsDialogOpen(true);
  };

  const handleDelete = (id: string, name: string) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer l'alerte "${name}" ?`)) {
      deleteAlert(id);
    }
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setEditingAlert(null);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement des alertes...</p>
        </div>
      </div>
    );
  }

  const activeAlerts = alerts.filter((a) => a.is_active).length;
  const inactiveAlerts = alerts.filter((a) => !a.is_active).length;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Alertes</h1>
          <p className="text-gray-600 mt-2">
            Configurez vos alertes pour être notifié en temps réel
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/alertes/history')}
            className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Clock className="w-5 h-5" />
            Historique
          </button>
          <button
            onClick={handleCreate}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Nouvelle Alerte
          </button>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Total Alertes</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{alerts.length}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-lg">
              <Bell className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Alertes Actives</p>
              <p className="text-3xl font-bold text-green-600 mt-1">{activeAlerts}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-lg">
              <Bell className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 font-medium">Alertes Inactives</p>
              <p className="text-3xl font-bold text-gray-400 mt-1">{inactiveAlerts}</p>
            </div>
            <div className="bg-gray-100 p-3 rounded-lg">
              <BellOff className="w-8 h-8 text-gray-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {alerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Aucune alerte configurée
            </h3>
            <p className="text-gray-600 mb-6">
              Créez votre première alerte pour être notifié en temps réel
            </p>
            <button
              onClick={handleCreate}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
              Créer une alerte
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Nom
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Canaux
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Destinataires
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">{alert.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-medium rounded-md border ${getAlertTypeBadgeClass(
                          alert.alert_type
                        )}`}
                      >
                        {getAlertTypeLabel(alert.alert_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex gap-2">
                        {alert.channels.whatsapp && (
                          <span className="inline-flex px-2 py-1 text-xs font-medium rounded-md border bg-green-50 text-green-700 border-green-200">
                            WhatsApp
                          </span>
                        )}
                        {alert.channels.email && (
                          <span className="inline-flex px-2 py-1 text-xs font-medium rounded-md border bg-blue-50 text-blue-700 border-blue-200">
                            Email
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {alert.recipients.whatsapp_numbers?.length || 0} WhatsApp
                      {alert.recipients.emails?.length > 0 &&
                        `, ${alert.recipients.emails.length} Email`}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={alert.is_active}
                          onChange={() => toggleAlert(alert.id)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => handleEdit(alert)}
                          className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(alert.id, alert.name)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Dialog création/modification */}
      <AlertConfigDialog
        open={isDialogOpen}
        onOpenChange={handleDialogClose}
        alert={editingAlert}
      />
    </div>
  );
};

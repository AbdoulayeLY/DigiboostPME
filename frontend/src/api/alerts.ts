/**
 * API Client pour la gestion des alertes
 */
import { apiClient } from './client';

// Types
export interface Alert {
  id: string;
  tenant_id: string;
  name: string;
  alert_type: 'RUPTURE_STOCK' | 'LOW_STOCK' | 'BAISSE_TAUX_SERVICE';
  conditions: Record<string, any>;
  channels: {
    whatsapp: boolean;
    email: boolean;
  };
  recipients: {
    whatsapp_numbers: string[];
    emails: string[];
  };
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AlertCreate {
  name: string;
  alert_type: 'RUPTURE_STOCK' | 'LOW_STOCK' | 'BAISSE_TAUX_SERVICE';
  conditions: Record<string, any>;
  channels: {
    whatsapp: boolean;
    email: boolean;
  };
  recipients: {
    whatsapp_numbers: string[];
    emails: string[];
  };
  is_active?: boolean;
}

export interface AlertUpdate {
  name?: string;
  alert_type?: 'RUPTURE_STOCK' | 'LOW_STOCK' | 'BAISSE_TAUX_SERVICE';
  conditions?: Record<string, any>;
  channels?: {
    whatsapp?: boolean;
    email?: boolean;
  };
  recipients?: {
    whatsapp_numbers?: string[];
    emails?: string[];
  };
  is_active?: boolean;
}

export interface AlertHistory {
  id: string;
  alert_id: string;
  tenant_id: string;
  triggered_at: string;
  alert_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  details: Record<string, any>;
  sent_whatsapp: boolean;
  sent_email: boolean;
  created_at: string;
}

export interface AlertTestResult {
  success: boolean;
  alert_id: string;
  alert_name: string;
  history_id: string;
  sent_whatsapp: boolean;
  sent_email: boolean;
}

export interface AlertHistoryFilters {
  alert_id?: string;
  alert_type?: string;
  severity?: string;
  limit?: number;
  offset?: number;
}

/**
 * API Client pour les alertes
 */
export const alertsApi = {
  /**
   * Liste toutes les alertes configurées
   */
  list: async (): Promise<Alert[]> => {
    const { data } = await apiClient.get('/alerts/');
    return data;
  },

  /**
   * Récupère une alerte par son ID
   */
  get: async (id: string): Promise<Alert> => {
    const { data } = await apiClient.get(`/alerts/${id}`);
    return data;
  },

  /**
   * Crée une nouvelle alerte
   */
  create: async (alert: AlertCreate): Promise<Alert> => {
    const { data } = await apiClient.post('/alerts/', alert);
    return data;
  },

  /**
   * Met à jour une alerte existante
   */
  update: async (id: string, alert: AlertUpdate): Promise<Alert> => {
    const { data} = await apiClient.put(`/alerts/${id}`, alert);
    return data;
  },

  /**
   * Supprime une alerte
   */
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/alerts/${id}`);
  },

  /**
   * Active/désactive une alerte (toggle)
   */
  toggle: async (id: string): Promise<Alert> => {
    const { data } = await apiClient.patch(`/alerts/${id}/toggle`);
    return data;
  },

  /**
   * Teste manuellement une alerte (déclenche sans conditions)
   */
  test: async (id: string): Promise<AlertTestResult> => {
    const { data } = await apiClient.post(`/alerts/${id}/test`);
    return data;
  },

  /**
   * Récupère l'historique des déclenchements
   */
  getHistory: async (params?: {
    alert_id?: string;
    alert_type?: string;
    severity?: string;
    limit?: number;
    offset?: number;
  }): Promise<AlertHistory[]> => {
    const { data } = await apiClient.get('/alerts/history/', { params });
    return data;
  },
};

/**
 * Service API pour le Wizard d'Onboarding Admin
 *
 * Sprint 3: Frontend wizard pour création de tenants
 */
import { apiClient } from './client';

// ============================================================================
// TYPES
// ============================================================================

export interface CreateTenantRequest {
  name: string; // Nom de l'entreprise (backend expects 'name', not 'company_name')
  email: string;
  phone?: string;
  whatsapp_number?: string;
  site_name: string;
  site_address?: string;
}

export interface CreateTenantResponse {
  tenant_id: string;
  site_id: string;
  session_id: string;
  message: string;
}

export interface CreateUserData {
  email?: string;
  phone?: string; // Backend uses 'phone' not just 'whatsapp_number'
  whatsapp_number?: string;
  first_name: string; // Backend requires first_name + last_name, not full_name
  last_name: string;
  role: 'admin' | 'user' | 'viewer'; // Backend only accepts these roles
  default_password: string;
  must_change_password?: boolean;
}

export interface CreateUsersRequest {
  tenant_id: string;
  users: CreateUserData[];
}

export interface UserCreationResponse {
  user_id: string; // Backend returns 'user_id' not 'id'
  email?: string;
  phone?: string;
  first_name: string;
  last_name: string;
  role: string;
  must_change_password: boolean;
}

export interface UsersCreationResponse {
  tenant_id: string;
  users_created: UserCreationResponse[];
  count: number;
}

export interface ImportJobResponse {
  job_id: string;
  celery_task_id: string;
  tenant_id: string;
  status: string;
  message: string;
}

export interface ImportStatusResponse {
  job_id: string;
  tenant_id: string;
  status: 'pending' | 'running' | 'success' | 'failed';
  progress_percent: number;
  file_name: string;
  stats: {
    products_imported?: number;
    sales_imported?: number;
    current_message?: string;
    [key: string]: unknown;
  };
  error_details?: {
    errors?: Array<{
      code: string;
      sheet?: string;
      row?: number;
      column?: string;
      message: string;
      value?: unknown;
    }>;
    warnings?: Array<{
      sheet?: string;
      row?: number;
      column?: string;
      message: string;
      value?: unknown;
    }>;
    [key: string]: unknown;
  };
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Étape 1: Créer un nouveau tenant avec son site principal
 */
export const createTenant = async (
  data: CreateTenantRequest
): Promise<CreateTenantResponse> => {
  const response = await apiClient.post<CreateTenantResponse>(
    '/admin/onboarding/create-tenant',
    data
  );
  return response.data;
};

/**
 * Étape 2: Créer des utilisateurs pour un tenant
 */
export const createUsers = async (
  data: CreateUsersRequest
): Promise<UsersCreationResponse> => {
  const response = await apiClient.post<UsersCreationResponse>(
    '/admin/onboarding/create-users',
    data
  );
  return response.data;
};

/**
 * Étape 3: Générer et télécharger le template Excel
 */
export const generateTemplate = async (
  tenantId: string,
  options?: {
    includeCategories?: boolean;
    includeSuppliers?: boolean;
    sampleData?: boolean;
  }
): Promise<Blob> => {
  const params = new URLSearchParams();

  if (options?.includeCategories !== undefined) {
    params.append('include_categories', options.includeCategories.toString());
  }
  if (options?.includeSuppliers !== undefined) {
    params.append('include_suppliers', options.includeSuppliers.toString());
  }
  if (options?.sampleData !== undefined) {
    params.append('sample_data', options.sampleData.toString());
  }

  const response = await apiClient.get(
    `/admin/onboarding/generate-template/${tenantId}?${params.toString()}`,
    {
      responseType: 'blob',
    }
  );

  return response.data;
};

/**
 * Étape 4: Upload et import du fichier Excel
 */
export const uploadTemplate = async (
  tenantId: string,
  file: File
): Promise<ImportJobResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<ImportJobResponse>(
    `/admin/onboarding/upload-template/${tenantId}`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      // Timeout plus long pour l'upload
      timeout: 120000, // 2 minutes
    }
  );

  return response.data;
};

/**
 * Polling: Récupérer le statut d'un import en cours
 */
export const getImportStatus = async (
  importJobId: string
): Promise<ImportStatusResponse> => {
  const response = await apiClient.get<ImportStatusResponse>(
    `/admin/onboarding/import-status/${importJobId}`
  );
  return response.data;
};

/**
 * Helper: Télécharger le template Excel
 */
export const downloadTemplate = async (
  tenantId: string,
  filename?: string
): Promise<void> => {
  const blob = await generateTemplate(tenantId, {
    includeCategories: true,
    includeSuppliers: true,
    sampleData: true,
  });

  // Créer un lien de téléchargement
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || `template_digiboost_${tenantId}.xlsx`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export default {
  createTenant,
  createUsers,
  generateTemplate,
  uploadTemplate,
  getImportStatus,
  downloadTemplate,
};

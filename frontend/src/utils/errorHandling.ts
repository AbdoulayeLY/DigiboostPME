/**
 * Utility pour gérer les erreurs de manière centralisée
 * Sprint 4 - Error Handling robuste
 */
import { toast } from 'sonner';
import type { AxiosError } from 'axios';

/**
 * Structure d'erreur API standardisée
 */
export interface ApiErrorResponse {
  error?: string;
  message: string;
  details?: unknown;
  technical_details?: string;
  retry_after?: number;
  request_id?: string | number;
}

/**
 * Types d'erreurs connues
 */
export const ErrorType = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INTEGRITY_ERROR: 'INTEGRITY_ERROR',
  DATABASE_ERROR: 'DATABASE_ERROR',
  TASK_TIMEOUT: 'TASK_TIMEOUT',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  INVALID_FILE_TYPE: 'INVALID_FILE_TYPE',
  FILE_UPLOAD_ERROR: 'FILE_UPLOAD_ERROR',
  BUSINESS_VALIDATION_ERROR: 'BUSINESS_VALIDATION_ERROR',
  INTERNAL_SERVER_ERROR: 'INTERNAL_SERVER_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
} as const;

/**
 * Messages d'erreur user-friendly par type
 */
const ERROR_MESSAGES: Record<string, string> = {
  [ErrorType.VALIDATION_ERROR]: 'Les données fournies sont invalides',
  [ErrorType.INTEGRITY_ERROR]: 'Cette entrée existe déjà ou viole une contrainte',
  [ErrorType.DATABASE_ERROR]: 'Service temporairement indisponible',
  [ErrorType.TASK_TIMEOUT]: 'L\'opération prend plus de temps que prévu',
  [ErrorType.FILE_TOO_LARGE]: 'Le fichier est trop volumineux',
  [ErrorType.INVALID_FILE_TYPE]: 'Le type de fichier n\'est pas accepté',
  [ErrorType.FILE_UPLOAD_ERROR]: 'Erreur lors de l\'upload du fichier',
  [ErrorType.BUSINESS_VALIDATION_ERROR]: 'Règle métier violée',
  [ErrorType.INTERNAL_SERVER_ERROR]: 'Erreur serveur inattendue',
  [ErrorType.NETWORK_ERROR]: 'Erreur de connexion au serveur',
  [ErrorType.UNAUTHORIZED]: 'Authentification requise',
  [ErrorType.FORBIDDEN]: 'Accès non autorisé',
  [ErrorType.NOT_FOUND]: 'Ressource non trouvée',
};

/**
 * Extrait le message d'erreur d'une réponse Axios
 */
export function extractErrorMessage(error: unknown): string {
  if (!error) {
    return 'Erreur inconnue';
  }

  // Erreur Axios
  if (isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;

    // Pas de réponse (erreur réseau)
    if (!axiosError.response) {
      return ERROR_MESSAGES[ErrorType.NETWORK_ERROR];
    }

    const { status, data } = axiosError.response;

    // Erreurs HTTP standards
    if (status === 401) {
      return data?.message || ERROR_MESSAGES[ErrorType.UNAUTHORIZED];
    }
    if (status === 403) {
      return data?.message || ERROR_MESSAGES[ErrorType.FORBIDDEN];
    }
    if (status === 404) {
      return data?.message || ERROR_MESSAGES[ErrorType.NOT_FOUND];
    }

    // Erreur avec structure standardisée
    if (data?.error && ERROR_MESSAGES[data.error]) {
      return data.message || ERROR_MESSAGES[data.error];
    }

    // Message custom de l'API
    if (data?.message) {
      return data.message;
    }

    // Detail (format FastAPI)
    if (data && typeof data === 'object' && 'detail' in data) {
      const detail = (data as { detail: unknown }).detail;
      if (typeof detail === 'string') {
        return detail;
      }
    }

    // Fallback basé sur status
    if (status >= 500) {
      return ERROR_MESSAGES[ErrorType.INTERNAL_SERVER_ERROR];
    }
    if (status >= 400) {
      return 'Requête invalide';
    }
  }

  // Erreur standard JavaScript
  if (error instanceof Error) {
    return error.message;
  }

  // Objet avec propriété message
  if (typeof error === 'object' && 'message' in error) {
    const msg = (error as { message: unknown }).message;
    if (typeof msg === 'string') {
      return msg;
    }
  }

  // String directe
  if (typeof error === 'string') {
    return error;
  }

  return 'Erreur inconnue';
}

/**
 * Type guard pour vérifier si c'est une erreur Axios
 */
function isAxiosError(error: unknown): error is AxiosError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'isAxiosError' in error &&
    (error as AxiosError).isAxiosError === true
  );
}

/**
 * Extrait les détails d'erreur de validation
 */
export function extractValidationErrors(
  error: unknown
): Array<{ field: string; message: string }> | null {
  if (!isAxiosError(error)) {
    return null;
  }

  const axiosError = error as AxiosError<ApiErrorResponse>;
  const data = axiosError.response?.data;

  if (!data || !data.details || typeof data.details !== 'object') {
    return null;
  }

  const details = data.details as unknown;

  // Format backend error_handlers.py
  if (Array.isArray(details)) {
    return details
      .filter((item): item is { field: string; message: string } =>
        typeof item === 'object' &&
        item !== null &&
        'field' in item &&
        'message' in item &&
        typeof item.field === 'string' &&
        typeof item.message === 'string'
      );
  }

  return null;
}

/**
 * Affiche une erreur avec toast
 */
export function showError(error: unknown, customMessage?: string): void {
  const message = customMessage || extractErrorMessage(error);
  const validationErrors = extractValidationErrors(error);

  if (validationErrors && validationErrors.length > 0) {
    // Afficher erreurs de validation
    toast.error('Erreurs de validation', {
      description: validationErrors.map((e) => `${e.field}: ${e.message}`).join('\n'),
      duration: 5000,
    });
  } else {
    // Erreur simple
    toast.error('Erreur', {
      description: message,
      duration: 4000,
    });
  }
}

/**
 * Gère une erreur de manière centralisée
 * - Log dans la console (dev)
 * - Affiche un toast user-friendly
 * - Retourne le message pour usage custom
 */
export function handleError(
  error: unknown,
  context?: string,
  showToast = true
): string {
  // Log détaillé en développement
  if (import.meta.env.DEV) {
    console.error(`[Error${context ? ` - ${context}` : ''}]:`, error);
  }

  const message = extractErrorMessage(error);

  // Afficher toast si demandé
  if (showToast) {
    showError(error);
  }

  return message;
}

/**
 * Wrapper pour les appels API avec gestion d'erreur automatique
 */
export async function withErrorHandling<T>(
  apiCall: () => Promise<T>,
  options?: {
    context?: string;
    showToast?: boolean;
    successMessage?: string;
    onError?: (error: unknown) => void;
  }
): Promise<T | null> {
  try {
    const result = await apiCall();

    // Afficher message de succès si fourni
    if (options?.successMessage) {
      toast.success(options.successMessage);
    }

    return result;
  } catch (error) {
    handleError(error, options?.context, options?.showToast ?? true);

    // Callback custom en cas d'erreur
    if (options?.onError) {
      options.onError(error);
    }

    return null;
  }
}

/**
 * Retry logic pour les erreurs temporaires
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    shouldRetry?: (error: unknown) => boolean;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    shouldRetry = (error) => {
      // Retry sur erreurs réseau ou 5xx
      if (isAxiosError(error)) {
        const status = error.response?.status;
        return !status || status >= 500;
      }
      return false;
    },
  } = options;

  let lastError: unknown;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Dernier essai
      if (attempt === maxRetries) {
        break;
      }

      // Vérifier si on doit retry
      if (!shouldRetry(error)) {
        break;
      }

      // Attendre avant retry
      await new Promise((resolve) => setTimeout(resolve, delay));

      // Backoff exponentiel
      delay = Math.min(delay * 2, maxDelay);
    }
  }

  throw lastError;
}

export default {
  extractErrorMessage,
  extractValidationErrors,
  showError,
  handleError,
  withErrorHandling,
  retryWithBackoff,
};

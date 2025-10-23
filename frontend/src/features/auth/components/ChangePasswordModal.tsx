/**
 * ChangePasswordModal - Modal pour changement de mot de passe forcé
 *
 * Sprint 3: Affiché au premier login si must_change_password=true
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Lock, Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react';
import { authApi } from '@/api/auth';
import { toast } from 'sonner';
import type { ChangePasswordFirstLoginRequest } from '@/types/api.types';

interface ChangePasswordModalProps {
  tempToken: string;
  onSuccess: (accessToken: string, refreshToken: string) => void;
  email: string;
}

interface FormData extends ChangePasswordFirstLoginRequest {
  confirm_password: string;
}

export const ChangePasswordModal = ({
  tempToken,
  onSuccess,
  email,
}: ChangePasswordModalProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showOldPassword, setShowOldPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormData>();

  const newPassword = watch('new_password');

  const validatePasswordStrength = (password: string): string | true => {
    if (password.length < 8) {
      return 'Le mot de passe doit contenir au moins 8 caractères';
    }
    if (!/[A-Z]/.test(password)) {
      return 'Le mot de passe doit contenir au moins une majuscule';
    }
    if (!/[a-z]/.test(password)) {
      return 'Le mot de passe doit contenir au moins une minuscule';
    }
    if (!/[0-9]/.test(password)) {
      return 'Le mot de passe doit contenir au moins un chiffre';
    }
    return true;
  };

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);

    try {
      const response = await authApi.changePasswordFirstLogin(
        {
          old_password: data.old_password,
          new_password: data.new_password,
        },
        tempToken
      );

      toast.success('Mot de passe changé avec succès!', {
        description: 'Vous pouvez maintenant accéder à votre compte',
      });

      // Appeler onSuccess avec les nouveaux tokens
      onSuccess(response.access_token, response.refresh_token);
    } catch (error: unknown) {
      console.error('Erreur changement mot de passe:', error);

      const errorMessage =
        error && typeof error === 'object' && 'response' in error
          ? (error as { response?: { data?: { detail?: string } } }).response
              ?.data?.detail || 'Erreur lors du changement de mot de passe'
          : 'Erreur lors du changement de mot de passe';

      toast.error('Échec du changement', {
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-amber-100 mb-3">
            <Lock className="w-6 h-6 text-amber-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            Changement de Mot de Passe Requis
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Pour des raisons de sécurité, vous devez changer votre mot de passe
            par défaut avant d'accéder à l'application.
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Connecté en tant que: <strong>{email}</strong>
          </p>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-6">
          <div className="flex gap-2">
            <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-1">Exigences du mot de passe:</p>
              <ul className="space-y-1 text-xs">
                <li>• Minimum 8 caractères</li>
                <li>• Au moins une majuscule (A-Z)</li>
                <li>• Au moins une minuscule (a-z)</li>
                <li>• Au moins un chiffre (0-9)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Ancien mot de passe */}
          <div>
            <label
              htmlFor="old_password"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Ancien mot de passe <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type={showOldPassword ? 'text' : 'password'}
                id="old_password"
                {...register('old_password', {
                  required: 'Ancien mot de passe obligatoire',
                })}
                className={`block w-full rounded-md shadow-sm pr-10 sm:text-sm ${
                  errors.old_password
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                }`}
                placeholder="Mot de passe par défaut"
              />
              <button
                type="button"
                onClick={() => setShowOldPassword(!showOldPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showOldPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
            {errors.old_password && (
              <p className="mt-1 text-sm text-red-600">
                {errors.old_password.message}
              </p>
            )}
          </div>

          {/* Nouveau mot de passe */}
          <div>
            <label
              htmlFor="new_password"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Nouveau mot de passe <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type={showNewPassword ? 'text' : 'password'}
                id="new_password"
                {...register('new_password', {
                  required: 'Nouveau mot de passe obligatoire',
                  validate: validatePasswordStrength,
                })}
                className={`block w-full rounded-md shadow-sm pr-10 sm:text-sm ${
                  errors.new_password
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                }`}
                placeholder="Nouveau mot de passe sécurisé"
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(!showNewPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showNewPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
            {errors.new_password && (
              <p className="mt-1 text-sm text-red-600">
                {errors.new_password.message}
              </p>
            )}
          </div>

          {/* Confirmer nouveau mot de passe */}
          <div>
            <label
              htmlFor="confirm_password"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Confirmer le nouveau mot de passe{' '}
              <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirm_password"
                {...register('confirm_password', {
                  required: 'Confirmation obligatoire',
                  validate: (value) =>
                    value === newPassword ||
                    'Les mots de passe ne correspondent pas',
                })}
                className={`block w-full rounded-md shadow-sm pr-10 sm:text-sm ${
                  errors.confirm_password
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                }`}
                placeholder="Retaper le nouveau mot de passe"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                {showConfirmPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
            {errors.confirm_password && (
              <p className="mt-1 text-sm text-red-600">
                {errors.confirm_password.message}
              </p>
            )}
          </div>

          {/* Submit Button */}
          <div className="pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Changement en cours...
                </>
              ) : (
                <>
                  <CheckCircle2 className="-ml-1 mr-3 h-5 w-5" />
                  Confirmer le Changement
                </>
              )}
            </button>
          </div>
        </form>

        {/* Footer Note */}
        <p className="mt-4 text-xs text-center text-gray-500">
          Ce modal ne peut pas être fermé. Vous devez changer votre mot de
          passe pour continuer.
        </p>
      </div>
    </div>
  );
};

export default ChangePasswordModal;

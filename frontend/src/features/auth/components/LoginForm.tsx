/**
 * Formulaire de connexion
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/stores/authStore';
import { ChangePasswordModal } from './ChangePasswordModal';
import { toast } from 'sonner';

// Schema de validation avec Zod
const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email requis')
    .email('Email invalide'),
  password: z
    .string()
    .min(6, 'Mot de passe doit contenir au moins 6 caracteres'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm = () => {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [tempToken, setTempToken] = useState<string>('');
  const [userEmail, setUserEmail] = useState<string>('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authApi.login(data);

      // Vérifier si changement de mot de passe requis
      if (response.must_change_password && response.temp_token) {
        setTempToken(response.temp_token);
        setUserEmail(data.email);
        setShowPasswordModal(true);
        toast.info('Changement de mot de passe requis', {
          description: 'Vous devez changer votre mot de passe par défaut',
        });
      } else {
        // Login normal - sauvegarder tokens et récupérer utilisateur
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);

        const userData = await authApi.getCurrentUser();
        setAuth(userData, response.access_token, response.refresh_token);

        navigate('/dashboard');
      }
    } catch (err: unknown) {
      console.error('Erreur login:', err);
      setError(
        'Identifiants incorrects ou erreur de connexion. Veuillez réessayer.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordChangeSuccess = async (
    accessToken: string,
    refreshToken: string
  ) => {
    // Sauvegarder les nouveaux tokens
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);

    // Récupérer l'utilisateur et se connecter
    try {
      const userData = await authApi.getCurrentUser();
      setAuth(userData, accessToken, refreshToken);
      setShowPasswordModal(false);
      navigate('/dashboard');
    } catch (error) {
      console.error('Erreur récupération utilisateur:', error);
      toast.error('Erreur lors de la connexion après changement de mot de passe');
    }
  };

  return (
    <>
      {showPasswordModal && (
        <ChangePasswordModal
          tempToken={tempToken}
          onSuccess={handlePasswordChangeSuccess}
          email={userEmail}
        />
      )}

      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">
            Digiboost PME
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Intelligence Supply Chain pour PME Senegalaises
          </p>
        </div>

        {/* Form */}
        <div className="bg-white py-8 px-6 shadow-lg rounded-lg">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700"
              >
                Adresse email
              </label>
              <input
                {...register('email')}
                type="email"
                id="email"
                autoComplete="email"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="exemple@digiboost.sn"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.email.message}
                </p>
              )}
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700"
              >
                Mot de passe
              </label>
              <input
                {...register('password')}
                type="password"
                id="password"
                autoComplete="current-password"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Error message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                <p className="text-sm">
                  Identifiants incorrects. Veuillez reessayer.
                </p>
              </div>
            )}

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

          {/* Demo credentials */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-500 text-center">
              Comptes de demonstration:
            </p>
            <div className="mt-2 space-y-1 text-xs text-gray-600">
              <p>Admin: admin@digiboost.sn / password123</p>
              <p>Manager: manager@digiboost.sn / password123</p>
              <p>User: user@digiboost.sn / password123</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    </>
  );
};

export default LoginForm;

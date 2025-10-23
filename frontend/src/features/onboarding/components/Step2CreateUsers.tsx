/**
 * Step2CreateUsers - Formulaire de création multi-utilisateurs
 *
 * Sprint 3: Étape 2 du wizard onboarding
 */
import { useState } from 'react';
import { useFieldArray, useForm } from 'react-hook-form';
import {
  UserPlus,
  Trash2,
  Plus,
  Loader2,
  Mail,
  MessageSquare,
  Eye,
  EyeOff,
} from 'lucide-react';
import { createUsers, type CreateUserData } from '@/api/onboarding';
import { toast } from 'sonner';

interface Step2CreateUsersProps {
  tenantId: string;
  onSuccess: (usersCount: number) => void;
  onNext: () => void;
  onBack: () => void;
}

// Type pour le formulaire (garde full_name pour l'UX)
interface FormUserData {
  identifier_type: 'email' | 'whatsapp';
  email?: string;
  whatsapp_number?: string;
  full_name: string;
  role: 'admin' | 'user'; // Simplifié pour l'onboarding
  default_password: string;
  must_change_password?: boolean;
}

interface FormData {
  users: FormUserData[];
}

export const Step2CreateUsers = ({
  tenantId,
  onSuccess,
  onNext,
  onBack,
}: Step2CreateUsersProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showPasswords, setShowPasswords] = useState<Record<number, boolean>>(
    {}
  );

  const {
    register,
    control,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      users: [
        {
          identifier_type: 'email',
          email: '',
          whatsapp_number: '',
          full_name: '',
          role: 'admin',
          default_password: '',
          must_change_password: true,
        },
      ],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'users',
  });

  const togglePasswordVisibility = (index: number) => {
    setShowPasswords((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);

    try {
      // Transformer les données pour l'API
      const usersToCreate: CreateUserData[] = data.users.map((user) => {
        // Séparer le full_name en first_name et last_name
        const nameParts = user.full_name.trim().split(/\s+/);
        const first_name = nameParts[0] || '';
        const last_name = nameParts.slice(1).join(' ') || first_name; // Si un seul mot, utiliser le même pour les deux

        return {
          email: user.identifier_type === 'email' ? user.email : undefined,
          phone: user.identifier_type === 'email' ? undefined : user.whatsapp_number,
          whatsapp_number: user.whatsapp_number || undefined,
          first_name,
          last_name,
          role: user.role, // Role is already 'admin' or 'user'
          default_password: user.default_password,
          must_change_password: user.must_change_password ?? true,
        };
      });

      const response = await createUsers({
        tenant_id: tenantId,
        users: usersToCreate,
      });

      toast.success(`${response.count} utilisateur(s) créé(s) avec succès!`);

      onSuccess(response.count);
      onNext();
    } catch (error: unknown) {
      console.error('Erreur création utilisateurs:', error);

      const errorMessage =
        error && typeof error === 'object' && 'response' in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
            'Erreur lors de la création des utilisateurs'
          : 'Erreur lors de la création des utilisateurs';

      toast.error('Échec de création', {
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <UserPlus className="w-6 h-6 text-indigo-600" />
          Utilisateurs
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Créez de 1 à 10 utilisateurs pour accéder au système
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Liste des utilisateurs */}
        <div className="space-y-6">
          {fields.map((field, index) => {
            const identifierType = watch(`users.${index}.identifier_type`);

            return (
              <div
                key={field.id}
                className="p-5 bg-gray-50 rounded-lg border border-gray-200"
              >
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-sm font-semibold text-gray-900">
                    Utilisateur {index + 1}
                  </h4>
                  {fields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => remove(index)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>

                <div className="space-y-4">
                  {/* Type d'identifiant */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Type d'identifiant <span className="text-red-500">*</span>
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <label className="relative flex items-center justify-center px-4 py-2 border rounded-md cursor-pointer hover:bg-gray-50">
                        <input
                          type="radio"
                          {...register(`users.${index}.identifier_type`, {
                            required: true,
                          })}
                          value="email"
                          className="sr-only"
                        />
                        <Mail className="w-4 h-4 mr-2" />
                        <span className="text-sm font-medium">Email</span>
                        {identifierType === 'email' && (
                          <div className="absolute inset-0 border-2 border-indigo-600 rounded-md pointer-events-none" />
                        )}
                      </label>

                      <label className="relative flex items-center justify-center px-4 py-2 border rounded-md cursor-pointer hover:bg-gray-50">
                        <input
                          type="radio"
                          {...register(`users.${index}.identifier_type`, {
                            required: true,
                          })}
                          value="whatsapp"
                          className="sr-only"
                        />
                        <MessageSquare className="w-4 h-4 mr-2" />
                        <span className="text-sm font-medium">WhatsApp</span>
                        {identifierType === 'whatsapp' && (
                          <div className="absolute inset-0 border-2 border-indigo-600 rounded-md pointer-events-none" />
                        )}
                      </label>
                    </div>
                  </div>

                  {/* Email ou WhatsApp */}
                  {identifierType === 'email' ? (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Email <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="email"
                        {...register(`users.${index}.email`, {
                          required:
                            identifierType === 'email'
                              ? 'Email obligatoire'
                              : false,
                          pattern: {
                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                            message: 'Email invalide',
                          },
                        })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        placeholder="user@example.com"
                      />
                      {errors.users?.[index]?.email && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.users[index]?.email?.message}
                        </p>
                      )}
                    </div>
                  ) : (
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Numéro WhatsApp <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="tel"
                        {...register(`users.${index}.whatsapp_number`, {
                          required:
                            identifierType === 'whatsapp'
                              ? 'Numéro WhatsApp obligatoire'
                              : false,
                          pattern: {
                            value: /^(\+221)?[0-9\s-]{9,15}$/,
                            message: 'Numéro invalide',
                          },
                        })}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        placeholder="+221 77 123 45 67"
                      />
                      {errors.users?.[index]?.whatsapp_number && (
                        <p className="mt-1 text-sm text-red-600">
                          {errors.users[index]?.whatsapp_number?.message}
                        </p>
                      )}
                    </div>
                  )}

                  {/* Nom complet */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Nom complet <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      {...register(`users.${index}.full_name`, {
                        required: 'Nom complet obligatoire',
                        minLength: {
                          value: 2,
                          message: 'Minimum 2 caractères',
                        },
                      })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      placeholder="Ex: Amadou Diallo"
                    />
                    {errors.users?.[index]?.full_name && (
                      <p className="mt-1 text-sm text-red-600">
                        {errors.users[index]?.full_name?.message}
                      </p>
                    )}
                  </div>

                  {/* Rôle */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Rôle <span className="text-red-500">*</span>
                    </label>
                    <select
                      {...register(`users.${index}.role`, {
                        required: 'Rôle obligatoire',
                      })}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    >
                      <option value="admin">Administrateur</option>
                      <option value="user">Utilisateur</option>
                    </select>
                  </div>

                  {/* Mot de passe */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Mot de passe par défaut{' '}
                      <span className="text-red-500">*</span>
                    </label>
                    <div className="relative mt-1">
                      <input
                        type={showPasswords[index] ? 'text' : 'password'}
                        {...register(`users.${index}.default_password`, {
                          required: 'Mot de passe obligatoire',
                          minLength: {
                            value: 8,
                            message: 'Minimum 8 caractères',
                          },
                        })}
                        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm pr-10"
                        placeholder="Minimum 8 caractères"
                      />
                      <button
                        type="button"
                        onClick={() => togglePasswordVisibility(index)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      >
                        {showPasswords[index] ? (
                          <EyeOff className="h-5 w-5 text-gray-400" />
                        ) : (
                          <Eye className="h-5 w-5 text-gray-400" />
                        )}
                      </button>
                    </div>
                    {errors.users?.[index]?.default_password && (
                      <p className="mt-1 text-sm text-red-600">
                        {errors.users[index]?.default_password?.message}
                      </p>
                    )}
                  </div>

                  {/* Forcer changement mot de passe */}
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      {...register(`users.${index}.must_change_password`)}
                      defaultChecked
                      className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    />
                    <label className="ml-2 block text-sm text-gray-700">
                      Forcer le changement de mot de passe à la première
                      connexion
                    </label>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Bouton Ajouter utilisateur */}
        {fields.length < 10 && (
          <button
            type="button"
            onClick={() =>
              append({
                identifier_type: 'email',
                email: '',
                whatsapp_number: '',
                full_name: '',
                role: 'admin',
                default_password: '',
                must_change_password: true,
              })
            }
            className="w-full flex items-center justify-center px-4 py-3 border-2 border-dashed border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:border-indigo-500 hover:text-indigo-600 focus:outline-none"
          >
            <Plus className="w-5 h-5 mr-2" />
            Ajouter un utilisateur ({fields.length}/10)
          </button>
        )}

        {/* Actions */}
        <div className="flex justify-between gap-3 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Retour
          </button>

          <button
            type="submit"
            disabled={isLoading}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                Création en cours...
              </>
            ) : (
              <>Créer et Continuer</>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Step2CreateUsers;

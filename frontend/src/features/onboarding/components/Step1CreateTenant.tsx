/**
 * Step1CreateTenant - Formulaire de création tenant + site
 *
 * Sprint 3: Étape 1 du wizard onboarding
 */
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Building2, MapPin, Mail, Phone, MessageSquare, Loader2 } from 'lucide-react';
import { createTenant, type CreateTenantRequest } from '@/api/onboarding';
import { toast } from 'sonner';

interface Step1CreateTenantProps {
  onSuccess: (tenantId: string, siteId: string, sessionId: string, tenantName: string, siteName: string) => void;
  onNext: () => void;
}

interface FormData extends CreateTenantRequest {}

export const Step1CreateTenant = ({
  onSuccess,
  onNext,
}: Step1CreateTenantProps) => {
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);

    try {
      const response = await createTenant(data);

      toast.success('Tenant créé avec succès!', {
        description: `Entreprise: ${data.name}`,
      });

      // Stocker les IDs et noms pour les étapes suivantes
      onSuccess(
        response.tenant_id,
        response.site_id,
        response.session_id,
        data.name,
        data.site_name
      );

      // Passer à l'étape suivante
      onNext();
    } catch (error: unknown) {
      console.error('Erreur création tenant:', error);

      const errorMessage =
        error && typeof error === 'object' && 'response' in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
            'Erreur lors de la création du tenant'
          : 'Erreur lors de la création du tenant';

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
        <h2 className="text-2xl font-bold text-gray-900">
          Informations Entreprise
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Créez le tenant et configurez le site principal
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Section Entreprise */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-indigo-600" />
            Entreprise
          </h3>

          {/* Nom Entreprise */}
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700"
            >
              Nom de l'entreprise <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="name"
              {...register('name', {
                required: "Le nom de l'entreprise est obligatoire",
                minLength: {
                  value: 2,
                  message: 'Le nom doit contenir au moins 2 caractères',
                },
              })}
              className={`mt-1 block w-full rounded-md shadow-sm sm:text-sm
                ${
                  errors.name
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                }
              `}
              placeholder="Ex: Boutique Thiossane"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">
                {errors.name.message}
              </p>
            )}
          </div>

          {/* Email */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email <span className="text-red-500">*</span>
            </label>
            <div className="relative mt-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="email"
                id="email"
                {...register('email', {
                  required: "L'email est obligatoire",
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Email invalide',
                  },
                })}
                className={`pl-10 block w-full rounded-md shadow-sm sm:text-sm
                  ${
                    errors.email
                      ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                      : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                  }
                `}
                placeholder="contact@thiossane.sn"
              />
            </div>
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          {/* Téléphone */}
          <div>
            <label
              htmlFor="phone"
              className="block text-sm font-medium text-gray-700"
            >
              Téléphone
            </label>
            <div className="relative mt-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Phone className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="tel"
                id="phone"
                {...register('phone', {
                  pattern: {
                    value: /^(\+221)?[0-9\s-]{9,15}$/,
                    message: 'Numéro de téléphone invalide',
                  },
                })}
                className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                placeholder="+221 77 123 45 67"
              />
            </div>
            {errors.phone && (
              <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
            )}
          </div>

          {/* WhatsApp */}
          <div>
            <label
              htmlFor="whatsapp_number"
              className="block text-sm font-medium text-gray-700"
            >
              Numéro WhatsApp
            </label>
            <div className="relative mt-1">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MessageSquare className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="tel"
                id="whatsapp_number"
                {...register('whatsapp_number', {
                  pattern: {
                    value: /^(\+221)?[0-9\s-]{9,15}$/,
                    message: 'Numéro WhatsApp invalide',
                  },
                })}
                className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                placeholder="+221 77 123 45 67"
              />
            </div>
            {errors.whatsapp_number && (
              <p className="mt-1 text-sm text-red-600">
                {errors.whatsapp_number.message}
              </p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Utilisé pour les alertes WhatsApp
            </p>
          </div>
        </div>

        {/* Section Site */}
        <div className="space-y-4 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-indigo-600" />
            Site Principal
          </h3>

          {/* Nom Site */}
          <div>
            <label
              htmlFor="site_name"
              className="block text-sm font-medium text-gray-700"
            >
              Nom du site <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="site_name"
              {...register('site_name', {
                required: 'Le nom du site est obligatoire',
                minLength: {
                  value: 2,
                  message: 'Le nom doit contenir au moins 2 caractères',
                },
              })}
              className={`mt-1 block w-full rounded-md shadow-sm sm:text-sm
                ${
                  errors.site_name
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
                }
              `}
              placeholder="Ex: Boutique Principale"
            />
            {errors.site_name && (
              <p className="mt-1 text-sm text-red-600">
                {errors.site_name.message}
              </p>
            )}
          </div>

          {/* Adresse Site */}
          <div>
            <label
              htmlFor="site_address"
              className="block text-sm font-medium text-gray-700"
            >
              Adresse
            </label>
            <textarea
              id="site_address"
              rows={3}
              {...register('site_address')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
              placeholder="Ex: Marché Sandaga, Avenue Lamine Gueye, Dakar"
            />
            <p className="mt-1 text-xs text-gray-500">
              Adresse physique du site (optionnel)
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
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

export default Step1CreateTenant;

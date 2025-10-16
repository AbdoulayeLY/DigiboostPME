/**
 * Dialog de configuration d'alerte (création/modification)
 */
import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { X } from 'lucide-react';
import { useAlerts } from '../hooks/useAlerts';
import type { Alert } from '@/api/alerts';

const alertSchema = z.object({
  name: z.string().min(3, 'Le nom doit contenir au moins 3 caractères'),
  alert_type: z.enum(['RUPTURE_STOCK', 'LOW_STOCK', 'BAISSE_TAUX_SERVICE']),
  channels: z.object({
    whatsapp: z.boolean(),
    email: z.boolean(),
  }),
  recipients: z.object({
    whatsapp_numbers: z.array(z.string()),
    emails: z.array(z.string()),
  }),
  conditions: z.record(z.string(), z.any()),
  is_active: z.boolean(),
});

type AlertFormData = z.infer<typeof alertSchema>;

interface AlertConfigDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  alert?: Alert | null;
}

export const AlertConfigDialog = ({
  open,
  onOpenChange,
  alert,
}: AlertConfigDialogProps) => {
  const { createAlert, updateAlert, isCreating, isUpdating } = useAlerts();
  const isEditing = !!alert;

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<AlertFormData>({
    resolver: zodResolver(alertSchema),
    defaultValues: {
      name: '',
      alert_type: 'RUPTURE_STOCK',
      channels: { whatsapp: true, email: false },
      recipients: { whatsapp_numbers: [], emails: [] },
      conditions: {},
      is_active: true,
    },
  });

  const watchWhatsApp = watch('channels.whatsapp');
  const watchEmail = watch('channels.email');

  // Charger les données de l'alerte en mode édition
  useEffect(() => {
    if (alert) {
      reset({
        name: alert.name,
        alert_type: alert.alert_type,
        channels: alert.channels,
        recipients: alert.recipients,
        conditions: alert.conditions,
        is_active: alert.is_active,
      });
    } else {
      reset({
        name: '',
        alert_type: 'RUPTURE_STOCK',
        channels: { whatsapp: true, email: false },
        recipients: { whatsapp_numbers: [], emails: [] },
        conditions: {},
        is_active: true,
      });
    }
  }, [alert, reset]);

  const onSubmit = (data: AlertFormData) => {
    if (isEditing && alert) {
      updateAlert(
        { id: alert.id, data },
        {
          onSuccess: () => {
            onOpenChange(false);
            reset();
          },
        }
      );
    } else {
      createAlert(data, {
        onSuccess: () => {
          onOpenChange(false);
          reset();
        },
      });
    }
  };

  const handleWhatsAppNumbersChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const numbers = value
      .split(',')
      .map((n) => n.trim())
      .filter((n) => n.length > 0);
    setValue('recipients.whatsapp_numbers', numbers);
  };

  const handleEmailsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const emails = value
      .split(',')
      .map((e) => e.trim())
      .filter((e) => e.length > 0);
    setValue('recipients.emails', emails);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={() => onOpenChange(false)}
        />

        {/* Dialog */}
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {isEditing ? "Modifier l'alerte" : 'Créer une nouvelle alerte'}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Configurez les paramètres de votre alerte pour être notifié en temps réel
              </p>
            </div>
            <button
              onClick={() => onOpenChange(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
            {/* Nom */}
            <div className="space-y-2">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Nom de l'alerte *
              </label>
              <input
                id="name"
                {...register('name')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Rupture produits prioritaires"
              />
              {errors.name && (
                <p className="text-sm text-red-600">{errors.name.message}</p>
              )}
            </div>

            {/* Type d'alerte */}
            <div className="space-y-2">
              <label htmlFor="alert_type" className="block text-sm font-medium text-gray-700">
                Type d'alerte *
              </label>
              <select
                id="alert_type"
                {...register('alert_type')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="RUPTURE_STOCK">Rupture de Stock</option>
                <option value="LOW_STOCK">Stock Faible</option>
                <option value="BAISSE_TAUX_SERVICE">Baisse Taux de Service</option>
              </select>
              {errors.alert_type && (
                <p className="text-sm text-red-600">{errors.alert_type.message}</p>
              )}
            </div>

            {/* Canaux de notification */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                Canaux de notification *
              </label>
              <div className="space-y-3 bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="whatsapp"
                    checked={watchWhatsApp}
                    onChange={(e) => setValue('channels.whatsapp', e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="whatsapp" className="text-sm text-gray-700 cursor-pointer">
                    WhatsApp
                  </label>
                </div>
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="email"
                    checked={watchEmail}
                    onChange={(e) => setValue('channels.email', e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="email" className="text-sm text-gray-700 cursor-pointer">
                    Email
                  </label>
                </div>
              </div>
            </div>

            {/* Destinataires WhatsApp */}
            {watchWhatsApp && (
              <div className="space-y-2">
                <label htmlFor="whatsapp_numbers" className="block text-sm font-medium text-gray-700">
                  Numéros WhatsApp *
                </label>
                <input
                  id="whatsapp_numbers"
                  type="text"
                  placeholder="+221771234567, +221765432109"
                  defaultValue={alert?.recipients.whatsapp_numbers?.join(', ') || ''}
                  onChange={handleWhatsAppNumbersChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500">
                  Format international (+221...). Séparez plusieurs numéros par des virgules.
                </p>
              </div>
            )}

            {/* Destinataires Email */}
            {watchEmail && (
              <div className="space-y-2">
                <label htmlFor="emails" className="block text-sm font-medium text-gray-700">
                  Adresses email *
                </label>
                <input
                  id="emails"
                  type="text"
                  placeholder="user@example.com, admin@example.com"
                  defaultValue={alert?.recipients.emails?.join(', ') || ''}
                  onChange={handleEmailsChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500">
                  Séparez plusieurs adresses par des virgules.
                </p>
              </div>
            )}

            {/* Activer à la création */}
            {!isEditing && (
              <div className="flex items-center space-x-3 bg-blue-50 p-4 rounded-lg">
                <input
                  type="checkbox"
                  id="is_active"
                  defaultChecked={true}
                  onChange={(e) => setValue('is_active', e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <label htmlFor="is_active" className="text-sm text-gray-700 cursor-pointer">
                  Activer l'alerte immédiatement après création
                </label>
              </div>
            )}

            {/* Boutons */}
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={() => {
                  onOpenChange(false);
                  reset();
                }}
                disabled={isCreating || isUpdating}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={isCreating || isUpdating}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {isCreating || isUpdating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    {isEditing ? 'Modification...' : 'Création...'}
                  </>
                ) : (
                  <>{isEditing ? 'Modifier' : 'Créer'}</>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

/**
 * WizardLayout - Layout principal du wizard d'onboarding
 *
 * Sprint 3: Composant layout avec stepper 4 étapes
 */
import type { ReactNode } from 'react';
import { Check } from 'lucide-react';

interface WizardLayoutProps {
  currentStep: number;
  children: ReactNode;
}

interface Step {
  number: number;
  title: string;
  description: string;
}

const steps: Step[] = [
  {
    number: 1,
    title: 'Informations Entreprise',
    description: 'Créer le tenant et le site principal',
  },
  {
    number: 2,
    title: 'Utilisateurs',
    description: 'Ajouter les utilisateurs du système',
  },
  {
    number: 3,
    title: 'Télécharger Template',
    description: 'Obtenir le fichier Excel de données',
  },
  {
    number: 4,
    title: 'Importer Données',
    description: 'Charger produits et ventes',
  },
];

export const WizardLayout = ({ currentStep, children }: WizardLayoutProps) => {
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Wizard d'Onboarding Client
          </h1>
          <p className="mt-2 text-gray-600">
            Créez un nouveau tenant en 4 étapes simples
          </p>
        </div>

        {/* Stepper */}
        <nav aria-label="Progress" className="mb-10">
          <ol className="flex items-center justify-between">
            {steps.map((step, index) => {
              const isCompleted = currentStep > step.number;
              const isCurrent = currentStep === step.number;

              return (
                <li
                  key={step.number}
                  className={`relative flex-1 ${
                    index !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''
                  }`}
                >
                  {/* Connector Line */}
                  {index !== steps.length - 1 && (
                    <div
                      className="absolute top-4 left-0 right-0 -translate-x-1/2 translate-x-[calc(50%+1rem)]"
                      aria-hidden="true"
                    >
                      <div
                        className={`h-0.5 w-full ${
                          isCompleted ? 'bg-indigo-600' : 'bg-gray-300'
                        }`}
                      />
                    </div>
                  )}

                  {/* Step Circle */}
                  <div className="relative flex flex-col items-center group">
                    <span
                      className={`
                        w-9 h-9 flex items-center justify-center rounded-full
                        text-sm font-semibold
                        ${
                          isCompleted
                            ? 'bg-indigo-600 text-white'
                            : isCurrent
                            ? 'bg-indigo-600 text-white ring-8 ring-indigo-100'
                            : 'bg-white text-gray-500 border-2 border-gray-300'
                        }
                      `}
                    >
                      {isCompleted ? (
                        <Check className="w-5 h-5" />
                      ) : (
                        step.number
                      )}
                    </span>

                    {/* Step Label */}
                    <div className="mt-3 text-center">
                      <span
                        className={`
                          block text-sm font-medium
                          ${
                            isCurrent
                              ? 'text-indigo-600'
                              : isCompleted
                              ? 'text-gray-900'
                              : 'text-gray-500'
                          }
                        `}
                      >
                        {step.title}
                      </span>
                      <span className="hidden sm:block text-xs text-gray-500 mt-1">
                        {step.description}
                      </span>
                    </div>
                  </div>
                </li>
              );
            })}
          </ol>
        </nav>

        {/* Content Card */}
        <div className="bg-white shadow-lg rounded-lg p-6 sm:p-8">
          {children}
        </div>

        {/* Footer */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>
            Étape {currentStep} sur {steps.length} - Vous pourrez modifier ces
            informations plus tard
          </p>
        </div>
      </div>
    </div>
  );
};

export default WizardLayout;

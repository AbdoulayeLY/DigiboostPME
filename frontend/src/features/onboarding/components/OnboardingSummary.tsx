/**
 * OnboardingSummary - Récapitulatif final après import réussi
 *
 * Sprint 3: Affiche tenant créé, users, stats import
 */
import { CheckCircle2, Building2, Users, Package, ShoppingCart } from 'lucide-react';

interface OnboardingSummaryProps {
  tenantId: string;
  tenantName: string;
  siteName: string;
  usersCreated: number;
  productsImported: number;
  salesImported: number;
  onComplete: () => void;
}

export const OnboardingSummary = ({
  tenantId,
  tenantName,
  siteName,
  usersCreated,
  productsImported,
  salesImported,
  onComplete,
}: OnboardingSummaryProps) => {
  return (
    <div className="space-y-6">
      {/* Header Success */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
          <CheckCircle2 className="w-10 h-10 text-green-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900">
          Onboarding Terminé!
        </h2>
        <p className="mt-2 text-lg text-gray-600">
          Le tenant est maintenant configuré et prêt à être utilisé
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        {/* Tenant Info */}
        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-6 border border-indigo-200">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-indigo-600 rounded-lg">
              <Building2 className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                Entreprise Créée
              </h3>
              <p className="text-2xl font-bold text-indigo-600 mt-1">
                {tenantName}
              </p>
              <div className="mt-3 space-y-1 text-sm text-gray-700">
                <div>
                  <span className="font-medium">ID Tenant:</span>{' '}
                  <code className="px-2 py-1 bg-white rounded text-xs">
                    {tenantId}
                  </code>
                </div>
                <div>
                  <span className="font-medium">Site Principal:</span> {siteName}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Users Created */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-600 rounded-lg">
              <Users className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                Utilisateurs
              </h3>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                {usersCreated} {usersCreated > 1 ? 'utilisateurs' : 'utilisateur'}
              </p>
              <p className="mt-3 text-sm text-gray-700">
                Comptes créés avec accès au système
              </p>
            </div>
          </div>
        </div>

        {/* Products Imported */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-purple-600 rounded-lg">
              <Package className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                Produits Importés
              </h3>
              <p className="text-2xl font-bold text-purple-600 mt-1">
                {productsImported}
              </p>
              <p className="mt-3 text-sm text-gray-700">
                Articles ajoutés au catalogue
              </p>
            </div>
          </div>
        </div>

        {/* Sales Imported */}
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-green-600 rounded-lg">
              <ShoppingCart className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900">
                Ventes Importées
              </h3>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {salesImported}
              </p>
              <p className="mt-3 text-sm text-gray-700">
                Historique des ventes chargé
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 mt-6">
        <h3 className="text-lg font-semibold text-amber-900 mb-3">
          Prochaines Étapes
        </h3>
        <ul className="space-y-2 text-sm text-amber-900">
          <li className="flex items-start gap-2">
            <span className="font-bold mt-0.5">1.</span>
            <span>
              Les utilisateurs peuvent maintenant se connecter avec leurs
              identifiants
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold mt-0.5">2.</span>
            <span>
              Ils devront changer leur mot de passe à la première connexion
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold mt-0.5">3.</span>
            <span>
              Les prédictions et alertes seront générées automatiquement dans
              les 24h
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="font-bold mt-0.5">4.</span>
            <span>
              Le dashboard sera accessible immédiatement avec les données
              importées
            </span>
          </li>
        </ul>
      </div>

      {/* Action Button */}
      <div className="flex justify-center pt-6">
        <button
          type="button"
          onClick={onComplete}
          className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
        >
          <CheckCircle2 className="-ml-1 mr-3 h-6 w-6" />
          Terminer et Retourner au Dashboard
        </button>
      </div>
    </div>
  );
};

export default OnboardingSummary;

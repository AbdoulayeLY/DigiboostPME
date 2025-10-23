/**
 * Step3GenerateTemplate - Génération et téléchargement du template Excel
 *
 * Sprint 3: Étape 3 du wizard onboarding
 */
import { useState } from 'react';
import { Download, FileSpreadsheet, CheckCircle2, Loader2 } from 'lucide-react';
import { downloadTemplate } from '@/api/onboarding';
import { toast } from 'sonner';

interface Step3GenerateTemplateProps {
  tenantId: string;
  onNext: () => void;
  onBack: () => void;
}

export const Step3GenerateTemplate = ({
  tenantId,
  onNext,
  onBack,
}: Step3GenerateTemplateProps) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [hasDownloaded, setHasDownloaded] = useState(false);

  const handleDownload = async () => {
    setIsDownloading(true);

    try {
      await downloadTemplate(tenantId);

      toast.success('Template téléchargé avec succès!', {
        description: "Remplissez le fichier Excel et revenez pour l'importer",
      });

      setHasDownloaded(true);
    } catch (error) {
      console.error('Erreur téléchargement template:', error);

      toast.error('Échec du téléchargement', {
        description: 'Impossible de télécharger le template',
      });
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Télécharger le Template
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Obtenez le fichier Excel personnalisé pour importer vos données
        </p>
      </div>

      {/* Instructions */}
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-indigo-900 mb-4">
          📋 Instructions
        </h3>
        <ol className="space-y-3 text-sm text-indigo-900">
          <li className="flex items-start gap-2">
            <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-indigo-600 text-white rounded-full text-xs font-bold">
              1
            </span>
            <span>
              <strong>Téléchargez le template Excel</strong> en cliquant sur le
              bouton ci-dessous
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-indigo-600 text-white rounded-full text-xs font-bold">
              2
            </span>
            <span>
              <strong>Remplissez les onglets</strong>:
              <ul className="mt-2 ml-6 space-y-1 list-disc">
                <li>
                  <strong>Produits</strong>: Votre catalogue complet (codes,
                  noms, prix, stocks)
                </li>
                <li>
                  <strong>Ventes</strong>: Historique des ventes (optionnel,
                  recommandé 30 jours minimum)
                </li>
              </ul>
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-indigo-600 text-white rounded-full text-xs font-bold">
              3
            </span>
            <span>
              <strong>Suivez les instructions</strong> dans l'onglet
              "Instructions" du fichier
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-indigo-600 text-white rounded-full text-xs font-bold">
              4
            </span>
            <span>
              <strong>Revenez ici</strong> pour importer le fichier rempli
            </span>
          </li>
        </ol>
      </div>

      {/* Contenu du template */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          📊 Contenu du Template
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Onglet Produits */}
          <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-lg p-4 border border-indigo-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 bg-indigo-600 rounded"></div>
              <h4 className="font-semibold text-gray-900">Produits</h4>
            </div>
            <p className="text-xs text-gray-600 mb-2">
              Informations produits complètes
            </p>
            <ul className="text-xs text-gray-700 space-y-1">
              <li>• Code produit (unique)</li>
              <li>• Nom et catégorie</li>
              <li>• Prix achat/vente</li>
              <li>• Stocks (initial, min, max)</li>
              <li>• Validation Excel intégrée</li>
            </ul>
          </div>

          {/* Onglet Ventes */}
          <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 bg-green-600 rounded"></div>
              <h4 className="font-semibold text-gray-900">Ventes</h4>
            </div>
            <p className="text-xs text-gray-600 mb-2">
              Historique des transactions
            </p>
            <ul className="text-xs text-gray-700 space-y-1">
              <li>• Code produit (référence)</li>
              <li>• Date de vente</li>
              <li>• Quantité et prix</li>
              <li>• Formules automatiques</li>
              <li>• Optionnel mais recommandé</li>
            </ul>
          </div>

          {/* Onglet Instructions */}
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg p-4 border border-amber-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 bg-amber-600 rounded"></div>
              <h4 className="font-semibold text-gray-900">Instructions</h4>
            </div>
            <p className="text-xs text-gray-600 mb-2">Guide utilisateur complet</p>
            <ul className="text-xs text-gray-700 space-y-1">
              <li>• Étapes d'utilisation</li>
              <li>• Format des données</li>
              <li>• Erreurs courantes</li>
              <li>• Conseils et astuces</li>
            </ul>
          </div>

          {/* Onglets Référence */}
          <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-lg p-4 border border-purple-200">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 bg-purple-600 rounded"></div>
              <h4 className="font-semibold text-gray-900">Référence</h4>
            </div>
            <p className="text-xs text-gray-600 mb-2">
              Données de référence
            </p>
            <ul className="text-xs text-gray-700 space-y-1">
              <li>• Catégories existantes</li>
              <li>• Fournisseurs existants</li>
              <li>• Listes pré-remplies</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bouton Télécharger */}
      <div className="flex flex-col items-center gap-4 py-8">
        {hasDownloaded && (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle2 className="w-5 h-5" />
            <span className="text-sm font-medium">
              Template téléchargé avec succès!
            </span>
          </div>
        )}

        <button
          type="button"
          onClick={handleDownload}
          disabled={isDownloading}
          className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isDownloading ? (
            <>
              <Loader2 className="animate-spin -ml-1 mr-3 h-6 w-6" />
              Téléchargement en cours...
            </>
          ) : (
            <>
              <Download className="-ml-1 mr-3 h-6 w-6" />
              Télécharger le Template Excel
            </>
          )}
        </button>

        <p className="text-xs text-gray-500">
          Fichier: template_digiboost_{tenantId}.xlsx
        </p>
      </div>

      {/* Alert */}
      {hasDownloaded && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <div className="flex gap-3">
            <FileSpreadsheet className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-amber-900">
              <p className="font-medium mb-1">Remplissez le template avant de continuer</p>
              <p>
                Une fois votre fichier Excel complété avec vos produits et
                ventes, cliquez sur "Continuer" pour passer à l'import.
              </p>
            </div>
          </div>
        </div>
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
          type="button"
          onClick={onNext}
          disabled={!hasDownloaded}
          className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continuer vers l'Import
        </button>
      </div>
    </div>
  );
};

export default Step3GenerateTemplate;

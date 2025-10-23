/**
 * Step4DataImport - Upload et import du fichier Excel
 *
 * Sprint 3: Étape 4 finale du wizard avec progress tracking
 */
import { useState, useRef } from 'react';
import { Upload, FileSpreadsheet, Loader2, CheckCircle2, AlertTriangle } from 'lucide-react';
import { uploadTemplate } from '@/api/onboarding';
import { ImportProgressTracker } from './ImportProgressTracker';
import { toast } from 'sonner';

interface Step4DataImportProps {
  tenantId: string;
  onImportComplete: (productsCount: number, salesCount: number) => void;
  onBack: () => void;
}

export const Step4DataImport = ({
  tenantId,
  onImportComplete,
  onBack,
}: Step4DataImportProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [importJobId, setImportJobId] = useState<string | null>(null);
  const [importStats, setImportStats] = useState<{
    products: number;
    sales: number;
  } | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const file = files[0];

      // Vérifier le format
      if (!file.name.endsWith('.xlsx')) {
        toast.error('Format invalide', {
          description: 'Seuls les fichiers .xlsx sont acceptés',
        });
        return;
      }

      // Vérifier la taille (max 10MB)
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        toast.error('Fichier trop volumineux', {
          description: 'La taille maximale est de 10 MB',
        });
        return;
      }

      setSelectedFile(file);
      setImportJobId(null);
      setImportStats(null);
      setImportError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setImportError(null);

    try {
      const response = await uploadTemplate(tenantId, selectedFile);

      toast.success('Fichier uploadé avec succès!', {
        description: "L'import a démarré, veuillez patienter...",
      });

      // Démarrer le tracking de progression
      setImportJobId(response.job_id);
    } catch (error: unknown) {
      console.error('Erreur upload:', error);

      const errorMessage =
        error && typeof error === 'object' && 'response' in error
          ? (error as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
            "Erreur lors de l'upload du fichier"
          : "Erreur lors de l'upload du fichier";

      toast.error("Échec de l'upload", {
        description: errorMessage,
      });

      setImportError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];

      if (!file.name.endsWith('.xlsx')) {
        toast.error('Format invalide', {
          description: 'Seuls les fichiers .xlsx sont acceptés',
        });
        return;
      }

      setSelectedFile(file);
      setImportJobId(null);
      setImportStats(null);
      setImportError(null);
    }
  };

  const handleImportComplete = (productsCount: number, salesCount: number) => {
    setImportStats({ products: productsCount, sales: salesCount });
    toast.success('Import terminé avec succès!', {
      description: 'Toutes vos données ont été importées',
    });
  };

  const handleImportError = (error: string) => {
    setImportError(error);
    toast.error("Échec de l'import", {
      description: error,
    });
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Importer les Données</h2>
        <p className="mt-1 text-sm text-gray-600">
          Uploadez le fichier Excel rempli pour importer vos produits et ventes
        </p>
      </div>

      {/* Upload Zone ou Progress Tracker */}
      {!importJobId ? (
        <div className="space-y-6">
          {/* Drag & Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`
              relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
              transition-colors duration-200
              ${
                selectedFile
                  ? 'border-indigo-300 bg-indigo-50'
                  : 'border-gray-300 bg-gray-50 hover:border-indigo-400 hover:bg-indigo-50'
              }
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx"
              onChange={handleFileSelect}
              className="hidden"
            />

            <div className="space-y-4">
              {selectedFile ? (
                <>
                  <FileSpreadsheet className="mx-auto h-16 w-16 text-indigo-600" />
                  <div>
                    <p className="text-lg font-semibold text-gray-900">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-gray-600">
                      {(selectedFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <p className="text-sm text-indigo-600">
                    Cliquez pour changer de fichier
                  </p>
                </>
              ) : (
                <>
                  <Upload className="mx-auto h-16 w-16 text-gray-400" />
                  <div>
                    <p className="text-lg font-semibold text-gray-900">
                      Glissez-déposez votre fichier Excel ici
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      ou cliquez pour parcourir
                    </p>
                  </div>
                  <p className="text-xs text-gray-500">
                    Format accepté: .xlsx (max 10 MB)
                  </p>
                </>
              )}
            </div>
          </div>

          {/* Bouton Upload */}
          {selectedFile && !importJobId && (
            <button
              type="button"
              onClick={handleUpload}
              disabled={isUploading}
              className="w-full inline-flex items-center justify-center px-6 py-4 border border-transparent text-lg font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-3 h-6 w-6" />
                  Upload en cours...
                </>
              ) : (
                <>
                  <Upload className="-ml-1 mr-3 h-6 w-6" />
                  Lancer l'Import
                </>
              )}
            </button>
          )}

          {/* Avertissements */}
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="flex gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-amber-900 space-y-2">
                <p className="font-medium">Points d'attention:</p>
                <ul className="list-disc ml-4 space-y-1">
                  <li>
                    Assurez-vous d'avoir rempli au minimum l'onglet "Produits"
                  </li>
                  <li>
                    Vérifiez que les codes produits sont uniques
                  </li>
                  <li>
                    L'historique des ventes est optionnel mais recommandé (30
                    jours min)
                  </li>
                  <li>
                    L'import peut prendre quelques minutes selon la quantité de
                    données
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Progress Tracker */
        <ImportProgressTracker
          importJobId={importJobId}
          onComplete={handleImportComplete}
          onError={handleImportError}
        />
      )}

      {/* Error Message */}
      {importError && !importJobId && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <div className="text-sm text-red-900">
              <p className="font-medium">Erreur lors de l'import:</p>
              <p className="mt-1">{importError}</p>
              <p className="mt-2">
                Vérifiez votre fichier et réessayez, ou contactez le support si
                le problème persiste.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between gap-3 pt-6 mt-6 border-t border-gray-200">
        <button
          type="button"
          onClick={onBack}
          disabled={isUploading || !!importJobId}
          className="px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Retour
        </button>

        {importStats && (
          <button
            type="button"
            onClick={() =>
              onImportComplete(importStats.products, importStats.sales)
            }
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <CheckCircle2 className="-ml-1 mr-2 h-5 w-5" />
            Voir le Récapitulatif
          </button>
        )}
      </div>
    </div>
  );
};

export default Step4DataImport;

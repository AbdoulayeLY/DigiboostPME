/**
 * Page de génération de rapports
 */
import { useState } from 'react';
import { FileText, Download, Calendar, Loader2, FileSpreadsheet, FileBox } from 'lucide-react';
import { apiClient } from '@/api/client';
import { toast } from 'sonner';

const RapportsPage = () => {
  const [loadingInventory, setLoadingInventory] = useState(false);
  const [loadingPDF, setLoadingPDF] = useState(false);
  const [loadingSales, setLoadingSales] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  // Télécharger un fichier
  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  // Générer rapport inventaire (Excel)
  const handleGenerateInventory = async () => {
    setLoadingInventory(true);
    try {
      const response = await apiClient.get('/reports/inventory/excel', {
        responseType: 'blob',
      });

      const filename = `inventaire_stock_${new Date().toISOString().split('T')[0]}.xlsx`;
      downloadFile(response.data, filename);
      toast.success('Rapport inventaire généré avec succès!');
    } catch (error: any) {
      console.error('Erreur génération inventaire:', error);
      toast.error('Erreur lors de la génération du rapport');
    } finally {
      setLoadingInventory(false);
    }
  };

  // Générer rapport ventes (Excel)
  const handleGenerateSales = async () => {
    setLoadingSales(true);
    try {
      const response = await apiClient.get('/reports/sales-analysis/monthly/excel', {
        params: {
          month: selectedMonth,
          year: selectedYear,
        },
        responseType: 'blob',
      });

      const monthNames = [
        'janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre'
      ];
      const filename = `analyse_ventes_${monthNames[selectedMonth - 1]}_${selectedYear}.xlsx`;
      downloadFile(response.data, filename);
      toast.success('Rapport ventes généré avec succès!');
    } catch (error: any) {
      console.error('Erreur génération ventes:', error);
      toast.error('Erreur lors de la génération du rapport');
    } finally {
      setLoadingSales(false);
    }
  };

  // Générer synthèse mensuelle (PDF)
  const handleGenerateMonthlySummary = async () => {
    setLoadingPDF(true);
    try {
      const response = await apiClient.get('/reports/monthly-summary/pdf', {
        params: {
          month: selectedMonth,
          year: selectedYear,
        },
        responseType: 'blob',
      });

      const monthNames = [
        'janvier', 'fevrier', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'decembre'
      ];
      const filename = `synthese_mensuelle_${monthNames[selectedMonth - 1]}_${selectedYear}.pdf`;
      downloadFile(response.data, filename);
      toast.success('Synthèse mensuelle générée avec succès!');
    } catch (error: any) {
      console.error('Erreur génération PDF:', error);
      toast.error('Erreur lors de la génération de la synthèse');
    } finally {
      setLoadingPDF(false);
    }
  };

  const months = [
    { value: 1, label: 'Janvier' },
    { value: 2, label: 'Février' },
    { value: 3, label: 'Mars' },
    { value: 4, label: 'Avril' },
    { value: 5, label: 'Mai' },
    { value: 6, label: 'Juin' },
    { value: 7, label: 'Juillet' },
    { value: 8, label: 'Août' },
    { value: 9, label: 'Septembre' },
    { value: 10, label: 'Octobre' },
    { value: 11, label: 'Novembre' },
    { value: 12, label: 'Décembre' },
  ];

  const years = Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i);

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Rapports</h1>
        <p className="mt-2 text-gray-600">
          Générez des rapports professionnels (Excel, PDF) pour votre gestion
        </p>
      </div>

      {/* Grille de rapports */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Rapport Inventaire Stock */}
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <FileSpreadsheet className="h-6 w-6 text-green-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">Excel</span>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Inventaire Stock
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Liste complète de vos produits avec stock actuel, min/max et valorisation
          </p>

          <ul className="text-xs text-gray-500 mb-4 space-y-1">
            <li>• Tous les produits</li>
            <li>• Stock actuel, min, max</li>
            <li>• Prix et valorisation</li>
            <li>• Totaux par catégorie</li>
          </ul>

          <button
            onClick={handleGenerateInventory}
            disabled={loadingInventory}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loadingInventory ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Génération...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Générer
              </>
            )}
          </button>
        </div>

        {/* Rapport Analyse Ventes */}
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <FileSpreadsheet className="h-6 w-6 text-blue-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">Excel</span>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Analyse Ventes
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Analyse détaillée de vos ventes par produit et catégorie
          </p>

          {/* Sélection période */}
          <div className="mb-4 space-y-2">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <label className="text-xs font-medium text-gray-700">Période</label>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <select
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(Number(e.target.value))}
                className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {months.map((month) => (
                  <option key={month.value} value={month.value}>
                    {month.label}
                  </option>
                ))}
              </select>

              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleGenerateSales}
            disabled={loadingSales}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loadingSales ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Génération...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Générer
              </>
            )}
          </button>
        </div>

        {/* Rapport Synthèse Mensuelle (PDF) */}
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <FileBox className="h-6 w-6 text-purple-600" />
            </div>
            <span className="text-sm font-medium text-gray-500">PDF</span>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Synthèse Mensuelle
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Rapport professionnel avec KPIs, graphiques et recommandations
          </p>

          {/* Sélection période */}
          <div className="mb-4 space-y-2">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <label className="text-xs font-medium text-gray-700">Période</label>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <select
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(Number(e.target.value))}
                className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {months.map((month) => (
                  <option key={month.value} value={month.value}>
                    {month.label}
                  </option>
                ))}
              </select>

              <select
                value={selectedYear}
                onChange={(e) => setSelectedYear(Number(e.target.value))}
                className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleGenerateMonthlySummary}
            disabled={loadingPDF}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loadingPDF ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Génération...
              </>
            ) : (
              <>
                <Download className="h-4 w-4" />
                Générer PDF
              </>
            )}
          </button>
        </div>
      </div>

      {/* Section info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <FileText className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-blue-900 mb-1">
              Rapports Automatiques
            </h4>
            <p className="text-sm text-blue-700">
              La synthèse mensuelle est générée automatiquement le 1er de chaque mois à 8h00
              et envoyée par email. Les fichiers sont conservés pendant 90 jours.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RapportsPage;

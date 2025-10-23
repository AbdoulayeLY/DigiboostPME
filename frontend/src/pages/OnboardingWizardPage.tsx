/**
 * OnboardingWizardPage - Page principale du wizard d'onboarding
 *
 * Sprint 3: Orchestration complète des 4 étapes
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WizardLayout } from '@/features/onboarding/components/WizardLayout';
import { Step1CreateTenant } from '@/features/onboarding/components/Step1CreateTenant';
import { Step2CreateUsers } from '@/features/onboarding/components/Step2CreateUsers';
import { Step3GenerateTemplate } from '@/features/onboarding/components/Step3GenerateTemplate';
import { Step4DataImport } from '@/features/onboarding/components/Step4DataImport';
import { OnboardingSummary } from '@/features/onboarding/components/OnboardingSummary';
import { toast } from 'sonner';

interface OnboardingState {
  tenantId: string | null;
  tenantName: string | null;
  siteName: string | null;
  siteId: string | null;
  sessionId: string | null;
  usersCreated: number;
  productsImported: number;
  salesImported: number;
}

export const OnboardingWizardPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [showSummary, setShowSummary] = useState(false);
  const [onboardingState, setOnboardingState] = useState<OnboardingState>({
    tenantId: null,
    tenantName: null,
    siteName: null,
    siteId: null,
    sessionId: null,
    usersCreated: 0,
    productsImported: 0,
    salesImported: 0,
  });

  // Step 1: Création tenant/site
  const handleStep1Success = (
    tenantId: string,
    siteId: string,
    sessionId: string,
    tenantName: string,
    siteName: string
  ) => {
    setOnboardingState((prev) => ({
      ...prev,
      tenantId,
      siteId,
      sessionId,
      tenantName,
      siteName,
    }));
  };

  // Step 2: Création utilisateurs
  const handleStep2Success = (usersCount: number) => {
    setOnboardingState((prev) => ({
      ...prev,
      usersCreated: usersCount,
    }));
  };

  // Step 4: Import terminé
  const handleImportComplete = (
    productsCount: number,
    salesCount: number
  ) => {
    setOnboardingState((prev) => ({
      ...prev,
      productsImported: productsCount,
      salesImported: salesCount,
    }));
    setShowSummary(true);
  };

  // Wizard terminé
  const handleComplete = () => {
    toast.success('Onboarding terminé!', {
      description: `Le tenant ${onboardingState.tenantName} est maintenant actif`,
      duration: 5000,
    });

    // Rediriger vers le dashboard
    setTimeout(() => {
      navigate('/dashboard');
    }, 2000);
  };

  // Navigation
  const goToNextStep = () => {
    if (currentStep < 4) {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const goToPreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  // Afficher le summary si import terminé
  if (showSummary && onboardingState.tenantId && onboardingState.tenantName && onboardingState.siteName) {
    return (
      <WizardLayout currentStep={5}>
        <OnboardingSummary
          tenantId={onboardingState.tenantId}
          tenantName={onboardingState.tenantName}
          siteName={onboardingState.siteName}
          usersCreated={onboardingState.usersCreated}
          productsImported={onboardingState.productsImported}
          salesImported={onboardingState.salesImported}
          onComplete={handleComplete}
        />
      </WizardLayout>
    );
  }

  return (
    <WizardLayout currentStep={currentStep}>
      {currentStep === 1 && (
        <Step1CreateTenant
          onSuccess={handleStep1Success}
          onNext={goToNextStep}
        />
      )}

      {currentStep === 2 && onboardingState.tenantId && (
        <Step2CreateUsers
          tenantId={onboardingState.tenantId}
          onSuccess={handleStep2Success}
          onNext={goToNextStep}
          onBack={goToPreviousStep}
        />
      )}

      {currentStep === 3 && onboardingState.tenantId && (
        <Step3GenerateTemplate
          tenantId={onboardingState.tenantId}
          onNext={goToNextStep}
          onBack={goToPreviousStep}
        />
      )}

      {currentStep === 4 && onboardingState.tenantId && (
        <Step4DataImport
          tenantId={onboardingState.tenantId}
          onImportComplete={handleImportComplete}
          onBack={goToPreviousStep}
        />
      )}
    </WizardLayout>
  );
};

export default OnboardingWizardPage;

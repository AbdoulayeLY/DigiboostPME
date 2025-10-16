# SPÉCIFICATION FONCTIONNELLE POC v1.0
## Plateforme Intelligence Supply Chain - Approche Métier

**Version** : 1.0 POC  
**Date** : Octobre 2025  
**Rôle** : Supply Chain Business Analyst  
**Public** : Product Owner, Business Stakeholders, Équipe Projet

---

## 📋 TABLE DES MATIÈRES

1. [Vision Métier](#1-vision-métier)
2. [Domaines Métiers Couverts](#2-domaines-métiers-couverts)
3. [Indicateurs & KPI Supply Chain](#3-indicateurs--kpi-supply-chain)
4. [Dashboards - Spécifications Fonctionnelles](#4-dashboards---spécifications-fonctionnelles)
5. [Système d'Alerting - Logique Métier](#5-système-dalerting---logique-métier)
6. [Rapports & Analyses](#6-rapports--analyses)
7. [Agent IA - Cas d'Usage Métier](#7-agent-ia---cas-dusage-métier)
8. [Règles de Gestion Supply Chain](#8-règles-de-gestion-supply-chain)
9. [Données Métiers Requises](#9-données-métiers-requises)
10. [Gestion Multi-Site](#10-gestion-multi-site)
11. [Feuille de Route Fonctionnelle](#11-feuille-de-route-fonctionnelle)

---

## 1. VISION MÉTIER

### 1.1 Problématique Supply Chain PME Sénégal

**Constat Terrain** :
- **Visibilité limitée** : Le gérant ne connaît sa situation stock qu'en consultant manuellement son Excel/cahier
- **Réactivité insuffisante** : Les ruptures sont constatées APRÈS qu'elles se produisent, jamais anticipées
- **Décisions au feeling** : Manque d'indicateurs chiffrés pour piloter (taux de service, rotation, marge)
- **Opportunités manquées** : Produits stars non identifiés, surstocks immobilisant trésorerie

**Objectif Plateforme** :
> Transformer les données supply chain en intelligence actionnable permettant au gérant de **voir**, **anticiper** et **décider** en temps réel.

### 1.2 Proposition de Valeur

```
AVANT                           APRÈS
─────────────────────────────────────────────────────────────
📊 Consultation Excel          →  Dashboard temps réel
   Manuel, statique                 Automatique, dynamique

❓ "Combien de sacs riz ?"     →  Alerte proactive
   Découverte rupture              "Rupture dans 3 jours"

🤔 Décision intuitive          →  Recommandation chiffrée
   "Je commande 50 sacs"           "Commander 73 sacs (15j couverture)"

📉 Pilotage aveugle            →  KPI actionnables
   Pas de métriques                Taux service 87% (objectif 95%)

💰 Trésorerie bloquée          →  Optimisation stock
   Surstocks non identifiés        2.5M FCFA mobilisés inutilement
```

### 1.3 Périmètre POC

**Phase 1 - Intelligence Layer (POC)** :
- ✅ Lecture données existantes (via vues SQL)
- ✅ Dashboards temps réel (4 tableaux de bord)
- ✅ Système d'alerting configurable (5 types d'alertes)
- ✅ Rapports automatisés (3 rapports standards)
- ✅ Préparation infrastructure agent IA

**Hors Périmètre POC** :
- ❌ Saisie directe données (pas de formulaires entrée/sortie stock)
- ❌ Gestion commandes fournisseurs (pas de bon de commande)
- ❌ Gestion commandes clients (pas de prise de commande)
- ❌ Intégration Expose API (simulation données en base)
- ❌ Agent IA opérationnel (préparation uniquement)

---

## 2. DOMAINES MÉTIERS COUVERTS

### 2.1 Gestion Stock

#### Périmètre Fonctionnel
**Ce que la plateforme DOIT permettre** :
- Connaître l'état du stock en temps réel (quantité, valeur)
- Identifier les produits en situation critique (rupture, stock faible, surstock)
- Suivre l'évolution du stock dans le temps (historique)
- Anticiper les ruptures futures (prédiction basée sur consommation)
- Mesurer la performance stock (taux de service, rotation, couverture)

**Granularités d'Analyse** :
- Vue globale : "Mon stock total vaut 12.5M FCFA"
- Par catégorie : "Riz = 35% valeur stock total"
- Par produit : "Farine 50kg : 23 sacs (4 jours de vente restants)"
- Par statut : "12 produits en rupture, 34 en alerte"

#### Règles Métier Stock

**RG-STOCK-01 : Définition Statut Stock**
```
Pour chaque produit :

RUPTURE si :
  - Stock actuel = 0
  OU Stock actuel < Stock minimum (si défini)

ALERTE si :
  - Stock actuel < (Vente moyenne quotidienne × Délai alerte jours)
  - Délai alerte par défaut = 7 jours
  - Exemple : Vente moy = 5/jour, Stock = 30 → Alerte si < 35 (5×7)

NORMAL si :
  - Stock >= Seuil alerte
  - Stock <= Stock maximum (si défini)

SURSTOCK si :
  - Stock > Stock maximum (si défini)
  - OU Stock > (Vente moyenne quotidienne × 60 jours) ET aucune vente 30 derniers jours
```

**RG-STOCK-02 : Calcul Couverture Stock**
```
Couverture (jours) = Stock actuel / Vente moyenne quotidienne

Vente moyenne quotidienne calculée sur :
  - Par défaut : 30 derniers jours
  - Minimum : 7 derniers jours (si historique < 30j)
  - Exclusion jours sans vente (dimanches, jours fériés si configuré)

Exemple :
  Stock actuel : 45 sacs
  Ventes 30 derniers jours : 180 sacs
  Vente moy/jour : 180/30 = 6 sacs/jour
  Couverture : 45/6 = 7.5 jours
```

**RG-STOCK-03 : Calcul Rotation Stock**
```
Rotation annuelle = (Coût marchandises vendues année) / (Valeur stock moyen)

Ou plus simplement pour PME :
Rotation = (Quantité vendue période) / (Stock moyen période)

Interprétation :
  - Rotation > 12 : Excellent (produit tourne plus d'une fois/mois)
  - Rotation 6-12 : Bon
  - Rotation 3-6 : Acceptable
  - Rotation < 3 : Mauvais (produit dort en stock)

Exemple :
  Ventes 12 mois : 1200 sacs
  Stock moyen : 150 sacs
  Rotation : 1200/150 = 8 rotations/an (bon)
```

### 2.2 Analyse Ventes

#### Périmètre Fonctionnel
**Ce que la plateforme DOIT permettre** :
- Suivre le chiffre d'affaires (jour, semaine, mois)
- Identifier les produits moteurs (top ventes)
- Identifier les meilleurs clients (si données disponibles)
- Détecter les tendances (produits en croissance/déclin)
- Mesurer la rentabilité (marges par produit/catégorie)

**Granularités d'Analyse** :
- Temporelle : Jour, semaine, mois, trimestre, année
- Produit : Par référence, par catégorie
- Client : Par client (si données disponibles)
- Géographique : Par zone (si données disponibles)

#### Règles Métier Ventes

**RG-VENTE-01 : Calcul Chiffre d'Affaires**
```
CA = Somme (Quantité vendue × Prix unitaire vente)

Par période (jour, semaine, mois...)
Par catégorie
Par produit
Par client (si disponible)

Comparaisons :
  - CA jour vs veille : Variation %
  - CA semaine vs semaine précédente
  - CA mois vs même mois année précédente (si historique)
```

**RG-VENTE-02 : Calcul Marge**
```
Marge unitaire = Prix vente - Prix achat
Marge % = ((Prix vente - Prix achat) / Prix achat) × 100

Marge brute période = Somme (Quantité vendue × Marge unitaire)
Taux marge période = (Marge brute / CA) × 100

Exemple :
  Farine 50kg : Prix achat 18 000 F, Prix vente 20 000 F
  Marge unitaire : 2 000 F
  Marge % : (2000/18000) × 100 = 11.1%
  
  Ventes mois : 150 sacs
  Marge brute mois : 150 × 2000 = 300 000 F
```

**RG-VENTE-03 : Classification ABC Produits**
```
Classement produits par CA décroissant :

Classe A (Produits stars) :
  - Représentent 80% du CA
  - Environ 20% des références
  - Priorité maximale : JAMAIS de rupture

Classe B (Produits importants) :
  - Représentent 15% du CA
  - Environ 30% des références
  - Maintenir bon niveau service

Classe C (Produits secondaires) :
  - Représentent 5% du CA
  - Environ 50% des références
  - Accepter ruptures occasionnelles, optimiser stock

Application :
  - Alertes rupture prioritaires sur produits A
  - Recommandations achat focus sur produits A et B
  - Considérer déréférencement produits C sans rotation
```

### 2.3 Performance Supply Chain

#### Indicateurs Clés

**Taux de Service**
```
Définition : Capacité à satisfaire les demandes clients sans rupture

Calcul :
  Taux service = (Jours sans rupture / Jours total période) × 100
  
  Ou par référence :
  Taux service produit = (Quantité livrée / Quantité demandée) × 100

Objectifs :
  - Objectif minimum : 90%
  - Objectif bon : 95%
  - Objectif excellent : 98%

Impact business rupture :
  - Perte vente immédiate
  - Report commande (client achète ailleurs)
  - Détérioration relation client
```

**Taux de Rotation**
```
Voir RG-STOCK-03

Utilisation :
  - Identifier produits dormants (rotation < 3)
  - Optimiser investissement stock (privilégier produits rotation élevée)
  - Négocier avec fournisseurs (produits forte rotation = pouvoir négociation)
```

**Valorisation Stock**
```
Valeur stock = Somme (Quantité × Prix achat)

Par catégorie
Évolution dans le temps
Comparaison avec objectif (ex: max 15% CA mensuel immobilisé)

Exemple :
  Stock total : 12.5M FCFA
  CA mensuel : 45M FCFA
  Ratio : 12.5/45 = 27.8% (élevé, optimisation possible)
```

---

## 3. INDICATEURS & KPI SUPPLY CHAIN

### 3.1 KPI Principaux (Tableau de Synthèse)

| KPI | Définition | Calcul | Objectif | Usage Décision |
|-----|-----------|---------|----------|----------------|
| **Taux de Service** | % satisfaction demande sans rupture | (Jours sans rupture / Total jours) × 100 | ≥ 95% | Évalue qualité service client |
| **Taux de Rotation** | Fois où stock se renouvelle/an | Ventes annuelles / Stock moyen | ≥ 6 | Identifie capital immobilisé |
| **Couverture Stock** | Nb jours avant rupture théorique | Stock actuel / Vente moy quotidienne | 15-30j | Pilote réapprovisionnement |
| **Taux de Rupture** | % références en rupture | (Nb produits rupture / Total produits) × 100 | ≤ 5% | Alerte qualité gestion |
| **Marge Brute** | Profit avant charges | CA - Coût achat marchandises | Variable | Mesure rentabilité |
| **Valeur Stock** | Capital immobilisé | Σ (Quantité × Prix achat) | ≤ 20% CA | Optimise trésorerie |

### 3.2 KPI Opérationnels (Suivi Quotidien)

**Indicateurs Stock** :
- Nombre produits en rupture
- Nombre produits en alerte (< 7 jours)
- Valeur stock immobilisé
- Top 10 produits stock excessif
- Top 10 produits rotation lente

**Indicateurs Ventes** :
- CA du jour vs objectif
- CA du jour vs veille (% variation)
- Nombre commandes traitées
- Panier moyen
- Top 5 produits vendus jour

**Indicateurs Prédictifs** :
- Nombre produits rupture prévue 7 jours
- Nombre produits rupture prévue 15 jours
- Valeur commandes suggérées (réappro optimal)

### 3.3 KPI Stratégiques (Suivi Mensuel/Trimestriel)

**Performance Globale** :
- Évolution CA (mois vs mois précédent, vs même mois N-1)
- Évolution marge brute
- Évolution taux de service
- Tendances par catégorie

**Optimisation Stock** :
- Réduction valeur stock (objectif -X%)
- Amélioration rotation (objectif +Y%)
- Réduction taux rupture

**Analyse Portefeuille Produits** :
- Produits classe A, B, C (CA)
- Nouveaux produits introduits
- Produits obsolètes à déréférencer
- Contribution marge par produit

---

## 4. DASHBOARDS - SPÉCIFICATIONS FONCTIONNELLES

### 4.1 Dashboard "Vue d'Ensemble" (Page d'Accueil)

**Objectif** : Le gérant visualise en 10 secondes la santé globale de son business.

**Indicateurs Affichés** :

**Bloc 1 : Santé Stock** (Priorité 1)
```
┌─────────────────────────────────────────┐
│  📦 SANTÉ STOCK                         │
├─────────────────────────────────────────┤
│                                         │
│  🔴 URGENT - 12 PRODUITS EN RUPTURE     │
│  → [Voir détails]                       │
│                                         │
│  ⚠️ ATTENTION - 23 PRODUITS < 7 JOURS   │
│  → [Voir détails]                       │
│                                         │
│  🟢 STOCK OK - 145 PRODUITS             │
│                                         │
│  📊 Taux de Service : 87%               │
│     Objectif : 95% ▼ (-8 points)       │
│                                         │
└─────────────────────────────────────────┘
```

**Règles Affichage** :
- Section "Urgent" visible SEULEMENT si ruptures > 0
- Section "Attention" visible SEULEMENT si produits alerte > 0
- Couleurs : Rouge (rupture), Orange (alerte), Vert (OK)
- Indicateur tendance taux de service (vs semaine précédente)

**Bloc 2 : Performance Ventes** (Priorité 2)
```
┌─────────────────────────────────────────┐
│  💰 VENTES                              │
├─────────────────────────────────────────┤
│  Aujourd'hui :    385 000 FCFA          │
│  Objectif jour :  350 000 FCFA ▲ (+10%) │
│                                         │
│  Semaine :      2 150 000 FCFA          │
│  Vs sem. préc : 1 980 000 FCFA ▲ (+8.6%)│
│                                         │
│  Mois :         8 750 000 FCFA          │
│  Objectif mois: 12 000 000 FCFA (73%)   │
│                                         │
│  📊 [Graphique CA 7 derniers jours]     │
│                                         │
└─────────────────────────────────────────┘
```

**Règles Affichage** :
- CA jour actualisé temps réel (si ventes enregistrées)
- Comparaison toujours avec période équivalente précédente
- Barre progression objectif mois
- Graphique simple (courbe ou barres) 7 jours glissants

**Bloc 3 : Valorisation & Trésorerie** (Priorité 3)
```
┌─────────────────────────────────────────┐
│  💵 VALORISATION STOCK                  │
├─────────────────────────────────────────┤
│  Valeur stock actuel : 12 500 000 FCFA  │
│  CA mensuel :          45 000 000 FCFA  │
│  Ratio :               27.8%            │
│                                         │
│  ⚠️ Stock élevé : 2.5M FCFA bloqués     │
│     dans produits rotation lente        │
│                                         │
│  💡 Opportunité libérer trésorerie      │
│     [Voir recommandations]              │
│                                         │
└─────────────────────────────────────────┘
```

**Règles Affichage** :
- Alerte si ratio stock/CA > 25% (seuil configurable)
- Identification automatique stock dormant
- Lien vers recommandations optimisation

**Bloc 4 : Alertes Récentes** (Priorité 4)
```
┌─────────────────────────────────────────┐
│  🔔 ALERTES RÉCENTES (24H)              │
├─────────────────────────────────────────┤
│  🔴 Farine 50kg : Rupture imminente (1j)│
│  🔴 Huile 20L : Rupture effective       │
│  ⚠️ Riz 25kg : Stock faible (4j)        │
│  ⚠️ Sucre 50kg : Stock faible (6j)      │
│                                         │
│  → [Voir toutes les alertes]            │
└─────────────────────────────────────────┘
```

**Règles Affichage** :
- Maximum 5 alertes affichées (les plus critiques)
- Tri par sévérité (Rupture > Alerte) puis par date
- Clic sur alerte → Détail produit + recommandation

### 4.2 Dashboard "Gestion Stock Détaillée"

**Objectif** : Analyse approfondie de la situation stock, produit par produit.

**Section 1 : Vue Tabulaire Produits**

**Filtres Disponibles** :
- Statut : Tous / Rupture / Alerte / Normal / Surstock
- Catégorie : Toutes / Sélection catégorie
- Recherche texte : Code ou désignation produit
- Tri : Stock actuel, Couverture jours, CA, Rotation

**Colonnes Affichées** :
```
┌──────┬─────────────────┬────────┬──────────┬───────────┬─────────┬────────┐
│Statut│ Produit         │Stock   │Couverture│Vente Moy  │Rotation │Actions │
│      │                 │Actuel  │(jours)   │(jour)     │         │        │
├──────┼─────────────────┼────────┼──────────┼───────────┼─────────┼────────┤
│  🔴  │ Farine 50kg     │   0    │    0     │    12     │   8.5   │ [📋]   │
│  ⚠️  │ Riz 25kg        │  45    │    4     │    11     │   12.3  │ [📋]   │
│  🟢  │ Huile 20L       │  230   │   21     │    11     │   6.8   │ [📋]   │
│  ⚠️  │ Sucre 50kg      │  38    │    6     │     6     │   9.2   │ [📋]   │
│  🟠  │ Lait poudre 500g│  850   │   78     │    11     │   1.2   │ [📋]   │
└──────┴─────────────────┴────────┴──────────┴───────────┴─────────┴────────┘
```

**Règles Affichage** :
- Couleur statut : Rouge (rupture), Orange (alerte), Vert (normal), Gris (surstock)
- Couverture jours : Bold si < 7 jours
- Rotation : Rouge si < 3, Orange si 3-6, Vert si > 6
- Action [📋] : Ouvre panneau latéral détail produit

**Section 2 : Détail Produit (Panneau Latéral)**

Ouvert au clic sur une ligne produit.

**Informations Affichées** :
```
┌─────────────────────────────────────────────────────┐
│  FARINE 50KG (Réf: F-001)                          │
├─────────────────────────────────────────────────────┤
│  Catégorie : Farine                                │
│  Fournisseur : Moulin Dakar (Délai: 3 jours)      │
│                                                     │
│  📊 STOCK                                          │
│  ├─ Actuel : 0 sacs      🔴 RUPTURE               │
│  ├─ Minimum : 10 sacs                             │
│  ├─ Maximum : 100 sacs                            │
│  └─ Couverture : 0 jours                          │
│                                                     │
│  📈 VENTES (30 derniers jours)                     │
│  ├─ Quantité : 360 sacs                           │
│  ├─ CA : 7 200 000 FCFA                           │
│  ├─ Vente moy/jour : 12 sacs                      │
│  └─ Tendance : ▲ +15% vs mois précédent          │
│                                                     │
│  💰 VALORISATION                                   │
│  ├─ Prix achat : 18 000 FCFA                      │
│  ├─ Prix vente : 20 000 FCFA                      │
│  ├─ Marge unitaire : 2 000 FCFA (11.1%)           │
│  └─ Marge mois : 720 000 FCFA                     │
│                                                     │
│  🔄 PERFORMANCE                                    │
│  ├─ Rotation annuelle : 8.5 (Bon)                 │
│  ├─ Classement : Produit A (Top 10 CA)            │
│  └─ Taux service : 92%                            │
│                                                     │
│  💡 RECOMMANDATION                                 │
│  🔴 ACTION URGENTE                                 │
│  Commander immédiatement 80 sacs                   │
│  (Couverture 7 jours + sécurité)                  │
│  Coût : 1 440 000 FCFA                            │
│  [Voir détail calcul]                             │
│                                                     │
│  📊 [Graphique historique stock 90 jours]          │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Règles Métier Recommandation** :
```
Quantité recommandée = 
  (Vente moy quotidienne × Couverture souhaitée) 
  + Stock sécurité 
  - Stock actuel

Paramètres :
  - Couverture souhaitée : 15 jours (par défaut, configurable)
  - Stock sécurité : 20% quantité calculée (buffer aléas)
  
Exemple Farine 50kg :
  Vente moy : 12 sacs/jour
  Couverture : 15 jours
  Besoin : 12 × 15 = 180 sacs
  Sécurité : 180 × 0.2 = 36 sacs
  Total : 180 + 36 = 216 sacs
  Stock actuel : 0
  À commander : 216 sacs
  
  Ajustement MOQ (Minimum Order Quantity) :
  Si fournisseur vend par palettes de 80 sacs
  → Commander 3 palettes = 240 sacs (arrondi supérieur)
```

### 4.3 Dashboard "Analyse Ventes"

**Objectif** : Comprendre les performances commerciales et identifier les leviers de croissance.

**Section 1 : Vue Temporelle CA**

**Graphique Principal** : Évolution CA sur période sélectionnable
```
Période sélectionnable :
  - 7 derniers jours (par jour)
  - 30 derniers jours (par jour)
  - 12 derniers mois (par mois)
  - Année en cours vs année précédente (par mois)

Type graphique : Courbe avec points
Affichage : CA + Objectif (ligne pointillée) + Période précédente (comparaison)
```

**Métriques Associées** :
- CA période sélectionnée
- Variation vs période précédente (%)
- Meilleur jour/mois
- Plus mauvais jour/mois
- Moyenne quotidienne/mensuelle

**Section 2 : Top Produits**

**Top 10 Produits par CA**
```
┌────┬──────────────┬──────────────┬─────────┬──────────┬─────────┐
│ #  │ Produit      │ CA Période   │ Marge   │ Quantité │ Trend   │
├────┼──────────────┼──────────────┼─────────┼──────────┼─────────┤
│ 1  │ Riz 25kg     │ 2 800 000 F  │ 340K F  │  350 sacs│ ▲ +8%   │
│ 2  │ Farine 50kg  │ 2 100 000 F  │ 280K F  │  250 sacs│ ▲ +3%   │
│ 3  │ Huile 20L    │ 1 900 000 F  │ 250K F  │  190 bid │ ▼ -5%   │
│ 4  │ Sucre 50kg   │ 1 500 000 F  │ 180K F  │  140 sacs│ → 0%    │
│ 5  │ Lait poudre  │ 1 200 000 F  │ 150K F  │  280 pqts│ ▲ +12%  │
│... │              │              │         │          │         │
└────┴──────────────┴──────────────┴─────────┴──────────┴─────────┘

💡 Insight automatique :
"Ces 10 produits représentent 78% de votre CA total"
"Focus sur ces références pour maximiser impact"
```

**Top 10 Produits par Marge**
```
Même structure, trié par Marge décroissante

💡 Insight automatique :
"Produits les plus rentables : Prioriser disponibilité"
"Opportunité : Promouvoir produits forte marge"
```

**Section 3 : Analyse Catégories**

**Répartition CA par Catégorie** (Graphique Camembert)
```
Catégories avec % CA :
  - Riz : 32%
  - Farine : 28%
  - Huile : 18%
  - Sucre : 12%
  - Autres : 10%

Clic sur catégorie → Drill-down détail produits catégorie
```

**Performance Catégories** (Tableau)
```
┌─────────────┬──────────┬─────────┬──────────┬──────────┐
│ Catégorie   │ CA       │ Marge % │ Rotation │ Trend    │
├─────────────┼──────────┼─────────┼──────────┼──────────┤
│ Riz         │ 3.2M F   │  8.5%   │   12.3   │ ▲ +6%    │
│ Farine      │ 2.8M F   │ 11.2%   │    8.7   │ ▲ +2%    │
│ Huile       │ 1.8M F   │  9.8%   │    6.5   │ ▼ -4%    │
│ Sucre       │ 1.2M F   │  7.2%   │    9.1   │ → 0%     │
└─────────────┴──────────┴─────────┴──────────┴──────────┘
```

### 4.4 Dashboard "Prédictions & Recommandations"

**Objectif** : Anticiper les besoins et guider les décisions du gérant.

**Section 1 : Prédiction Ruptures 15 Jours**

**Liste Produits Risque Rupture**
```
┌──────────────────┬───────┬────────────┬───────────────┬──────────────┐
│ Produit          │Stock  │Couverture  │Rupture Prévue │Action        │
├──────────────────┼───────┼────────────┼───────────────┼──────────────┤
│ Farine 50kg      │  45   │   4 jours  │ 18 Oct (4j)   │🔴 URGENT     │
│ Huile 20L        │  78   │   7 jours  │ 21 Oct (7j)   │⚠️ PRÉVOIR    │
│ Riz 25kg         │ 165   │  15 jours  │ 29 Oct (15j)  │📋 PLANIFIER  │
│ Sucre 50kg       │  85   │  14 jours  │ 28 Oct (14j)  │📋 PLANIFIER  │
└──────────────────┴───────┴────────────┴───────────────┴──────────────┘

💡 Insight :
"4 produits nécessitent approvisionnement dans 15 jours"
"2 actions urgentes cette semaine"
```

**Règles Calcul Prédiction** :
```
Date rupture prévue = Date actuelle + (Stock actuel / Vente moy quotidienne)

Avec ajustements :
  - Prise en compte tendance (croissance/décroissance ventes)
  - Exclusion jours sans vente (dimanches si pattern détecté)
  - Coefficient saisonnalité (si historique > 1 an)

Niveau urgence :
  - 🔴 URGENT : Rupture < 7 jours
  - ⚠️ PRÉVOIR : Rupture 7-15 jours
  - 📋 PLANIFIER : Rupture 15-30 jours
```

**Section 2 : Recommandations Achat Groupées**

**Bon de Commande Suggéré par Fournisseur**
```
┌──────────────────────────────────────────────────────────────┐
│  FOURNISSEUR : MOULIN DAKAR                                  │
│  Délai livraison : 3 jours                                   │
├──────────────────────────────────────────────────────────────┤
│  Produit            Qté Suggérée    Prix Unit.    Total      │
├──────────────────────────────────────────────────────────────┤
│  Farine 50kg            80 sacs      18 000 F   1 440 000 F │
│  Semoule 25kg           30 sacs      12 000 F     360 000 F │
│  Couscous 5kg           50 pqts       5 000 F     250 000 F │
├──────────────────────────────────────────────────────────────┤
│  TOTAL COMMANDE                                  2 050 000 F │
│                                                               │
│  💰 Trésorerie actuelle : 3 200 000 F             ✅ OK      │
│  📅 Livraison prévue : 17 Oct                                │
│  ⏰ Stock suffit jusqu'à : 16 Oct                  ✅ OK      │
│                                                               │
│  💡 Optimisation : Commande groupée = -15% frais livraison   │
│                                                               │
│  [✅ Valider]  [✏️ Modifier Quantités]  [❌ Ignorer]         │
└──────────────────────────────────────────────────────────────┘
```

**Logique Recommandation** :
```
Pour chaque fournisseur :
  1. Identifier tous produits nécessitant réappro < 15j
  2. Calculer quantité optimale par produit (couverture 15-30j)
  3. Vérifier contraintes :
     - MOQ (Minimum Order Quantity) fournisseur
     - Trésorerie disponible
     - Délai livraison vs date rupture
  4. Grouper commande même fournisseur (optimisation frais)
  5. Prioriser produits :
     - Classe A (CA) en priorité
     - Urgence (date rupture proche)
     - Rentabilité (marge élevée)

Validation automatique possible si :
  - Trésorerie suffisante
  - Délai livraison compatible
  - Aucune commande en cours même fournisseur
```

**Section 3 : Opportunités Optimisation Stock**

**Produits Surstockés** (Capital immobilisé)
```
┌───────────────────┬──────────┬───────────┬────────────┬────────────┐
│ Produit           │ Stock    │ Couverture│ Valeur     │ Action     │
├───────────────────┼──────────┼───────────┼────────────┼────────────┤
│ Lait poudre 500g  │  850 pqts│  78 jours │ 850 000 F  │ Promotion  │
│ Thé vert 100g     │  320 pqts│  65 jours │ 240 000 F  │ Déstockage │
│ Café soluble 200g │  180 pots│  55 jours │ 450 000 F  │ Promotion  │
├───────────────────┴──────────┴───────────┼────────────┼────────────┤
│ TOTAL CAPITAL IMMOBILISÉ INUTILEMENT     │ 1 540 000 F│            │
└──────────────────────────────────────────┴────────────┴────────────┘

💡 Recommandations :
"Lancer promotion -10% sur lait poudre pour écouler"
"Réduire achats thé vert prochains 2 mois"
"Opportunité libérer 1.5M FCFA trésorerie"
```

**Critères Surstock** :
```
Produit en surstock si :
  - Couverture > 60 jours
  ET
  - Rotation < 3 (tourne < 3 fois/an)
  OU
  - Aucune vente 30 derniers jours

Actions suggérées :
  - Promotion commerciale (écoulement stock)
  - Arrêt temporaire achat produit
  - Considérer déréférencement si aucune vente 90j
```

---

## 5. SYSTÈME D'ALERTING - LOGIQUE MÉTIER

### 5.1 Principe Général

**Objectif** : Informer proactivement le gérant des situations nécessitant action, AVANT qu'elles deviennent critiques.

**Canaux d'Alerte** :
- WhatsApp (prioritaire - taux ouverture 98%)
- Email (secondaire)
- Notification in-app (plateforme)

**Niveaux de Sévérité** :
- 🔴 **CRITIQUE** : Action immédiate requise (< 24h)
- ⚠️ **IMPORTANT** : Action rapide souhaitable (< 3 jours)
- 📋 **INFO** : Notification pour information (action planifiable)

### 5.2 Types d'Alertes Métier

#### ALERTE 1 : Rupture de Stock

**Déclenchement** :
```
Condition : Stock actuel d'un produit = 0

Fréquence vérification : Temps réel (dès mouvement stock)

Message type :
  🔴 RUPTURE STOCK
  
  Produit : Farine 50kg
  Stock actuel : 0 sacs
  Ventes perdues aujourd'hui : 12 sacs (estimation)
  Impact CA : 240 000 FCFA
  
  💡 Action recommandée :
  Commander 80 sacs immédiatement
  Fournisseur : Moulin Dakar (Délai 3j)
  
  👉 Voir détails : [Lien]
```

**Destinataires** : Gérant + Responsable achats (si configuré)

**Répétition** : 1 fois/jour tant que rupture active

**Désactivation** : Automatique dès stock > 0

#### ALERTE 2 : Stock Faible (Rupture Imminente)

**Déclenchement** :
```
Condition : 
  Stock actuel < (Vente moyenne quotidienne × Seuil jours alerte)
  ET Stock actuel > 0

Paramètre :
  Seuil jours alerte = 7 jours (par défaut, configurable par produit)

Exemple :
  Produit : Riz 25kg
  Stock : 45 sacs
  Vente moy : 11 sacs/jour
  Seuil : 7 jours
  Calcul : 45 < (11 × 7 = 77) → ALERTE

Fréquence vérification : 1 fois/jour (matin 8h)
```

**Message type** :
```
⚠️ STOCK FAIBLE

Produit : Riz 25kg
Stock actuel : 45 sacs
Vente moyenne : 11 sacs/jour
🔴 RUPTURE DANS 4 JOURS (18 Oct)

💡 Action suggérée :
Commander 165 sacs avant 15 Oct
(Couverture 15 jours)

👉 Voir recommandation : [Lien]
```

**Destinataires** : Gérant

**Répétition** : 
- 1ère alerte : J-7
- Rappel : J-3 (si aucune action)
- Rappel urgent : J-1 (si aucune action)

**Désactivation** : Dès commande passée OU stock réapprovisionné

#### ALERTE 3 : Prédiction Rupture Multiple (Alerte Groupée)

**Déclenchement** :
```
Condition : 
  >= 5 produits en situation "Stock Faible" simultanément

Fréquence : 1 fois/jour (matin 8h)
```

**Message type** :
```
⚠️ ALERTE STOCK - 12 PRODUITS EN SITUATION CRITIQUE

Urgences (< 3 jours) :
  • Farine 50kg : Rupture dans 2j
  • Huile 20L : Rupture dans 1j
  
À prévoir (3-7 jours) :
  • Riz 25kg : Rupture dans 4j
  • Sucre 50kg : Rupture dans 6j
  • Lait poudre : Rupture dans 5j
  
À planifier (7-15 jours) :
  • 7 autres produits
  
💡 Commandes suggérées :
  Moulin Dakar : 2.1M FCFA (3 produits)
  Import Riz : 1.8M FCFA (2 produits)
  
👉 Voir plan d'action : [Lien]
```

**Destinataires** : Gérant + Responsable achats

**Répétition** : 1 fois/jour jusqu'à résolution

#### ALERTE 4 : Baisse Performance (Taux de Service)

**Déclenchement** :
```
Condition :
  Taux de service semaine < Seuil objectif (95% par défaut)
  
Calcul taux service :
  (Jours sans rupture / 7 jours) × 100

Exemple :
  Semaine dernière : 3 jours avec ruptures
  Taux service : (4/7) × 100 = 57%
  Objectif : 95%
  → ALERTE

Fréquence : 1 fois/semaine (lundi matin - bilan semaine précédente)
```

**Message type** :
```
📉 BAISSE TAUX DE SERVICE

Semaine dernière : 57%
Objectif : 95% ▼ (-38 points)

Causes identifiées :
  • 3 jours avec ruptures (Farine, Riz, Huile)
  • Délai réapprovisionnement trop long

💡 Actions correctives :
  1. Augmenter stocks sécurité produits A
  2. Commander plus fréquemment (2×/semaine)
  3. Activer alertes anticipées (J-10)

👉 Voir analyse détaillée : [Lien]
```

**Destinataires** : Gérant

**Répétition** : 1 fois/semaine si problème persiste

#### ALERTE 5 : Opportunité Commerciale (Tendance)

**Déclenchement** :
```
Condition :
  Ventes produit en hausse >= 20% (vs même période mois précédent)
  OU
  Nouveau produit classe A (entre dans top 10 CA)

Fréquence : 1 fois/semaine (analyse tendances)
```

**Message type** :
```
📈 OPPORTUNITÉ COMMERCIALE

Produit : Lait poudre 500g

Performance :
  • Ventes : +35% vs mois dernier
  • Nouveau classement : #5 CA (était #12)
  • Marge : 12.5% (excellente)

💡 Recommandations :
  1. Augmenter stock sécurité (éviter rupture)
  2. Négocier prix achat (volume hausse)
  3. Mettre en avant (PLV, promo)

👉 Voir analyse : [Lien]
```

**Destinataires** : Gérant + Responsable commercial

**Répétition** : Unique (1 alerte par tendance identifiée)

### 5.3 Configuration Alertes (Interface Utilisateur)

**Fonctionnalité** : Le gérant peut personnaliser le système d'alerting.

**Paramètres Configurables** :

**Par Type d'Alerte** :
```
┌─────────────────────────────────────────────────────────┐
│ TYPE : Rupture de Stock                                 │
├─────────────────────────────────────────────────────────┤
│ Statut :  [🟢 Activée]  / [ ] Désactivée               │
│                                                         │
│ Sévérité : [🔴 Critique] ▼                             │
│                                                         │
│ Canaux :  [✓] WhatsApp                                 │
│           [✓] Email                                    │
│           [✓] Notification app                         │
│                                                         │
│ Destinataires :                                        │
│   • Gérant (vous) - WhatsApp: +221771234567           │
│   • Responsable achats - Email: achats@pme.sn         │
│   [+ Ajouter]                                          │
│                                                         │
│ Répétition : [1 fois/jour] ▼                           │
│                                                         │
│ Conditions spécifiques :                               │
│   [ ] Uniquement produits classe A                     │
│   [✓] Tous produits actifs                            │
│                                                         │
│ [💾 Enregistrer]  [🧪 Tester Alerte]                  │
└─────────────────────────────────────────────────────────┘
```

**Par Produit** (Personnalisation fine) :
```
┌─────────────────────────────────────────────────────────┐
│ PRODUIT : Farine 50kg                                   │
├─────────────────────────────────────────────────────────┤
│ Alertes personnalisées :                               │
│                                                         │
│ Seuil alerte stock faible : [10] jours                 │
│   (Par défaut : 7 jours)                               │
│                                                         │
│ Stock minimum absolu : [15] sacs                       │
│   Alerte critique si stock < cette valeur              │
│                                                         │
│ Priorité approvisionnement : [Haute] ▼                 │
│   (Produit classe A - CA important)                    │
│                                                         │
│ [💾 Enregistrer]                                       │
└─────────────────────────────────────────────────────────┘
```

**Règles Métier Configuration** :
- Impossible désactiver alertes critiques (rupture stock produits A)
- Minimum 1 destinataire par alerte activée
- Validation numéro WhatsApp (format international)
- Test alerte envoie notification factice (vérification configuration)

### 5.4 Historique Alertes

**Fonctionnalité** : Consultation alertes passées (audit, analyse).

**Interface** :
```
┌────────────────────────────────────────────────────────────────┐
│ HISTORIQUE ALERTES                                             │
├────────────────────────────────────────────────────────────────┤
│ Filtres : [Derniers 30 jours ▼] [Toutes sévérités ▼]         │
│                                                                │
├────────┬───────────────────┬──────────┬──────────┬────────────┤
│ Date   │ Type              │ Produit  │ Sévérité │ Statut     │
├────────┼───────────────────┼──────────┼──────────┼────────────┤
│ 14 Oct │ Rupture stock     │Farine50kg│    🔴    │ Résolue    │
│  8h15  │                   │          │          │ (14 Oct 14h│
│ 13 Oct │ Stock faible      │Riz 25kg  │    ⚠️    │ En cours   │
│  8h00  │                   │          │          │            │
│ 12 Oct │ Baisse perf.      │ -        │    📋    │ Résolue    │
│  9h00  │ (Taux service)    │          │          │ (13 Oct)   │
│ 11 Oct │ Opportunité com.  │Lait poudr│    📋    │ Notée      │
│  8h30  │ (Tendance hausse) │          │          │            │
└────────┴───────────────────┴──────────┴──────────┴────────────┘

💡 Statistiques période :
  • Total alertes : 24
  • Critiques : 5 (21%)
  • Résolues : 18 (75%)
  • Temps résolution moyen : 1.8 jours
```

**Détail Alerte** (clic sur ligne) :
```
┌─────────────────────────────────────────────────────────┐
│ DÉTAIL ALERTE #A-2024-10-14-001                        │
├─────────────────────────────────────────────────────────┤
│ Type : Rupture de Stock                                │
│ Produit : Farine 50kg                                  │
│ Sévérité : 🔴 Critique                                 │
│                                                         │
│ Déclenchée : 14 Oct 2024, 08:15                       │
│ Résolue : 14 Oct 2024, 14:30 (6h15 après)            │
│                                                         │
│ Contexte déclenchement :                               │
│   • Stock actuel : 0 sacs                             │
│   • Dernière vente : 14 Oct 07:45 (30 sacs)          │
│   • Ventes perdues estimées : 12 sacs (4h rupture)    │
│   • Impact CA estimé : 240 000 FCFA                   │
│                                                         │
│ Actions prises :                                       │
│   • Notification WhatsApp envoyée : ✅ 08:15          │
│   • Notification email envoyée : ✅ 08:16             │
│   • Commande passée : ✅ 14 Oct 10:00 (80 sacs)      │
│   • Réception stock : ✅ 14 Oct 14:30                │
│                                                         │
│ Résolution :                                           │
│   Stock réapprovisionné à 80 sacs                     │
│   Alerte automatiquement fermée                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 6. RAPPORTS & ANALYSES

### 6.1 Rapports Standards

#### RAPPORT 1 : Inventaire Stock Complet

**Fréquence** : À la demande (génération instantanée)

**Format** : Excel (.xlsx) - Tableau détaillé

**Contenu** :
```
Colonnes :
  • Code produit
  • Désignation
  • Catégorie
  • Stock actuel (quantité)
  • Unité de mesure
  • Prix achat unitaire
  • Valeur stock (quantité × prix achat)
  • Stock minimum
  • Stock maximum
  • Statut (Rupture/Alerte/Normal/Surstock)
  • Dernière mise à jour

Lignes :
  • Tous produits actifs
  • Triés par catégorie puis par code produit

Résumé (en bas) :
  • Nombre total produits : X
  • Valeur totale stock : Y FCFA
  • Produits en rupture : Z
  • Produits en alerte : W
```

**Usage** :
- Audit comptable annuel
- Bilan inventaire physique
- Analyse portefeuille produits

#### RAPPORT 2 : Synthèse Mensuelle Performance

**Fréquence** : Automatique (1er jour du mois, pour mois écoulé)

**Format** : PDF formaté (présentable actionnaires/banque)

**Contenu** :

**Page 1 - KPI Principaux** :
```
En-tête :
  Logo PME
  "Rapport Mensuel - [Mois Année]"
  Date génération

KPI Affichés (avec graphiques) :
  • CA mensuel vs objectif (jauge)
  • Évolution CA vs mois précédent (%)
  • Marge brute (montant + %)
  • Taux de service (%)
  • Nombre commandes traitées
  • Panier moyen

Comparaisons :
  • vs Mois précédent
  • vs Même mois année précédente (si dispo)
```

**Page 2 - Performance Commerciale** :
```
Top 10 Produits CA :
  Tableau + graphique barres
  
Top 10 Clients (si données) :
  Tableau avec CA, nb commandes, panier moyen
  
Évolution CA :
  Graphique courbe 12 derniers mois
  Identification tendance (croissance, stabilité, déclin)
```

**Page 3 - Santé Stock** :
```
Statistiques :
  • Valeur stock totale
  • Évolution vs mois précédent
  • Taux rotation global
  • Nombre ruptures mois (total jours rupture)
  
Points d'attention :
  • Liste produits rupture récurrente
  • Liste produits surstock (>60j couverture)
  • Liste produits rotation lente (<3/an)
```

**Page 4 - Recommandations** :
```
Analyse automatique :
  
  ✅ Points positifs :
    • CA +8% vs mois dernier (tendance positive)
    • Marge stable 10.5% (objectif 10%)
    • Taux service 93% (proche objectif 95%)
  
  ⚠️ Points d'amélioration :
    • 8 ruptures constatées (objectif: 0)
    • 3 produits surstock immobilisant 1.2M FCFA
    • Rotation catégorie "Thé/Café" faible (4.2)
  
  💡 Actions suggérées :
    1. Augmenter stocks sécurité produits A (éviter ruptures)
    2. Lancer promotions produits surstock
    3. Revoir politique achat catégorie faible rotation
    4. Objectif CA mois prochain : +5% (47.2M FCFA)
```

**Envoi** :
- Email automatique gérant
- WhatsApp lien téléchargement PDF
- Archivage automatique dans plateforme

#### RAPPORT 3 : Analyse Ventes Détaillée (Période Personnalisée)

**Fréquence** : À la demande

**Format** : Excel (.xlsx) multi-onglets

**Contenu** :

**Onglet 1 - Ventes Détail Transaction** :
```
Colonnes :
  • Date vente
  • Numéro commande
  • Client (si disponible)
  • Produit (code + désignation)
  • Quantité
  • Prix unitaire vente
  • Montant total
  • Prix achat unitaire
  • Marge unitaire
  • Marge %
  • Statut commande

Filtres :
  • Période sélectionnable (date début - date fin)
  • Catégorie (optionnel)
  • Produit (optionnel)
  • Client (optionnel)

Usage : Analyse fine, export comptabilité
```

**Onglet 2 - Synthèse par Produit** :
```
Colonnes :
  • Produit
  • Quantité vendue
  • CA total
  • Marge brute
  • Taux marge %
  • Nombre commandes
  • Panier moyen
  • Tendance vs période précédente

Tri : CA décroissant
Usage : Identifier produits stars
```

**Onglet 3 - Synthèse par Client** (si données clients) :
```
Colonnes :
  • Client
  • Nombre commandes
  • CA total
  • Panier moyen
  • Marge brute
  • Produits achetés (liste top 3)

Tri : CA décroissant
Usage : Identifier meilleurs clients
```

**Onglet 4 - Évolution Temporelle** :
```
Tableau pivot :
  Lignes : Jours/Semaines/Mois (selon période)
  Colonnes : CA, Quantité, Marge
  
Graphiques associés :
  • Courbe évolution CA quotidien
  • Barres CA par semaine
  • Heatmap ventes (jour × heure si données)

Usage : Identifier patterns saisonnalité, jours forts
```

---

## 7. AGENT IA - CAS D'USAGE MÉTIER

### 7.1 Vision Agent IA (Futur)

**Objectif** : Assistant intelligent conversationnel permettant au gérant d'interroger ses données en langage naturel et recevoir analyses actionnables.

**Principe** :
```
Gérant pose question en français simple
            ↓
Agent IA (LLM) comprend intention
            ↓
Agent interroge vues SQL pertinentes
            ↓
Agent analyse données + contexte métier
            ↓
Agent répond en français + recommandations
```

### 7.2 Cas d'Usage Métier Agent IA

#### CU-IA-01 : Diagnostic Situation Stock

**Interaction Type** :
```
Gérant : "Donne-moi un diagnostic de mon stock"

Agent IA interroge :
  - Vue stock global
  - Vue produits rupture
  - Vue produits alerte
  - Fonction calcul performance stock

Agent répond :
  📊 DIAGNOSTIC STOCK
  
  Situation globale : ⚠️ ATTENTION NÉCESSAIRE
  
  Votre stock actuel :
    • Valeur totale : 12.5M FCFA
    • 180 références actives
  
  Points d'alerte :
    🔴 8 produits en rupture (4% références)
       Dont 3 produits classe A → Impact CA critique
    
    ⚠️ 23 produits < 7 jours (13% références)
       Dont 7 produits classe A → Risque rupture
  
    📦 Taux de service : 87% (objectif 95%)
       Baisse de 5 points vs semaine dernière
  
  💡 Mes recommandations urgentes :
    1. Commander immédiatement 3 produits A en rupture
       (Farine, Riz, Huile) = 4.2M FCFA
    2. Planifier réappro 7 produits A en alerte
       avant fin semaine = 2.8M FCFA
    3. Augmenter stocks sécurité produits A (+20%)
       pour éviter ruptures récurrentes
  
  Veux-tu que je détaille un produit spécifique ?
  Ou que je génère les bons de commande suggérés ?
```

#### CU-IA-02 : Analyse Performance Commerciale

**Interaction Type** :
```
Gérant : "Comment vont mes ventes ce mois ?"

Agent IA interroge :
  - Vue ventes période
  - Vue évolution CA
  - Vue top produits
  - Fonction calcul tendances

Agent répond :
  📈 ANALYSE VENTES OCTOBRE 2024
  
  Performance globale : 🟢 EXCELLENTE
  
  Chiffres clés :
    • CA du mois : 8.75M FCFA (14 jours écoulés)
    • Projection fin mois : 18.8M FCFA
    • Objectif : 17M FCFA → ✅ Dépassement +10%
  
  Évolution :
    • vs Septembre : +12% (très bonne dynamique)
    • vs Octobre 2023 : +18% (croissance année)
  
  Produits moteurs :
    🏆 Riz 25kg : 2.8M FCFA (+15%)
       → Tendance forte, assurer disponibilité
    🏆 Farine 50kg : 2.1M FCFA (+8%)
       → Stable, pilier CA
    📈 Lait poudre : 1.2M FCFA (+35% !)
       → Nouveau star, opportunité à exploiter
  
  💡 Opportunités identifiées :
    1. Lait poudre en forte croissance
       → Augmenter stock +30%, négocier prix achat
    2. Catégorie "Produits laitiers" globale +28%
       → Élargir gamme (yaourts, fromages ?)
    3. Tendance CA positive (+12%)
       → Moment opportun investir marketing
  
  Veux-tu plus de détails sur un produit ?
  Ou une analyse par client ?
```

#### CU-IA-03 : Prédiction & Planification

**Interaction Type** :
```
Gérant : "Qu'est-ce que je dois commander cette semaine ?"

Agent IA interroge :
  - Vue prédiction ruptures
  - Vue stocks actuels
  - Fonction calcul quantité optimale
  - Données fournisseurs (délais)

Agent répond :
  📋 PLAN APPROVISIONNEMENT SEMAINE
  
  Urgences (< 3 jours) :
    🔴 Farine 50kg
       • Stock : 12 sacs (1 jour restant)
       • Commander : 80 sacs
       • Fournisseur : Moulin Dakar (3j délai)
       • Coût : 1.44M FCFA
       • 🚨 COMMANDE AUJOURD'HUI IMPÉRATIF
    
    🔴 Huile 20L
       • Stock : 18 bidons (2 jours restants)
       • Commander : 60 bidons
       • Fournisseur : Oleosine (2j délai)
       • Coût : 1.5M FCFA
       • 🚨 COMMANDE DEMAIN MAX
  
  À prévoir (3-7 jours) :
    ⚠️ Riz 25kg, Sucre 50kg, Lait poudre
       Total : 2.8M FCFA
       Commande conseillée : Jeudi/Vendredi
  
  💰 Optimisation :
    Si tu commandes Farine + Semoule (même fournisseur)
    → Livraison gratuite (économie 50K FCFA)
  
  Budget nécessaire semaine : 7.2M FCFA
  Trésorerie actuelle : 9.5M FCFA
  ✅ Budget OK
  
  Veux-tu que je génère les bons de commande ?
  Ou que je liste les produits par fournisseur ?
```

#### CU-IA-04 : Analyse Comparative

**Interaction Type** :
```
Gérant : "Compare mes résultats septembre vs octobre"

Agent IA interroge :
  - Vue ventes septembre
  - Vue ventes octobre (en cours)
  - Fonctions comparaison périodes

Agent répond :
  📊 COMPARAISON SEPTEMBRE vs OCTOBRE 2024
  
  ┌─────────────────┬────────────┬────────────┬──────────┐
  │ Indicateur      │ Septembre  │ Octobre(14j│ Évolution│
  ├─────────────────┼────────────┼────────────┼──────────┤
  │ CA              │ 15.8M FCFA │ 8.75M FCFA │  +12% ✅ │
  │ Marge brute     │ 1.58M FCFA │ 0.92M FCFA │  +16% ✅ │
  │ Taux service    │    92%     │    87%     │   -5% ⚠️ │
  │ Nb ruptures     │     5      │     8      │  +60% ❌ │
  │ Rotation moy    │    8.2     │    8.5     │   +4% ✅ │
  └─────────────────┴────────────┴────────────┴──────────┘
  
  Analyse :
  
  ✅ Points positifs :
    • CA en hausse (+12%) malgré mi-mois
    • Marge améliorée (+16%) = meilleure rentabilité
    • Rotation légèrement meilleure
  
  ⚠️ Points vigilance :
    • Taux service en baisse (92% → 87%)
    • Plus de ruptures (5 → 8)
    • Cause probable : Forte demande + stocks pas suivis
  
  💡 Actions correctives :
    1. Ajuster stocks sécurité produits A (+20%)
    2. Augmenter fréquence commandes (2×/sem)
    3. Activer alertes anticipées (J-10 au lieu J-7)
  
  Avec ces ajustements, objectif novembre :
    • CA : 19M FCFA (+20% vs oct projection)
    • Taux service : 95% (objectif atteint)
    • Zéro rupture produits A
  
  Tu veux simuler l'impact financier de ces actions ?
```

#### CU-IA-05 : Recherche & Exploration

**Interaction Type** :
```
Gérant : "Quels sont mes produits qui ne tournent pas ?"

Agent IA interroge :
  - Vue rotation produits
  - Vue ventes historique
  - Fonction identification produits dormants

Agent répond :
  🐌 PRODUITS À FAIBLE ROTATION
  
  Critère : Rotation < 3 (tourne < 3 fois/an)
  
  Produits identifiés (12) :
  
  Top 3 problèmes :
    1. Thé vert 100g
       • Rotation : 1.8
       • Stock : 320 pqts (65 jours)
       • Valeur immobilisée : 240K FCFA
       • Dernière vente : Il y a 12 jours
       💡 Action : Promotion -15% écoulement
    
    2. Café soluble 200g
       • Rotation : 2.1
       • Stock : 180 pots (55 jours)
       • Valeur immobilisée : 450K FCFA
       • Dernière vente : Il y a 8 jours
       💡 Action : Arrêter achat 2 mois
    
    3. Confiture fraise 500g
       • Rotation : 1.2
       • Stock : 95 pots (120 jours !)
       • Valeur immobilisée : 285K FCFA
       • Dernière vente : Il y a 18 jours
       💡 Action : Déstockage agressif ou déréférencer
  
  Impact total :
    • 12 produits faible rotation
    • 1.54M FCFA capital immobilisé
    • Opportunité libérer trésorerie
  
  💡 Plan d'action suggéré :
    1. Semaines 1-2 : Promotions produits 1-5
    2. Semaine 3 : Évaluation résultats
    3. Semaine 4 : Déréférencement produits 0 vente
  
  Impact trésorerie prévu : +800K FCFA libérés
  
  Tu veux que je génère les fiches promo ?
```

### 7.3 Préparation Infrastructure Agent IA

**Prérequis Techniques** (pour future intégration) :

#### Vues SQL Optimisées Agent IA
```
Les vues destinées à l'agent IA doivent :
  - Être documentées (commentaires explicites)
  - Retourner données contextuelles riches
  - Inclure métadonnées métier (définitions KPI)
  - Format structuré (JSON si possible)
  - Performance optimale (< 500ms réponse)

Exemple vue pour agent :
  v_ai_diagnostic_stock
  → Retourne :
     • Indicateurs globaux (valeur, nb références, taux service)
     • Listes produits par statut (rupture, alerte, normal)
     • KPI performance (rotation, couverture)
     • Métadonnées (définitions, seuils, objectifs)
     • Contexte temporel (évolution, tendances)
```

#### Catalogue Fonctions Métier
```
Documentation exhaustive pour chaque fonction :
  
  Nom : fn_calc_quantite_reappro
  
  Description :
    Calcule la quantité optimale à commander pour un produit
    basée sur historique ventes, stock actuel, couverture souhaitée
  
  Paramètres :
    - produit_id (UUID) : ID du produit
    - couverture_jours (INTEGER) : Nb jours couverture souhaités (défaut 15)
    - inclure_securite (BOOLEAN) : Ajouter stock sécurité 20% (défaut true)
  
  Retour :
    - quantite_commander (DECIMAL)
    - justification (TEXT) : Explication calcul
    - cout_estime (DECIMAL)
    - date_livraison_prevue (DATE)
  
  Logique métier :
    1. Calcul vente moyenne quotidienne (30 derniers jours)
    2. Quantité = Vente moy × Couverture souhaitée
    3. Ajout stock sécurité (+20%)
    4. Soustraction stock actuel
    5. Arrondi selon MOQ fournisseur
  
  Cas d'usage agent IA :
    "Combien commander de Farine ?" → Appel fonction → Réponse contextualisée
```

#### API Endpoints Dédiés Agent
```
Endpoints spécifiques pour agent IA :
  
  GET /api/ai/context/stock
  → Contexte complet stock (pour analyse globale)
  
  GET /api/ai/context/ventes?periode=30d
  → Contexte complet ventes période
  
  POST /api/ai/query
  Body : { "question": "Que dois-je commander ?", "context": {...} }
  → Interrogation intelligente avec contexte
  
  GET /api/ai/recommendations?type=reappro
  → Recommandations actionnables
  
Avantages :
  - Agent IA n'interroge pas directement base
  - Contrôle accès et permissions
  - Logs requêtes agent (audit)
  - Rate limiting (protection ressources)
```

---

## 8. RÈGLES DE GESTION SUPPLY CHAIN

### 8.1 Règles Calcul Stock

**RG-S-01 : Stock Actuel**
```
Stock actuel = Stock initial + Σ Entrées - Σ Sorties

Entrées :
  - Réceptions fournisseurs
  - Retours clients
  - Ajustements inventaire positifs

Sorties :
  - Ventes clients
  - Casse/Péremption
  - Ajustements inventaire négatifs

Mise à jour : Temps réel à chaque mouvement
```

**RG-S-02 : Stock de Sécurité**
```
Stock sécurité = Vente moyenne quotidienne × Délai réappro × Coefficient risque

Coefficient risque :
  - Produit classe A (CA critique) : 1.5 (sécurité +50%)
  - Produit classe B : 1.2 (sécurité +20%)
  - Produit classe C : 1.0 (sécurité standard)

Exemple Farine 50kg (classe A) :
  Vente moy : 12 sacs/jour
  Délai réappro : 3 jours
  Coefficient : 1.5
  Stock sécurité : 12 × 3 × 1.5 = 54 sacs
```

**RG-S-03 : Point de Commande**
```
Point commande = (Vente moyenne quotidienne × Délai réappro) + Stock sécurité

Déclenchement alerte : Stock actuel < Point de commande

Exemple Farine 50kg :
  Vente moy : 12 sacs/jour
  Délai réappro : 3 jours
  Stock sécurité : 54 sacs
  Point commande : (12 × 3) + 54 = 90 sacs
  
  → Alerte dès que stock < 90 sacs
```

**RG-S-04 : Couverture Stock**
```
Couverture (jours) = Stock actuel / Vente moyenne quotidienne

Interprétation :
  - Couverture < 7 jours : Alerte (risque rupture)
  - Couverture 7-30 jours : Normal
  - Couverture 30-60 jours : Élevé (surveiller)
  - Couverture > 60 jours : Surstock (action corrective)
```

**RG-S-05 : Valorisation Stock**
```
Méthode : FIFO (First In, First Out) par défaut

Valeur stock produit = Σ (Quantité lot × Prix achat lot)

Si pas historique lots (MVP) :
  Valeur stock = Stock actuel × Prix achat unitaire moyen

Valeur totale stock = Σ Valeur stock tous produits
```

### 8.2 Règles Calcul Ventes

**RG-V-01 : Chiffre d'Affaires**
```
CA = Σ (Quantité vendue × Prix unitaire vente)

Par période (jour, semaine, mois, année)
Par produit
Par catégorie
Par client (si données disponibles)

Exclusions :
  - Ventes annulées
  - Retours clients (CA négatif)
```

**RG-V-02 : Marge Commerciale**
```
Marge unitaire = Prix vente - Prix achat

Marge brute période = Σ (Quantité vendue × Marge unitaire)

Taux marge = (Marge brute / CA) × 100

Exemple :
  Ventes Farine octobre : 250 sacs
  Prix vente : 20 000 F/sac
  Prix achat : 18 000 F/sac
  
  CA : 250 × 20000 = 5 000 000 F
  Marge unitaire : 20000 - 18000 = 2 000 F
  Marge brute : 250 × 2000 = 500 000 F
  Taux marge : (500000 / 5000000) × 100 = 10%
```

**RG-V-03 : Panier Moyen**
```
Panier moyen = CA total période / Nombre commandes période

Interprétation :
  - Augmentation panier : Clients achètent plus (bon signe)
  - Diminution panier : Vigilance (perte pouvoir achat ?)

Exemple :
  CA mois : 15.8M FCFA
  Nb commandes : 320
  Panier moyen : 15800000 / 320 = 49 375 FCFA
```

**RG-V-04 : Tendance Ventes**
```
Tendance = ((Ventes période N - Ventes période N-1) / Ventes période N-1) × 100

Interprétation :
  - Tendance > +10% : Croissance forte
  - Tendance 0 à +10% : Croissance modérée
  - Tendance -5% à 0% : Stabilité
  - Tendance < -5% : Déclin (action requise)

Calcul sur minimum 3 périodes pour fiabilité
```

### 8.3 Règles Performance

**RG-P-01 : Taux de Service**
```
Méthode 1 (Disponibilité produit) :
  Taux service = (Jours sans rupture / Total jours période) × 100

Méthode 2 (Satisfaction commande) :
  Taux service = (Quantité livrée / Quantité commandée) × 100

MVP : Utiliser Méthode 1 (plus simple)

Objectif : >= 95%
```

**RG-P-02 : Taux de Rotation**
```
Rotation = Quantité vendue période / Stock moyen période

Stock moyen = (Stock début période + Stock fin période) / 2

Ou si données quotidiennes :
  Stock moyen = Moyenne stocks quotidiens période

Interprétation :
  - Rotation > 12 : Excellent (> 1 fois/mois)
  - Rotation 6-12 : Bon
  - Rotation 3-6 : Moyen
  - Rotation < 3 : Mauvais (produit dort)
```

**RG-P-03 : Délai Moyen Écoulement**
```
Délai écoulement (jours) = 365 / Rotation annuelle

Exemple :
  Rotation annuelle : 8
  Délai écoulement : 365 / 8 = 45.6 jours
  
  Signifie : En moyenne, un produit reste 46 jours en stock
  avant d'être vendu
```

### 8.4 Règles Classification

**RG-CL-01 : Classification ABC (Pareto)**
```
Classement produits par CA décroissant :

Classe A :
  - Produits représentant 80% CA cumulé
  - ~20% références
  - Priorité maximale (jamais de rupture)
  - Stock sécurité élevé
  - Suivi quotidien

Classe B :
  - Produits représentant 15% CA suivants (80-95% cumulé)
  - ~30% références
  - Importante mais moins critique
  - Stock sécurité moyen
  - Suivi hebdomadaire

Classe C :
  - Produits représentant 5% CA restant (95-100%)
  - ~50% références
  - Secondaire
  - Stock minimal
  - Ruptures tolérables

Application :
  - Alertes prioritaires classe A
  - Recommandations focus A et B
  - Déréférencement possible classe C faible rotation
```

**RG-CL-02 : Statut Produit**
```
Statut défini automatiquement :

RUPTURE :
  Stock actuel = 0

ALERTE :
  Stock actuel > 0
  ET Stock actuel < Point de commande
  (Point commande = RG-S-03)

NORMAL :
  Stock actuel >= Point de commande
  ET Stock actuel <= Stock maximum (si défini)

SURSTOCK :
  Stock actuel > Stock maximum (si défini)
  OU Couverture > 60 jours

Mise à jour : Automatique à chaque changement stock
```

---

## 9. DONNÉES MÉTIERS REQUISES

### 9.1 Données Maîtres (Master Data)

#### Tenant (PME Cliente)
```
Informations entreprise :
  - Identification : Nom, NINEA, Adresse
  - Contact : Email, Téléphone, Responsable
  - Configuration : Devise, Fuseau horaire, Langue
  - Paramètres métier : Objectifs CA, Taux service cible
  - Paramètres alertes : Numéros WhatsApp, Emails
  - Gestion multi-site : Activé/Désactivé (par défaut désactivé pour MVP)
```

#### Sites (Gestion Multi-Site)
```
Données requises :
  - Code site (référence interne unique, ex: "DKR-001", "THIES-01")
  - Nom site (ex: "Boutique Dakar Centre", "Dépôt Thiès")
  - Type site :
    * BOUTIQUE : Point de vente client
    * DEPOT : Stockage, pas de vente directe
    * ENTREPOT : Stockage central, distribution
    * SHOWROOM : Exposition, peu de stock
  - Adresse complète
  - Contact site : Responsable, Téléphone
  - Statut : Actif/Inactif
  - Paramètres spécifiques :
    * Site principal (siège) : Oui/Non
    * Autorise transferts sortants : Oui/Non
    * Autorise transferts entrants : Oui/Non
    * Objectif CA mensuel (optionnel)
  
Contraintes :
  - Au moins 1 site par tenant
  - 1 seul site peut être "site principal"
  - Code site unique par tenant

Usage :
  - Organisation géographique PME
  - Suivi stock par localisation
  - Analyse performance par site
  - Gestion transferts inter-sites
  - Alertes spécifiques par site

Scénarios d'usage :
  
  PME mono-site (MVP par défaut) :
    • 1 site créé automatiquement
    • Interface simplifiée (pas de filtre site)
    • Comportement identique version sans site
  
  PME multi-sites (activation optionnelle) :
    • 2 boutiques + 1 dépôt central
    • Stock consolidé ou par site
    • Transferts entre sites
    • Alertes par site ou globales
    • Dashboards comparatifs sites

Exemples réels Sénégal :
  
  Cas 1 - Grossiste alimentaire :
    • Site 1 : Dépôt Pikine (principal, stockage)
    • Site 2 : Boutique Sandaga (vente)
    • Site 3 : Boutique Thiès (vente)
  
  Cas 2 - Quincaillerie :
    • Site 1 : Magasin Rufisque (principal, vente + stock)
    • Site 2 : Annexe Bargny (vente, petit stock)
  
  Cas 3 - Pharmacie (réseau) :
    • Site 1 : Pharmacie Dakar Centre (principal)
    • Site 2 : Pharmacie Almadies
    • Site 3 : Pharmacie Guédiawaye
    • Dépôt central : Entrepôt commun
```

#### Catégories Produits
```
Données requises :
  - Nom catégorie (ex: Riz, Farine, Huile...)
  - Description (optionnel)
  - Catégorie parente (hiérarchie, optionnel)
  - Ordre affichage (tri interface)

Usage :
  - Regroupement produits dashboards
  - Filtres analyses
  - Calcul performance par catégorie
```

#### Fournisseurs
```
Données requises :
  - Code fournisseur (référence interne)
  - Nom commercial
  - Contact : Téléphone, Email, Personne contact
  - Adresse (optionnel)
  - Délai livraison moyen (jours)
  - Conditions paiement (optionnel)
  - Note performance (calculée, optionnel)

Usage :
  - Recommandations achat
  - Calcul points de commande
  - Groupement commandes par fournisseur
```

#### Produits (Référentiel Central)
```
Données OBLIGATOIRES :
  - Code produit (unique par tenant)
  - Désignation (nom commercial)
  - Catégorie
  - Prix achat unitaire
  - Prix vente unitaire
  - Unité de mesure (sac, bidon, kg, unité...)

Stock (selon mode gestion) :
  
  MODE MONO-SITE (par défaut MVP) :
    - Stock actuel global (quantité)
  
  MODE MULTI-SITES (optionnel) :
    - Stock par site (voir section Stock Multi-Site)
    - Stock global = Somme stocks tous sites
    
Données OPTIONNELLES mais RECOMMANDÉES :
  - Stock minimum (seuil alerte)
    * Mode mono-site : 1 valeur globale
    * Mode multi-sites : Configurable par site OU valeur globale par défaut
  - Stock maximum (seuil surstock)
    * Même logique que stock minimum
  - Fournisseur principal
  - Description détaillée
  - Code-barres / EAN
  - Image produit
  - Statut actif/inactif
  - Autoriser transferts inter-sites (Oui/Non) - si multi-sites

Données CALCULÉES (automatiquement) :
  - Marge unitaire (Prix vente - Prix achat)
  - Marge % ((Prix vente - Prix achat) / Prix achat × 100)
  - Valorisation stock :
    * Mono-site : Stock actuel × Prix achat
    * Multi-sites : Somme (Stock chaque site × Prix achat)
  - Statut stock :
    * Mono-site : 1 statut global
    * Multi-sites : Statut par site + statut consolidé
  - Classement ABC (calculé périodiquement sur CA consolidé)

Contraintes :
  - Code produit unique
  - Prix > 0
  - Stock >= 0 (par site si multi-sites)

Gestion multi-sites :
  - Produit existe au niveau tenant (référentiel central)
  - Stock géré par site (quantités différentes par localisation)
  - Prix identiques tous sites (variation prix non gérée MVP)
  - Possibilité activer/désactiver produit par site (assortiment différent)
```

### 9.2 Données Transactionnelles

#### Stock par Site (Multi-Site)
```
Données requises (si gestion multi-sites activée) :
  - Produit (référence)
  - Site (référence)
  - Quantité en stock
  - Stock minimum site (optionnel, sinon utilise valeur produit globale)
  - Stock maximum site (optionnel)
  - Dernière mise à jour (timestamp)
  - Statut site pour ce produit :
    * ACTIF : Produit disponible ce site
    * INACTIF : Produit non commercialisé ce site
    * TRANSFERT_UNIQUEMENT : Stock existe mais pas de vente (transit)

Données CALCULÉES :
  - Valorisation stock site (Quantité × Prix achat produit)
  - Couverture jours site (Stock / Vente moyenne quotidienne site)
  - Statut stock site (Rupture / Alerte / Normal / Surstock)

Contraintes :
  - 1 ligne unique par couple (Produit, Site)
  - Stock >= 0
  - Si produit inactif sur site, stock doit être 0

Consolidation :
  Stock global produit = Somme (Stocks tous sites)
  
Exemple :
  Produit : Farine 50kg
  
  Site Dakar Centre : 45 sacs (actif)
  Site Thiès : 30 sacs (actif)
  Site Dépôt Pikine : 120 sacs (actif)
  ─────────────────────────────────────────
  Stock global : 195 sacs

Usage :
  - Dashboards stock par site
  - Alertes spécifiques par site
  - Optimisation répartition stock
  - Identification besoins transferts
```

#### Transferts Inter-Sites
```
Données requises (si gestion multi-sites activée) :
  - Numéro transfert (référence unique, ex: "TR-2024-10-001")
  - Date transfert (création demande)
  - Site origine (départ marchandise)
  - Site destination (arrivée marchandise)
  - Statut transfert :
    * DEMANDE : Créé, pas encore validé
    * VALIDE : Approuvé, en préparation
    * EN_TRANSIT : Marchandise partie origine, pas encore reçue
    * RECEPTIONNE : Arrivée destination, stock mis à jour
    * ANNULE : Transfert annulé
  - Demandeur (utilisateur ayant créé transfert)
  - Valideur (responsable ayant approuvé - optionnel)
  - Date expédition réelle (optionnel)
  - Date réception réelle (optionnel)
  - Commentaire (raison transfert - optionnel)

Lignes transfert (détail produits) :
  - Produit transféré
  - Quantité demandée
  - Quantité expédiée (peut différer si rupture partielle)
  - Quantité reçue (peut différer si casse transport)
  - Motif transfert :
    * REEQUILIBRAGE : Optimisation stock entre sites
    * RUPTURE_SITE : Site destination en rupture
    * DEMANDE_CLIENT : Commande client nécessite transfert
    * RETOUR : Retour marchandise (produits invendables)

Règles métier :
  - Transfert ne peut partir que si stock origine suffisant
  - Stock origine décrémenté à l'expédition (statut EN_TRANSIT)
  - Stock destination incrémenté à la réception (statut RECEPTIONNE)
  - Période transit = écart entre expédition et réception
    → Stock "en transit" (ni origine ni destination temporairement)

Traçabilité :
  - Historique tous transferts par produit
  - Analyse fréquence transferts (identifier déséquilibres)
  - Coût transferts (transport) si capturé

Exemple scénario :
  Boutique Thiès en rupture Riz 25kg
  Dépôt Pikine a 500 sacs en stock
  
  1. Création transfert : Pikine → Thiès, 100 sacs Riz
  2. Validation responsable dépôt
  3. Expédition : -100 sacs stock Pikine
  4. Transport 1 jour
  5. Réception Thiès : +100 sacs stock Thiès

Usage :
  - Optimisation répartition stock réseau
  - Éviter ruptures en mutualisant stocks
  - Analyse flux logistiques
  - Coûts logistiques inter-sites
```

#### Mouvements Stock
```
Données requises :
  - Date mouvement (timestamp)
  - Site concerné (référence) - OBLIGATOIRE si multi-sites
  - Produit concerné (référence)
  - Type mouvement :
    * ENTREE : Réception fournisseur, retour client
    * SORTIE : Vente client, casse
    * AJUSTEMENT : Correction inventaire (+ ou -)
    * INVENTAIRE : Recompte physique
    * TRANSFERT_SORTIE : Départ transfert inter-site
    * TRANSFERT_ENTREE : Arrivée transfert inter-site
  - Quantité (+ pour entrée, - pour sortie)
  - Stock avant mouvement (traçabilité)
  - Stock après mouvement (traçabilité)
  - Référence document (N° facture, BL, N° transfert... - optionnel)
  - Commentaire (explication - optionnel)

Spécificités multi-sites :
  - Chaque mouvement affecte stock d'1 seul site
  - Transferts inter-sites = 2 mouvements liés :
    * TRANSFERT_SORTIE site origine (-quantité)
    * TRANSFERT_ENTREE site destination (+quantité)
  - Inventaire = AJUSTEMENT pour aligner stock système avec physique

Consolidation :
  Mono-site : Mouvements appliqués stock global
  Multi-sites : Mouvements par site, agrégation si besoin vue consolidée

Usage :
  - Calcul stock actuel temps réel par site
  - Traçabilité mouvements
  - Historique évolution stock site
  - Audit inventaire par site
  - Analyse flux (entrées/sorties par site)
```

#### Ventes
```
Données OBLIGATOIRES :
  - Date vente (timestamp)
  - Site vente (référence) - OBLIGATOIRE si multi-sites
  - Produit vendu (référence)
  - Quantité
  - Prix unitaire vente (prix pratiqué)
  - Montant total (Quantité × Prix unitaire)

Données OPTIONNELLES mais RECOMMANDÉES :
  - Numéro commande (référence unique)
  - Client (nom ou ID si gestion clients)
  - Statut commande :
    * CONFIRMEE : Commande prise
    * EN_PREPARATION : Picking en cours
    * LIVREE : Client servi
    * ANNULEE : Annulation
  - Date livraison prévue
  - Date livraison réelle
  - Mode paiement (Espèces, Mobile Money, Crédit...)
  - Canal vente (Boutique, Livraison, WhatsApp...)
  - Site livraison (si différent site vente - cas livraison)

Spécificités multi-sites :
  - Vente impacte stock du site de vente uniquement
  - Si livraison depuis autre site :
    * Option 1 : Vente enregistrée site commande, transfert automatique créé
    * Option 2 : Vente enregistrée site livraison directement
    * MVP : Option 2 (plus simple)
  - Analyse CA par site = ventes du site
  - Analyse CA consolidée = somme ventes tous sites

Données CALCULÉES :
  - Marge vente (calculée via prix achat produit)
  - Marge % vente
  - Contribution site au CA global

Usage :
  - Calcul CA par site
  - Analyse performance commerciale site
  - Calcul ventes moyennes site (prédictions)
  - Top produits par site
  - Comparaison performance sites
  - Consolidation CA groupe (tous sites)
```

### 9.3 Données Système (Alerting & Configuration)

#### Configuration Alertes
```
Données requises :
  - Nom alerte (ex: "Rupture Stock Produits A")
  - Type alerte (Rupture / Stock faible / Baisse perf / Opportunité)
  - Vue SQL source (ex: v_alert_rupture_stock)
  - Condition SQL (expression booléenne déclenchement)
  - Sévérité (Critique / Important / Info)
  - Canal envoi (WhatsApp / Email / App)
  - Destinataires (liste numéros/emails)
  - Fréquence vérification (temps réel / quotidien / hebdo)
  - Actif/Inactif

Usage :
  - Moteur alerting configurable
  - Personnalisation par tenant
  - Test alertes (simulation)
```

#### Historique Alertes
```
Données enregistrées :
  - Date/heure déclenchement
  - Alerte concernée (type + config)
  - Produit concerné (si applicable)
  - Données contextuelles (JSON) :
    * Valeurs ayant déclenché alerte
    * Métriques associées
  - Message envoyé
  - Statut envoi (Succès / Échec)
  - Canal utilisé
  - Date/heure résolution (si applicable)
  - Statut (En cours / Résolue / Ignorée)

Usage :
  - Audit alertes
  - Statistiques performance alerting
  - Analyse temps résolution
  - Éviter duplications (alerte déjà envoyée)
```

### 9.4 Qualité Données (Data Quality)

**Règles Validation Import** :

```
PRODUITS :
  ✅ Obligatoire :
    - Code non vide, unique
    - Désignation non vide
    - Prix >= 0
    - Stock >= 0
  
  ⚠️ Alertes (données acceptées mais attention) :
    - Stock minimum non défini (utiliser défaut 0)
    - Fournisseur manquant (pas de recommandations fournisseur)
    - Prix achat = 0 (pas de calcul marge)
  
  ❌ Rejet :
    - Code déjà existant (doublon)
    - Prix négatif
    - Stock négatif

VENTES :
  ✅ Obligatoire :
    - Date vente valide
    - Produit existant (référence valide)
    - Quantité > 0
    - Prix unitaire > 0
  
  ⚠️ Alertes :
    - Prix vente très différent prix catalogue (>20% écart)
      → Vérifier pas d'erreur saisie
    - Quantité inhabituelle (>3× vente moyenne)
      → Confirmer commande spéciale
  
  ❌ Rejet :
    - Produit inexistant
    - Quantité <= 0
    - Prix <= 0
    - Date future

MOUVEMENTS STOCK :
  ✅ Obligatoire :
    - Date mouvement valide
    - Produit existant
    - Type mouvement valide (ENTREE/SORTIE/AJUSTEMENT)
    - Quantité != 0
  
  ⚠️ Alertes :
    - Stock résultant négatif
      → Accepter mais alerter (possible erreur inventaire)
  
  ❌ Rejet :
    - Produit inexistant
    - Type mouvement invalide
    - Quantité = 0
```

**Nettoyage Automatique** :
```
Lors import données :
  - Trim espaces (début/fin textes)
  - Normalisation casse (Majuscules codes produits)
  - Suppression caractères spéciaux codes
  - Conversion formats dates (multiples formats acceptés)
  - Remplacement valeurs vides :
    * Stock minimum : 0 si vide
    * Stock maximum : NULL si vide
    * Prix achat : Alerte si vide (pas de marge calculable)
```

---

## 10. GESTION MULTI-SITE

### 10.1 Vision Fonctionnelle Multi-Site

**Objectif** : Permettre aux PME ayant plusieurs points de vente, dépôts ou magasins de gérer leur stock de manière centralisée tout en conservant une visibilité par site.

**Principe d'Activation** :
```
Mode par défaut : MONO-SITE
  • 1 seul site créé automatiquement (site principal)
  • Interface simplifiée sans notion de site
  • Comportement identique version sans multi-site

Activation MULTI-SITES (optionnelle) :
  • Gérant active depuis paramètres tenant
  • Création sites supplémentaires
  • Interface enrichie avec filtres sites
  • Fonctionnalités transferts inter-sites débloquées
```

**Cas d'Usage Sénégal** :
```
Grossiste alimentaire Dakar :
  ├─ Dépôt central Pikine (stockage + distribution)
  ├─ Boutique Sandaga (vente détail)
  └─ Boutique Thiès (vente détail)

Quincaillerie :
  ├─ Magasin principal Rufisque (vente + stock important)
  └─ Annexe Bargny (vente, petit stock)

Pharmacie réseau :
  ├─ Pharmacie Centre (principale)
  ├─ Pharmacie Almadies
  ├─ Pharmacie Guédiawaye
  └─ Dépôt commun (entrepôt)
```

### 10.2 Impact sur les Dashboards

#### Dashboard "Vue d'Ensemble" (Multi-Site)

**Sélecteur Site** (en haut de page) :
```
┌──────────────────────────────────────────────────────────┐
│  Site : [🏢 Tous les sites ▼]   [⚙️ Gérer sites]        │
│                                                          │
│  Options :                                               │
│    • Tous les sites (vue consolidée)                    │
│    • Dépôt Pikine                                       │
│    • Boutique Sandaga                                   │
│    • Boutique Thiès                                     │
└──────────────────────────────────────────────────────────┘
```

**Vue Consolidée (Tous les sites)** :
```
┌─────────────────────────────────────────┐
│  📦 SANTÉ STOCK GLOBALE                 │
├─────────────────────────────────────────┤
│  🔴 URGENT - 12 PRODUITS EN RUPTURE     │
│  • Pikine : 3 ruptures                  │
│  • Sandaga : 6 ruptures                 │
│  • Thiès : 3 ruptures                   │
│                                         │
│  ⚠️ ATTENTION - 23 PRODUITS < 7 JOURS   │
│  • Pikine : 8 alertes                   │
│  • Sandaga : 10 alertes                 │
│  • Thiès : 5 alertes                    │
│                                         │
│  📊 Taux de Service Global : 87%        │
│  • Meilleur : Pikine 94%                │
│  • À améliorer : Sandaga 81%            │
│                                         │
│  [Comparer sites]  [Voir détails]      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  💰 VENTES CONSOLIDÉES                  │
├─────────────────────────────────────────┤
│  Aujourd'hui :    2 150 000 FCFA        │
│  • Pikine : 0 F (dépôt, pas de vente)   │
│  • Sandaga : 1 350 000 F (63%)          │
│  • Thiès : 800 000 F (37%)              │
│                                         │
│  Mois :          45 800 000 FCFA        │
│  • Sandaga : 28M F (61%)                │
│  • Thiès : 17.8M F (39%)                │
│                                         │
│  📊 [Graphique CA par site 7 derniers j]│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  💵 VALORISATION STOCK PAR SITE         │
├─────────────────────────────────────────┤
│  Valeur totale : 28 500 000 FCFA        │
│  • Pikine : 18M F (63%) - Dépôt central │
│  • Sandaga : 7M F (25%)                 │
│  • Thiès : 3.5M F (12%)                 │
│                                         │
│  💡 Déséquilibre détecté :              │
│  Thiès sous-stocké (11 ruptures/mois)   │
│  [Voir recommandations transferts]      │
└─────────────────────────────────────────┘
```

**Vue Site Spécifique** (Sélection "Boutique Thiès") :
```
┌─────────────────────────────────────────┐
│  🏢 BOUTIQUE THIÈS                      │
├─────────────────────────────────────────┤
│  📦 SANTÉ STOCK                         │
│  🔴 URGENT - 3 PRODUITS EN RUPTURE      │
│  ⚠️ ATTENTION - 5 PRODUITS < 7 JOURS    │
│  🟢 STOCK OK - 87 PRODUITS              │
│  📊 Taux de Service : 89%               │
│                                         │
│  💰 VENTES                              │
│  Aujourd'hui :    800 000 FCFA          │
│  Semaine :      4 500 000 FCFA          │
│  Mois :        17 800 000 FCFA          │
│  Objectif mois : 20M F (89% réalisé)    │
│                                         │
│  💵 STOCK                               │
│  Valeur stock : 3 500 000 FCFA          │
│  Rotation moy : 9.2 (bon)               │
│                                         │
│  💡 RECOMMANDATIONS                     │
│  • 3 produits à transférer depuis Pikine│
│  • Commander 5 produits fournisseur     │
│                                         │
└─────────────────────────────────────────┘
```

#### Dashboard "Gestion Stock" (Multi-Site)

**Filtre Site** + **Colonne Site** dans tableau :
```
┌────────────────────────────────────────────────────────────────┐
│  Filtre : [Site: Tous ▼] [Statut: Alerte ▼] [Catégorie: ▼]   │
└────────────────────────────────────────────────────────────────┘

┌──────┬──────┬─────────────┬────────┬───────────┬──────────┬────┐
│Statut│ Site │ Produit     │Stock   │Couverture │Stock Site│Act.│
│      │      │             │        │(jours)    │Autres    │    │
├──────┼──────┼─────────────┼────────┼───────────┼──────────┼────┤
│  🔴  │Thiès │Farine 50kg  │   0    │    0      │Pikine:120│[↔️]│
│      │      │             │        │           │Sandaga:8 │    │
│  ⚠️  │Thies │Riz 25kg     │  12    │    2      │Pikine:500│[↔️]│
│      │      │             │        │           │Sandaga:45│    │
│  🟢  │Pikine│Huile 20L    │  450   │   42      │Thiès:30  │[↔️]│
│      │      │             │        │           │Sandaga:78│    │
└──────┴──────┴─────────────┴────────┴───────────┴──────────┴────┘

💡 Insights :
  • Farine disponible Pikine (120 sacs) : Transférer 50 vers Thiès
  • Huile surstock Pikine (42j) : Équilibrer vers autres sites
```

**Bouton Action [↔️] : Initier Transfert Inter-Site**
```
Clic sur [↔️] Farine 50kg ligne Thiès :

┌─────────────────────────────────────────────────────────┐
│  CRÉER TRANSFERT - Farine 50kg                         │
├─────────────────────────────────────────────────────────┤
│  Origine :    [Dépôt Pikine ▼]   (Stock: 120 sacs)    │
│  Destination : Boutique Thiès    (Stock: 0 sacs)       │
│                                                         │
│  Quantité à transférer : [50] sacs                     │
│                                                         │
│  Motif : [Rupture site destination ▼]                 │
│  Commentaire : _____________________________           │
│                                                         │
│  Impact stocks :                                       │
│  • Pikine après : 70 sacs (21j couverture)  ✅         │
│  • Thiès après : 50 sacs (8j couverture)    ✅         │
│                                                         │
│  Délai livraison estimé : 1 jour                       │
│  Coût transport : 15 000 FCFA (estimation)             │
│                                                         │
│  [✅ Créer Transfert]  [❌ Annuler]                    │
└─────────────────────────────────────────────────────────┘
```

#### Dashboard "Comparaison Sites"

**Nouveau dashboard spécifique multi-sites** :
```
┌──────────────────────────────────────────────────────────────┐
│  📊 COMPARAISON PERFORMANCE SITES                            │
├──────────────────────────────────────────────────────────────┤
│  Période : [Octobre 2024 ▼]                                 │
│                                                              │
│  ┌────────┬────────────┬─────────┬──────────┬──────────┐   │
│  │ Site   │ CA         │ Taux Srvc│ Rotation │ Ruptures │   │
│  ├────────┼────────────┼─────────┼──────────┼──────────┤   │
│  │Sandaga │ 28.0M F    │   93%   │   10.5   │    8     │   │
│  │        │ 🏆 Meilleur│  🟢 Bon │  🟢 Bon  │  ⚠️ Moy  │   │
│  │Thiès   │ 17.8M F    │   89%   │    9.8   │   11     │   │
│  │        │            │  ⚠️ Moy │  🟢 Bon  │  🔴 Élevé│   │
│  │Pikine  │    0 F     │   96%   │    8.2   │    5     │   │
│  │ (Dépôt)│    N/A     │  🟢 Excl│  🟢 Bon  │  🟢 Bas  │   │
│  └────────┴────────────┴─────────┴──────────┴──────────┘   │
│                                                              │
│  💡 Analyse comparative :                                   │
│  ✅ Points forts :                                          │
│    • Sandaga : CA élevé, bonne rotation                    │
│    • Pikine : Excellent taux service (dépôt bien géré)     │
│                                                              │
│  ⚠️ Points d'amélioration :                                │
│    • Thiès : Trop de ruptures (11/mois)                    │
│      → Augmenter stocks sécurité OU transferts fréquents   │
│    • Sandaga : 8 ruptures malgré bon taux service          │
│      → Revoir prédictions demande                          │
│                                                              │
│  [📊 Graphiques détaillés]  [📄 Rapport PDF]               │
└──────────────────────────────────────────────────────────────┘
```

### 10.3 Impact sur les Alertes

#### Configuration Alertes Multi-Site

**Granularité Alertes** :
```
Lors configuration alerte, choix niveau :

┌─────────────────────────────────────────────────────────┐
│  CONFIGURATION ALERTE : Rupture Stock                   │
├─────────────────────────────────────────────────────────┤
│  Périmètre :                                            │
│    ○ Tous les sites (alerte globale)                   │
│    ● Par site (alertes séparées)                       │
│                                                         │
│  Si "Par site" sélectionné :                           │
│    Sites concernés :                                    │
│      [✓] Boutique Sandaga                              │
│      [✓] Boutique Thiès                                │
│      [ ] Dépôt Pikine (exclure dépôt)                  │
│                                                         │
│  Destinataires :                                       │
│    • Gérant (tous sites) : +221771234567               │
│    • Resp. Sandaga : +221776543210                     │
│    • Resp. Thiès : +221779876543                       │
│                                                         │
│  Règle routage notification :                          │
│    ● Envoyer au responsable site concerné              │
│    ○ Envoyer à tous les destinataires                  │
│    ○ Envoyer uniquement au gérant                      │
│                                                         │
│  [💾 Enregistrer]                                      │
└─────────────────────────────────────────────────────────┘
```

#### Messages Alertes Multi-Site

**Alerte Rupture Site Spécifique** :
```
🔴 RUPTURE STOCK - Boutique Thiès

Produit : Farine 50kg
Stock site : 0 sacs
Ventes perdues aujourd'hui : 8 sacs (estimation)

💡 SOLUTION IMMÉDIATE :
Dépôt Pikine a 120 sacs en stock
→ Transférer 50 sacs (1 jour livraison)

OU Commander fournisseur :
→ 80 sacs Moulin Dakar (3 jours délai)

👉 Créer transfert : https://app.digiboost.sn/transfert/new?...
👉 Commander : https://app.digiboost.sn/reappro/...
```

**Alerte Consolidée Multi-Ruptures** :
```
⚠️ ALERTE STOCK MULTIPLE - 3 SITES CONCERNÉS

Ruptures détectées :

📍 Boutique Sandaga (6 produits) :
  • Farine 50kg, Riz 25kg, Huile 20L...
  
📍 Boutique Thiès (3 produits) :
  • Sucre 50kg, Lait poudre, Café...

📍 Dépôt Pikine (3 produits) :
  • Thé vert, Couscous, Pâtes...

💡 PLAN D'ACTION SUGGÉRÉ :
1. Transferts Pikine → Boutiques (9 produits)
2. Commandes fournisseurs (3 produits Pikine)

Investissement nécessaire : 4.2M FCFA
Délai résolution : 2-3 jours

👉 Voir plan détaillé : https://app.digiboost.sn/...
```

### 10.4 Règles de Gestion Multi-Site

#### RG-MS-01 : Calcul Stock Global vs Site
```
Stock global produit = Somme (Stock tous sites)

Stock site = Stock physique présent sur site

Exemple Farine 50kg :
  • Pikine : 120 sacs
  • Sandaga : 8 sacs
  • Thiès : 0 sacs
  ─────────────────────
  Global : 128 sacs

Statut :
  • Statut par site (peut différer) :
    Pikine : NORMAL (stock suffisant)
    Sandaga : ALERTE (< 7 jours)
    Thiès : RUPTURE (0)
  
  • Statut global : ALERTE
    (au moins 1 site en alerte ou rupture)
```

#### RG-MS-02 : Priorisation Transferts
```
Algorithme suggestion transferts automatiques :

1. Identifier sites en rupture ou alerte (destination)
2. Identifier sites avec surplus (origine potentielle)
3. Calculer priorité destination :
   - Rupture > Alerte
   - Site classe A (CA élevé) > Site classe B/C
   - Ventes quotidiennes élevées > Faibles
4. Calculer capacité origine :
   - Stock disponible = Stock actuel - Stock sécurité site
   - Ne pas créer rupture sur site origine
5. Optimiser routes (proximité géographique)
6. Grouper transferts même trajet

Exemple :
  Thiès : Rupture Farine (priorité haute, CA élevé)
  Pikine : Surplus Farine (120 sacs, besoin 50)
  → Transfert 50 sacs Pikine → Thiès
```

#### RG-MS-03 : Répartition Stock Optimal
```
Pour chaque produit, répartition optimale entre sites :

Stock site optimal = 
  (Vente moy quotidienne site × Couverture jours)
  + Stock sécurité site

Couverture jours :
  • Site avec vente : 15-30 jours
  • Dépôt central : 45-60 jours (alimente autres sites)

Répartition % :
  Basée sur contribution site au CA produit

Exemple Farine 50kg (Stock global 200 sacs) :
  
  Ventes mensuelles :
    • Sandaga : 250 sacs (60% ventes)
    • Thiès : 150 sacs (36% ventes)
    • Pikine : 20 sacs (4% ventes - usage interne)
  
  Répartition optimale :
    • Sandaga : 120 sacs (60%)
    • Thiès : 72 sacs (36%)
    • Pikine : 8 sacs (4%)
  
  VS Répartition actuelle :
    • Sandaga : 8 sacs (4%) ❌ SOUS-STOCK
    • Thiès : 0 sacs (0%) ❌ RUPTURE
    • Pikine : 192 sacs (96%) ❌ SURSTOCK
  
  → Déséquilibre majeur, transferts nécessaires
```

#### RG-MS-04 : Classification Sites
```
Classification sites par CA :

Site Classe A :
  • Représente ≥40% CA consolidé
  • Priorité maximale (jamais rupture)
  • Transferts prioritaires vers ces sites
  • Objectif taux service : 98%

Site Classe B :
  • Représente 25-40% CA consolidé
  • Important
  • Objectif taux service : 95%

Site Classe C :
  • Représente <25% CA consolidé
  • Secondaire
  • Accepter ruptures occasionnelles
  • Objectif taux service : 90%

Exemple réseau :
  • Sandaga : 28M F (61% CA) → Classe A
  • Thiès : 17.8M F (39% CA) → Classe B
```

#### RG-MS-05 : Gestion Stock en Transit
```
Stock en transit = 
  Stock transféré mais pas encore réceptionné

Comptabilisation :
  • N'appartient ni au site origine ni au site destination
  • Comptabilisé séparément (état intermédiaire)
  • Durée transit = Temps entre expédition et réception

Exemple :
  Transfert 50 sacs Farine Pikine → Thiès
  Expédition : 14 Oct 10h
  Réception : 15 Oct 14h (28h transit)
  
  État stocks :
    14 Oct 10h (expédition) :
      • Pikine : 120 → 70 sacs
      • Transit : 0 → 50 sacs
      • Thiès : 0 sacs
    
    15 Oct 14h (réception) :
      • Pikine : 70 sacs
      • Transit : 50 → 0 sacs
      • Thiès : 0 → 50 sacs

Impact dashboards :
  • Stock global inchangé (128 sacs avant/après)
  • Mais répartition différente
  • Alerte sur stock transit trop élevé ou trop long
    (>5% stock global ou >3 jours transit)
```

### 10.5 Fonctionnalités Spécifiques Multi-Site

#### Dashboard "Transferts Inter-Sites"

**Nouveau dashboard dédié** :
```
┌──────────────────────────────────────────────────────────────┐
│  🚚 GESTION TRANSFERTS INTER-SITES                           │
├──────────────────────────────────────────────────────────────┤
│  [+ Nouveau Transfert]  [📋 Transferts en cours: 3]         │
│                                                              │
│  Filtres : [Statut: Tous ▼] [Site: Tous ▼] [30 derniers j] │
│                                                              │
│  ┌────────┬──────────┬──────────┬────────┬─────────────┐   │
│  │ N°     │ Origine  │ Destin.  │ Produits│ Statut      │   │
│  ├────────┼──────────┼──────────┼────────┼─────────────┤   │
│  │TR-001  │ Pikine   │ Thiès    │ 3 prod │ EN_TRANSIT  │   │
│  │14/10   │          │          │ 150 pcs│ Exp: 14/10  │   │
│  │        │          │          │        │ [Récept.→]  │   │
│  ├────────┼──────────┼──────────┼────────┼─────────────┤   │
│  │TR-002  │ Pikine   │ Sandaga  │ 2 prod │ VALIDE      │   │
│  │14/10   │          │          │ 80 pcs │ Prép. en crs│   │
│  │        │          │          │        │ [Expédier→] │   │
│  ├────────┼──────────┼──────────┼────────┼─────────────┤   │
│  │TR-003  │ Sandaga  │ Thiès    │ 1 prod │ RECEPTIONNE │   │
│  │12/10   │          │          │ 20 pcs │ ✅ Terminé  │   │
│  └────────┴──────────┴──────────┴────────┴─────────────┘   │
│                                                              │
│  💡 Insights :                                              │
│    • Flux Pikine → Boutiques : 87% transferts              │
│    • Délai moyen : 1.3 jours                               │
│    • 15 transferts ce mois (vs 8 mois dernier)             │
│      → Augmentation significative = déséquilibre stocks    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Détail Transfert** (clic sur ligne) :
```
┌─────────────────────────────────────────────────────────┐
│  TRANSFERT TR-001                                       │
├─────────────────────────────────────────────────────────┤
│  📍 Pikine → Thiès                                      │
│  📅 Créé : 14 Oct 08:15 (Demandeur: Amadou Diop)       │
│                                                         │
│  Statut : 🚚 EN_TRANSIT                                │
│  ├─ Demandé : 14 Oct 08:15 ✅                          │
│  ├─ Validé : 14 Oct 08:30 ✅ (Valideur: Fatou Sall)   │
│  ├─ Expédié : 14 Oct 10:00 ✅                          │
│  └─ Réception : En attente (prévu 15 Oct 14h)         │
│                                                         │
│  Produits transférés :                                 │
│  ┌─────────────────┬────────┬──────────┬────────────┐  │
│  │ Produit         │ Qté    │ Valeur   │ Statut     │  │
│  ├─────────────────┼────────┼──────────┼────────────┤  │
│  │ Farine 50kg     │ 50 sacs│ 900K F   │ En transit │  │
│  │ Riz 25kg        │ 80 sacs│ 1.2M F   │ En transit │  │
│  │ Huile 20L       │ 20 bid │ 500K F   │ En transit │  │
│  └─────────────────┴────────┴──────────┴────────────┘  │
│  TOTAL : 150 unités - Valeur : 2.6M FCFA               │
│                                                         │
│  Motif : Rupture multiple site destination             │
│  Commentaire : Urgence boutique Thiès (weekend approche│
│                                                         │
│  [✅ Confirmer Réception]  [📄 Bon de Transfert]       │
│  [📞 Contacter Thiès]      [❌ Annuler]                │
└─────────────────────────────────────────────────────────┘
```

#### Rapport "Flux Logistiques Multi-Site"

**Nouveau rapport spécifique** :
```
┌──────────────────────────────────────────────────────────────┐
│  📊 ANALYSE FLUX LOGISTIQUES - Octobre 2024                 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. VOLUME TRANSFERTS                                       │
│     • Nombre transferts : 15                                │
│     • Total unités transférées : 1 250                      │
│     • Valeur marchandise : 18.5M FCFA                       │
│     • Évolution : +87% vs mois dernier ⚠️                   │
│                                                              │
│  2. FLUX PRINCIPAUX                                         │
│     Pikine → Thiès : 8 transferts (53%)                     │
│     Pikine → Sandaga : 5 transferts (33%)                   │
│     Sandaga → Thiès : 2 transferts (13%)                    │
│                                                              │
│  3. DÉLAIS MOYENS                                           │
│     • Pikine → Thiès : 1.5 jours                           │
│     • Pikine → Sandaga : 0.5 jours                         │
│     • Sandaga → Thiès : 1.2 jours                          │
│                                                              │
│  4. PRODUITS LES PLUS TRANSFÉRÉS                            │
│     • Farine 50kg : 5 transferts (280 sacs)                │
│     • Riz 25kg : 4 transferts (350 sacs)                   │
│     • Huile 20L : 3 transferts (120 bidons)                │
│                                                              │
│  5. COÛTS LOGISTIQUES (estimation)                          │
│     • Transport : 225 000 FCFA                             │
│     • Coût/transfert moyen : 15 000 FCFA                   │
│     • Coût/unité : 180 FCFA                                │
│                                                              │
│  6. PROBLÈMES IDENTIFIÉS                                    │
│     ⚠️ Hausse +87% transferts = déséquilibre structurel    │
│     ⚠️ Thiès : destination 67% transferts (sous-stocké)    │
│     ⚠️ Pikine : origine 87% transferts (surstock)          │
│                                                              │
│  💡 RECOMMANDATIONS                                         │
│     1. Revoir allocation stock initiale (RG-MS-03)         │
│     2. Augmenter stock sécurité Thiès (+30%)               │
│     3. Réduire stock Pikine (-20%)                         │
│     4. Impact attendu : -60% transferts, -90K F coûts      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 10.6 Migration Mono-Site → Multi-Site

**Process d'activation** :
```
Étape 1 : Gérant active multi-site (paramètres tenant)

Étape 2 : Migration automatique données
  • Site principal créé automatiquement
  • Nom : [Nom tenant] - Principal
  • Type : BOUTIQUE (par défaut)
  • Stock actuel → Stock site principal
  • Ventes historiques → Ventes site principal

Étape 3 : Création sites additionnels
  • Gérant crée nouveaux sites (wizard)
  • Stock sites additionnels initialement à 0
  • Répartition stock à faire manuellement ou via transferts

Étape 4 : Formation utilisateurs
  • Tutorial interactif multi-site
  • Vidéo explicative transferts
  • Guide bonnes pratiques

Étape 5 : Période test (15 jours)
  • Possibilité revenir mono-site si besoin
  • Support prioritaire Digiboost
```

**Rétrocompatibilité** :
```
Interface :
  • Si 1 seul site : interface simplifiée (pas de filtre site)
  • Si 2+ sites : interface enrichie (filtres, comparaisons)

Vues SQL :
  • Vues existantes continuent fonctionner
  • Nouvelles vues spécifiques multi-sites ajoutées
  • Paramètre optionnel site_id dans fonctions

Alertes :
  • Alertes existantes → Tous sites (par défaut)
  • Nouvelles alertes → Configurables par site
```

---

## 11. FEUILLE DE ROUTE FONCTIONNELLE

### 11.1 Phase POC (MVP) - 6-8 Semaines

**Périmètre POC** : MONO-SITE uniquement (multi-site Phase 2)

#### Sprint 1 : Fondations (Semaines 1-2)
```
Objectif : Infrastructure données + 1er dashboard fonctionnel

Livrables :
  ✅ Tables métiers créées et documentées
  ✅ Vues SQL dashboard "Vue d'Ensemble"
     - v_dashboard_sante_stock
     - v_dashboard_performance_ventes
     - v_dashboard_valorisation_stock
  ✅ Fonctions calcul de base
     - fn_calc_couverture_stock
     - fn_calc_rotation_stock
     - fn_calc_taux_service
  ✅ Interface dashboard "Vue d'Ensemble" opérationnelle
  ✅ Données test (1 tenant fictif, 50 produits, historique 3 mois)

Critères acceptation :
  - Gérant test voit dashboard avec données cohérentes
  - KPI principaux affichés et calculés correctement
  - Temps chargement < 3 secondes
```

#### Sprint 2 : Alerting (Semaines 3-4)
```
Objectif : Système alertes configurables fonctionnel

Livrables :
  ✅ Vues SQL alerting
     - v_alert_rupture_stock
     - v_alert_stock_faible
     - v_alert_baisse_performance
  ✅ Moteur alerting (évaluation conditions)
  ✅ Intégration WhatsApp Business API
  ✅ Interface configuration alertes
  ✅ Historique alertes
  ✅ 3 types alertes opérationnels :
     - Rupture stock
     - Stock faible
     - Baisse taux service

Critères acceptation :
  - Alerte WhatsApp reçue dans 2 min après déclenchement
  - Gérant peut activer/désactiver alertes
  - Gérant peut modifier destinataires
  - Historique alertes consultable
```

#### Sprint 3 : Analyses (Semaines 5-6)
```
Objectif : Dashboards analyse + Prédictions

Livrables :
  ✅ Dashboard "Gestion Stock Détaillée"
     - Liste produits filtrable
     - Détail produit avec recommandations
  ✅ Dashboard "Analyse Ventes"
     - Évolution CA temporelle
     - Top produits
     - Analyse catégories
  ✅ Fonctions prédictives
     - fn_predict_date_rupture
     - fn_calc_quantite_reappro
  ✅ Dashboard "Prédictions & Recommandations"
     - Liste ruptures prévues 15j
     - Recommandations achat groupées

Critères acceptation :
  - Prédictions ruptures fiables (marge erreur <10%)
  - Recommandations achat calculées correctement
  - Dashboards fluides (chargement <3s)
  - Filtres et tris fonctionnels
```

#### Sprint 4 : Rapports & Finitions (Semaines 7-8)
```
Objectif : Rapports automatisés + Préparation agent IA

Livrables :
  ✅ 3 rapports standards
     - Inventaire stock complet (Excel)
     - Synthèse mensuelle (PDF formaté)
     - Analyse ventes détaillée (Excel multi-onglets)
  ✅ Génération automatique rapports
  ✅ Envoi automatique email + WhatsApp
  ✅ Vues SQL spécifiques agent IA
     - v_ai_diagnostic_stock
     - v_ai_analyse_ventes
     - v_ai_recommandations
  ✅ Documentation vues/fonctions pour agent IA
  ✅ Tests end-to-end POC
  ✅ Documentation utilisateur (guide PME)

Critères acceptation :
  - Rapport mensuel généré automatiquement 1er du mois
  - Qualité rapports PDF (présentables banquier)
  - Rapports Excel exploitables (formules, graphiques)
  - Documentation agent IA complète
  - POC démontrable 30 min devant prospect
```

### 11.2 Phase Post-POC - Roadmap Fonctionnelle

#### Phase 2 : Intégration Expose API + Multi-Site (Mois 3-4)
```
Objectifs :
  - Connexion automatique sources PME (Excel, MySQL, etc.)
  - Synchronisation temps réel
  - Onboarding automatisé (<5 min)
  - Activation gestion multi-site (optionnelle)

Fonctionnalités :
  ✅ Interface configuration sources données
  ✅ Mapping automatique colonnes (templates Sénégal)
  ✅ Synchronisation bidirectionnelle
  ✅ Monitoring santé connexions
  ✅ Détection anomalies données
  
  NOUVEAU - Multi-Site :
  ✅ Activation multi-site (paramètres tenant)
  ✅ Création/gestion sites
  ✅ Stock par site
  ✅ Ventes par site
  ✅ Transferts inter-sites
  ✅ Dashboard comparaison sites
  ✅ Alertes configurables par site
  ✅ Rapport flux logistiques
```

#### Phase 3 : Agent IA Conversationnel (Mois 5-6)
```
Objectifs :
  - Assistant IA opérationnel
  - Interrogation données langage naturel
  - Recommandations actionnables

Fonctionnalités :
  ✅ Interface chat intégrée plateforme
  ✅ Intégration LLM (GPT-4 ou Claude)
  ✅ Connexion vues SQL via API
  ✅ Génération insights automatiques
  ✅ Suggestions actions (bons de commande, promotions)
  ✅ Mode vocal (WhatsApp Voice)
```

#### Phase 4 : Gestion Transactionnelle (Mois 7-9)
```
Objectifs :
  - PME saisit directement commandes clients
  - PME enregistre réceptions fournisseurs
  - Gestion complète supply chain

Fonctionnalités :
  ✅ Saisie commandes clients (interface simple)
  ✅ Génération bons de commande fournisseurs
  ✅ Suivi livraisons (statuts)
  ✅ Gestion retours clients
  ✅ Inventaires périodiques (comptage physique)
  ✅ Gestion multi-dépôts (si PME >1 magasin)
```

#### Phase 5 : Fonctionnalités Avancées (Mois 10-12)
```
Objectifs :
  - Outils optimisation avancés
  - Intégrations externes
  - Analytics poussés

Fonctionnalités :
  ✅ Prévisions ventes IA (machine learning)
  ✅ Optimisation prix dynamique
  ✅ Gestion promotions (planning, impact)
  ✅ Intégration comptabilité (export FEC)
  ✅ Intégration paiement mobile (Orange Money, Wave)
  ✅ Module fidélité clients
  ✅ Analytics avancés (cohortes, RFM, CLV)
```

### 11.3 Critères Succès POC

**Métriques Adoption** :
- 80% gérants consultent dashboard 1× par jour minimum
- 90% gérants reçoivent et lisent alertes WhatsApp
- 70% gérants génèrent au moins 1 rapport par mois

**Métriques Business** :
- 50% réduction ruptures de stock (vs avant plateforme)
- +15% taux de service moyen
- 30% réduction capital immobilisé (produits dormants)
- 20% amélioration marge brute (meilleure gestion)

**Métriques Satisfaction** :
- NPS (Net Promoter Score) > 50
- 70% gérants recommandent plateforme
- 80% gérants prêts payer abonnement après période test

**Métriques Techniques** :
- Uptime > 99.5%
- Temps chargement dashboards < 3s (P95)
- Taux erreur API < 1%
- Alertes envoyées < 2 min après déclenchement

**Métriques Multi-Site** (Phase 2 uniquement) :
- 40% PME multi-sites activent fonctionnalité
- 60% réduction transferts d'urgence (meilleure répartition stock)
- +10% taux service sites secondaires (vs avant multi-site)
- 80% gérants multi-sites utilisent dashboard comparaison hebdomadairement

---

**FIN DU DOCUMENT**

*Pour toute question fonctionnelle : Équipe Produit Digiboost*
### 🔧 PROMPT 1.5 : Setup Projet Frontend React

```
CONTEXTE:
Le backend avec premier dashboard est fonctionnel. Je dois maintenant créer le projet frontend React avec TypeScript, TailwindCSS, et configuration PWA pour mode offline.

OBJECTIF:
Initialiser projet React complet avec:
- Vite + React 18 + TypeScript
- TailwindCSS + Shadcn/ui
- TanStack Query (React Query)
- React Router 6
- Configuration PWA (Service Worker)
- Structure dossiers recommandée
- Client API avec axios
- Store auth (Zustand)

SPÉCIFICATIONS TECHNIQUES:

COMMANDES INITIALISATION:
```bash
# Créer projet Vite
npm create vite@latest digiboost-frontend -- --template react-ts
cd digiboost-frontend

# Installer dépendances
npm install

# UI & Styling
npm install -D tailwindcss postcss autoprefixer
npm install clsx tailwind-merge
npx tailwindcss init -p

# State & Data
npm install @tanstack/react-query
npm install zustand
npm install axios

# Routing & Forms
npm install react-router-dom
npm install react-hook-form @hookform/resolvers
npm install zod

# Charts & Icons
npm install recharts
npm install lucide-react

# PWA
npm install -D vite-plugin-pwa
npm install dexie  # IndexedDB wrapper
npm install workbox-window

# Dev tools
npm install -D @types/node
```

STRUCTURE REQUISE:
```
digiboost-frontend/
├── public/
│   ├── manifest.json
│   └── icons/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/
│   │   ├── client.ts           # Client HTTP
│   │   ├── auth.ts             # API auth
│   │   └── dashboards.ts       # API dashboards
│   ├── components/
│   │   ├── ui/                 # Composants base
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── MainLayout.tsx
│   │   └── common/
│   │       ├── LoadingSpinner.tsx
│   │       └── ErrorBoundary.tsx
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts
│   │   │   └── store/
│   │   │       └── authStore.ts
│   │   └── dashboard/
│   │       ├── components/
│   │       └── hooks/
│   ├── hooks/
│   │   ├── useNetworkStatus.ts
│   │   └── useOfflineSync.ts
│   ├── lib/
│   │   ├── utils.ts
│   │   └── constants.ts
│   ├── services/
│   │   ├── offlineService.ts
│   │   └── cacheService.ts
│   ├── stores/
│   │   └── useAppStore.ts
│   ├── types/
│   │   ├── api.types.ts
│   │   └── models.types.ts
│   ├── styles/
│   │   └── globals.css
│   └── routes/
│       └── index.tsx
├── .env
├── .env.example
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── package.json
```

FICHIER .env:
```
VITE_API_URL=http://localhost:8000
VITE_API_V1_PREFIX=/api/v1
VITE_APP_NAME=Digiboost PME
```

CONFIGURATION VITE (vite.config.ts):
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'icons/**/*'],
      manifest: {
        name: 'Digiboost PME',
        short_name: 'Digiboost',
        description: 'Intelligence Supply Chain pour PME',
        theme_color: '#4F46E5',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      },
      workbox: {
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/.*\/api\/v1\/dashboards/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'dashboard-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 300
              }
            }
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
```

CONFIGURATION TAILWIND (tailwind.config.js):
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
        },
      },
    },
  },
  plugins: [],
}
```

CLIENT API (src/api/client.ts):
```typescript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;
const API_V1 = import.meta.env.VITE_API_V1_PREFIX;

export const apiClient = axios.create({
  baseURL: `${API_URL}${API_V1}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercepteur pour refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Gérer refresh token
    }
    return Promise.reject(error);
  }
);
```

STORE AUTH (src/features/auth/store/authStore.ts):
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  full_name: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken }),
      clearAuth: () =>
        set({ user: null, accessToken: null, refreshToken: null }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

CRITÈRES D'ACCEPTATION:
✅ Projet Vite créé et démarre
✅ TailwindCSS fonctionnel
✅ Structure dossiers complète
✅ Configuration PWA (manifest.json)
✅ Client API axios configuré
✅ Store auth Zustand créé
✅ Types TypeScript pour API
✅ npm run dev démarre sur http://localhost:5173
✅ npm run build génère dist/ sans erreur

COMMANDES DE TEST:
```bash
npm run dev
npm run build
npm run preview
```
```

---

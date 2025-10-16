# PATTERNS FRONTEND - DIGIBOOST PME

## 🎨 ARCHITECTURE COMPOSANTS

### Structure Feature-Based

```
features/
├── auth/               # Authentification
│   ├── LoginPage.tsx
│   ├── useAuth.ts
│   └── authStore.ts
├── dashboard/          # Dashboard overview
│   ├── DashboardPage.tsx
│   ├── StockHealthCard.tsx
│   ├── SalesChart.tsx
│   └── TopProductsTable.tsx
├── products/           # Gestion produits
│   ├── ProductsPage.tsx
│   ├── ProductForm.tsx
│   ├── ProductTable.tsx
│   └── useProducts.ts
├── sales/              # Gestion ventes
│   ├── SalesPage.tsx
│   ├── SaleForm.tsx
│   └── useSales.ts
├── alerts/             # Gestion alertes
│   ├── AlertsPage.tsx
│   ├── AlertForm.tsx
│   └── useAlerts.ts
└── reports/            # Génération rapports
    ├── ReportsPage.tsx
    └── ReportGenerator.tsx
```

### Hiérarchie Composants

```
┌─────────────────────────────────────────┐
│            App.tsx                       │
│  (Routing, Auth Provider, Query Client) │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│          Layout.tsx                      │
│  (Sidebar, Header, Footer)               │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│       Feature Pages                      │
│  (DashboardPage, ProductsPage, etc.)     │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│     Feature Components                   │
│  (StockHealthCard, ProductTable, etc.)   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│       Shared Components                  │
│  (DataTable, StatCard, Chart, etc.)      │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│         UI Components                    │
│  (Button, Input, Card - Shadcn/ui)       │
└─────────────────────────────────────────┘
```

## 🔄 PATTERNS STATE MANAGEMENT

### 1. Server State (TanStack Query)

**Toutes les données API** → React Query

```typescript
// hooks/useProducts.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { Product, ProductCreate } from '@/types/product'

export function useProducts(params?: {
  search?: string
  category_id?: string
  stock_status?: string
}) {
  return useQuery({
    queryKey: ['products', params],
    queryFn: () => api.products.getAll(params),
    staleTime: 5 * 60 * 1000, // 5 min
    gcTime: 10 * 60 * 1000,   // 10 min
  })
}

export function useProduct(id: string) {
  return useQuery({
    queryKey: ['products', id],
    queryFn: () => api.products.getById(id),
    enabled: !!id,
  })
}

export function useCreateProduct() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (data: ProductCreate) => api.products.create(data),
    onSuccess: () => {
      // Invalider cache pour refetch
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useUpdateProduct() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Product> }) =>
      api.products.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: ['products', id] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useDeleteProduct() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: string) => api.products.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}
```

### 2. Client State (Zustand)

**Auth & UI globaux** → Zustand

```typescript
// stores/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types/user'

interface AuthStore {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: (token, user) =>
        set({ token, user, isAuthenticated: true }),
      
      logout: () =>
        set({ token: null, user: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
      }),
    }
  )
)
```

```typescript
// stores/uiStore.ts
import { create } from 'zustand'

interface UIStore {
  sidebarOpen: boolean
  theme: 'light' | 'dark'
  toggleSidebar: () => void
  setTheme: (theme: 'light' | 'dark') => void
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  theme: 'light',
  
  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  setTheme: (theme) => set({ theme }),
}))
```

## 🧩 PATTERN COMPOSANTS

### Composant de Page Type

```typescript
// features/products/ProductsPage.tsx
import { useState } from 'react'
import { useProducts, useDeleteProduct } from '@/hooks/useProducts'
import { ProductTable } from './ProductTable'
import { ProductForm } from './ProductForm'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useDebounce } from '@/hooks/useDebounce'
import { toast } from 'sonner'

export function ProductsPage() {
  const [search, setSearch] = useState('')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const debouncedSearch = useDebounce(search, 500)
  
  const { data, isLoading, error } = useProducts({
    search: debouncedSearch,
  })
  
  const deleteMutation = useDeleteProduct()
  
  const handleDelete = async (id: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce produit ?')) {
      return
    }
    
    try {
      await deleteMutation.mutateAsync(id)
      toast.success('Produit supprimé avec succès')
    } catch (err) {
      toast.error('Erreur lors de la suppression')
    }
  }
  
  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-red-500">Erreur: {error.message}</p>
      </div>
    )
  }
  
  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Produits</h1>
        <Button onClick={() => setIsFormOpen(true)}>
          Nouveau produit
        </Button>
      </div>
      
      {/* Recherche */}
      <Input
        placeholder="Rechercher un produit..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="max-w-md"
      />
      
      {/* Table */}
      <ProductTable
        products={data?.data || []}
        isLoading={isLoading}
        onDelete={handleDelete}
      />
      
      {/* Modal Form */}
      <ProductForm
        open={isFormOpen}
        onClose={() => setIsFormOpen(false)}
      />
    </div>
  )
}
```

### Composant UI Réutilisable

```typescript
// components/shared/StatCard.tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  className?: string
}

export function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  className,
}: StatCardProps) {
  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {trend && (
          <p
            className={cn(
              'text-xs mt-1',
              trend.isPositive ? 'text-green-600' : 'text-red-600'
            )}
          >
            {trend.isPositive ? '+' : ''}
            {trend.value}% vs période précédente
          </p>
        )}
      </CardContent>
    </Card>
  )
}
```

### Data Table Pattern

```typescript
// components/shared/DataTable.tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'

interface Column<T> {
  key: keyof T | string
  header: string
  cell?: (item: T) => React.ReactNode
  sortable?: boolean
}

interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  isLoading?: boolean
  emptyMessage?: string
}

export function DataTable<T extends { id: string }>({
  data,
  columns,
  isLoading,
  emptyMessage = 'Aucune donnée',
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    )
  }
  
  if (data.length === 0) {
    return (
      <div className="text-center py-10 text-muted-foreground">
        {emptyMessage}
      </div>
    )
  }
  
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((column) => (
              <TableHead key={String(column.key)}>
                {column.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item) => (
            <TableRow key={item.id}>
              {columns.map((column) => (
                <TableCell key={String(column.key)}>
                  {column.cell
                    ? column.cell(item)
                    : String(item[column.key as keyof T])}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
```

## 📝 PATTERN FORMULAIRES

### React Hook Form + Zod

```typescript
// features/products/ProductForm.tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useCreateProduct, useUpdateProduct } from '@/hooks/useProducts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { toast } from 'sonner'

const productSchema = z.object({
  code: z.string().min(1, 'Code requis'),
  name: z.string().min(1, 'Nom requis'),
  category_id: z.string().uuid(),
  supplier_id: z.string().uuid().optional(),
  purchase_price: z.number().min(0),
  sale_price: z.number().min(0),
  unit: z.string(),
  current_stock: z.number().min(0),
  stock_min: z.number().min(0),
  stock_max: z.number().optional(),
}).refine((data) => data.sale_price > data.purchase_price, {
  message: 'Le prix de vente doit être supérieur au prix d\'achat',
  path: ['sale_price'],
})

type ProductFormData = z.infer<typeof productSchema>

interface ProductFormProps {
  open: boolean
  onClose: () => void
  initialData?: ProductFormData
  productId?: string
}

export function ProductForm({
  open,
  onClose,
  initialData,
  productId,
}: ProductFormProps) {
  const createMutation = useCreateProduct()
  const updateMutation = useUpdateProduct()
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<ProductFormData>({
    resolver: zodResolver(productSchema),
    defaultValues: initialData,
  })
  
  const onSubmit = async (data: ProductFormData) => {
    try {
      if (productId) {
        await updateMutation.mutateAsync({ id: productId, data })
        toast.success('Produit mis à jour')
      } else {
        await createMutation.mutateAsync(data)
        toast.success('Produit créé')
      }
      reset()
      onClose()
    } catch (err) {
      toast.error('Une erreur est survenue')
    }
  }
  
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {productId ? 'Modifier' : 'Nouveau'} produit
          </DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <Label htmlFor="code">Code</Label>
            <Input id="code" {...register('code')} />
            {errors.code && (
              <p className="text-sm text-red-500">{errors.code.message}</p>
            )}
          </div>
          
          <div>
            <Label htmlFor="name">Nom</Label>
            <Input id="name" {...register('name')} />
            {errors.name && (
              <p className="text-sm text-red-500">{errors.name.message}</p>
            )}
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="purchase_price">Prix d'achat</Label>
              <Input
                id="purchase_price"
                type="number"
                {...register('purchase_price', { valueAsNumber: true })}
              />
              {errors.purchase_price && (
                <p className="text-sm text-red-500">
                  {errors.purchase_price.message}
                </p>
              )}
            </div>
            
            <div>
              <Label htmlFor="sale_price">Prix de vente</Label>
              <Input
                id="sale_price"
                type="number"
                {...register('sale_price', { valueAsNumber: true })}
              />
              {errors.sale_price && (
                <p className="text-sm text-red-500">
                  {errors.sale_price.message}
                </p>
              )}
            </div>
          </div>
          
          {/* ... autres champs ... */}
          
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Annuler
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Enregistrement...' : 'Enregistrer'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
```

## 🎨 STYLING CONVENTIONS

### TailwindCSS Utilities

```typescript
// Responsive design mobile-first
<div className="
  p-4 md:p-6 lg:p-8          // Padding responsive
  grid grid-cols-1           // 1 col mobile
  md:grid-cols-2             // 2 cols tablet
  lg:grid-cols-3             // 3 cols desktop
  gap-4                      // Gap fixe
">

// Status colors
<Badge className={cn(
  "font-medium",
  status === 'ok' && "bg-green-100 text-green-800",
  status === 'low' && "bg-yellow-100 text-yellow-800",
  status === 'out' && "bg-red-100 text-red-800"
)}>

// Dark mode support
<Card className="
  bg-white dark:bg-gray-800
  border-gray-200 dark:border-gray-700
">
```

### Utility Function `cn()`

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## 🔄 PWA PATTERNS

### Service Worker Strategy

```typescript
// service-worker.ts
import { precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { CacheFirst, NetworkFirst } from 'workbox-strategies'

// Precache des assets build
precacheAndRoute(self.__WB_MANIFEST)

// Strategy API: Network First (avec fallback cache)
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/v1/dashboards'),
  new NetworkFirst({
    cacheName: 'api-dashboards',
    networkTimeoutSeconds: 3,
  })
)

// Strategy Images: Cache First
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images',
  })
)
```

### Offline State Detection

```typescript
// hooks/useOnlineStatus.ts
import { useEffect, useState } from 'react'

export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])
  
  return isOnline
}
```

```typescript
// components/OfflineBanner.tsx
import { useOnlineStatus } from '@/hooks/useOnlineStatus'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { WifiOff } from 'lucide-react'

export function OfflineBanner() {
  const isOnline = useOnlineStatus()
  
  if (isOnline) return null
  
  return (
    <Alert variant="warning" className="fixed top-0 left-0 right-0 z-50">
      <WifiOff className="h-4 w-4" />
      <AlertDescription>
        Vous êtes hors ligne. Les données affichées peuvent être obsolètes.
      </AlertDescription>
    </Alert>
  )
}
```

## 🧪 TESTING PATTERNS

### Component Testing (React Testing Library)

```typescript
// features/products/ProductTable.test.tsx
import { render, screen } from '@testing-library/react'
import { ProductTable } from './ProductTable'

const mockProducts = [
  {
    id: '1',
    code: 'RIZ-001',
    name: 'Riz parfumé 50kg',
    current_stock: 120,
    stock_min: 50,
  },
]

describe('ProductTable', () => {
  it('renders product list', () => {
    render(<ProductTable products={mockProducts} isLoading={false} />)
    
    expect(screen.getByText('Riz parfumé 50kg')).toBeInTheDocument()
    expect(screen.getByText('RIZ-001')).toBeInTheDocument()
  })
  
  it('shows loading state', () => {
    render(<ProductTable products={[]} isLoading={true} />)
    
    expect(screen.getAllByRole('progressbar')).toHaveLength(5)
  })
  
  it('shows empty state', () => {
    render(<ProductTable products={[]} isLoading={false} />)
    
    expect(screen.getByText('Aucune donnée')).toBeInTheDocument()
  })
})
```

## ⚡ OPTIMISATIONS PERFORMANCE

### Code Splitting

```typescript
// App.tsx
import { lazy, Suspense } from 'react'

const DashboardPage = lazy(() => import('@/features/dashboard/DashboardPage'))
const ProductsPage = lazy(() => import('@/features/products/ProductsPage'))
const SalesPage = lazy(() => import('@/features/sales/SalesPage'))

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/sales" element={<SalesPage />} />
      </Routes>
    </Suspense>
  )
}
```

### Memoization

```typescript
// Expensive component render
const ExpensiveChart = memo(({ data }: { data: ChartData[] }) => {
  return <LineChart data={data} />
})

// Expensive computation
function DashboardPage() {
  const { data } = useDashboard()
  
  const topProducts = useMemo(
    () => data?.top_products.slice(0, 5) || [],
    [data?.top_products]
  )
  
  return <TopProductsTable products={topProducts} />
}
```

---

**Patterns garantissent** :
- ✅ Code maintenable et testable
- ✅ Performance optimale
- ✅ Expérience utilisateur fluide
- ✅ Offline-first fonctionnel
- ✅ Styling cohérent
import { APP_NAME } from './lib/constants'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-4xl font-bold text-primary-600 mb-4">
            {APP_NAME}
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Intelligence Supply Chain pour PME Senegalaises
          </p>

          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-semibold mb-4">
              Projet Frontend Initialise avec Succes! ✅
            </h2>

            <div className="space-y-3 text-left">
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Vite + React 18 + TypeScript</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>TailwindCSS configure</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>React Query (TanStack)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Zustand pour state management</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>Axios client API</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-green-500">✓</span>
                <span>PWA configuration</span>
              </div>
            </div>
          </div>

          <div className="mt-8 text-sm text-gray-500">
            <p>API Backend: {import.meta.env.VITE_API_URL}</p>
            <p>Version: 1.0.0</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

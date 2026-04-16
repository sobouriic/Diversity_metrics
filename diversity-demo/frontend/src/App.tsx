import { useState } from 'react'
import { apiClient, MetricsResponse, Solution } from './api'
import ManualForm from './components/ManualForm'
import ExperimentForm from './components/ExperimentForm'
import ResultsModal from './components/ResultsModal'
import Toast from './components/Toast'
import './App.css'

type TabType = 'manual' | 'experiment'

interface ToastState {
  message: string
  type: 'error' | 'success' | 'info'
}
export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('manual')
  const [results, setResults] = useState<MetricsResponse | null>(null)
  const [showModal, setShowModal] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [toast, setToast] = useState<ToastState | null>(null)

  const showToast = (message: string, type: 'error' | 'success' | 'info' = 'info') => {
    setToast({ message, type })
  }

  const closeToast = () => {
    setToast(null)
  }

  const handleManualSubmit = async (solutions: Solution[], mission?: string, goal?: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.analyzeSolutions(solutions, mission, goal)
      setResults(response)
      setShowModal(true)
      showToast(`Analysis complete: Diversity = ${response.diversity_score.toFixed(3)}`, 'success')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze solutions'
      setError(message)
      showToast(message, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleUploadSolutions = async (solutions: Solution[]) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.analyzeSolutions(solutions)
      setResults(response)
      setShowModal(true)
      showToast(`Analysis complete: Diversity = ${response.diversity_score.toFixed(3)}`, 'success')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to analyze uploaded file'
      setError(message)
      showToast(message, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>Metrics Analysis</h1>
          <p className="subtitle">Measure diversity of ideas</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          <div className="layout-full">
            <div className="input-panel">
              <div className="tabs">
                <button
                  className={`tab ${activeTab === 'manual' ? 'active' : ''}`}
                  onClick={() => setActiveTab('manual')}
                >
                  Manual Entry
                </button>
                <button
                  className={`tab ${activeTab === 'experiment' ? 'active' : ''}`}
                  onClick={() => setActiveTab('experiment')}
                >
                  Experiment Folder
                </button>
              </div>

              <div className="tab-content">
                {error && (
                  <div className="error-box">
                    <p>{error}</p>
                  </div>
                )}

                {loading && (
                  <div className="loading-box">
                    <div className="spinner"></div>
                    <p>Analyzing...</p>
                  </div>
                )}

                {!loading && !error && (
                  <>
                    {activeTab === 'manual' && (
                      <ManualForm onSubmit={handleManualSubmit} loading={loading} onToast={showToast} />
                    )}
                    {activeTab === 'experiment' && (
                      <ExperimentForm onUploadSolutions={handleUploadSolutions} loading={loading} onToast={showToast} />
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      <ResultsModal results={showModal ? results : null} onClose={() => setShowModal(false)} />
      
      {toast && (
        <div className="toast-container">
          <Toast message={toast.message} type={toast.type} onClose={closeToast} />
        </div>
      )}
    </div>
  )
}

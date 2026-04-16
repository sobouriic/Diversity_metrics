import { MetricsResponse } from '../api'
import { downloadJSON, downloadCSV, generateTimestamp } from '../utils/download'
import './Results.css'

interface Props {
  results: MetricsResponse
}

export default function ResultsDisplay({ results }: Props) {
  const timestamp = generateTimestamp()
  
  const handleDownloadJSON = () => {
    downloadJSON(results, `metrics-${timestamp}.json`)
  }

  const handleDownloadCSV = () => {
    if (results.solutions) {
      downloadCSV(results.solutions, `solutions-${timestamp}.csv`)
    }
  }

  const diversityPercent = Math.round(results.diversity_score * 100)

  return (
    <div className="results">
      <div className="results-header">
        <h2>Analysis Results</h2>
        <p className="results-count">{results.metadata.solutions_count} solutions analyzed</p>
      </div>

      <div className="download-buttons">
        <button onClick={handleDownloadJSON} className="btn-download btn-download-json">
          ↓ JSON
        </button>
        <button onClick={handleDownloadCSV} className="btn-download btn-download-csv">
          ↓ CSV
        </button>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Diversity Score</div>
          <div className="metric-value" style={{ color: '#2c2c2a' }}>
            {results.diversity_score.toFixed(3)}
          </div>
          <div className="metric-bar">
            <div className="metric-fill" style={{ width: `${diversityPercent}%` }}></div>
          </div>
          <div className="metric-percent">{diversityPercent}%</div>
        </div>


      </div>

      {results.validation_report && (
        <div className="validation-section">
          <div className="validation-header">
            <h3>Validation</h3>
            <span className={`status ${results.validation_report.valid ? 'valid' : 'invalid'}`}>
              {results.validation_report.valid ? '✓ Valid' : '✗ Invalid'}
            </span>
          </div>
          {/* Summary of passed validation checks */}
          <p className="validation-checks">
            {results.validation_report.checks_passed} checks passed
          </p>
          {results.validation_report.warnings && results.validation_report.warnings.length > 0 && (
            <div className="warnings">
              <p className="warnings-title">Warnings:</p>
              <ul>
                {results.validation_report.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}


    </div>
  )
}

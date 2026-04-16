import { MetricsResponse } from '../api'
import { downloadJSON, downloadCSV, generateTimestamp } from '../utils/download'
import './ResultsModal.css'

interface Props {
  results: MetricsResponse | null
  onClose: () => void
}

function getDiversityLabel(score: number): string {
  if (score < 0.2) return "Very Low"
  if (score < 0.4) return "Low"
  if (score < 0.6) return "Medium"
  if (score < 0.8) return "High"
  return "Very High"
}

function getDiversityInterpretation(score: number): string {
  if (score < 0.2) return "Ideas are very similar — consider exploring more diverse approaches."
  if (score < 0.4) return "Many solutions are variations of similar ideas."
  if (score < 0.6) return "Mixed similarities and differences — a balanced portfolio."
  if (score < 0.8) return "Quite different approaches representing diverse thinking."
  return "Highly diverse solutions spanning different domains and perspectives."
}

export default function ResultsModal({ results, onClose }: Props) {
  if (!results) return null

  const timestamp = generateTimestamp()
  const diversityLabel = getDiversityLabel(results.diversity_score)
  const interpretation = getDiversityInterpretation(results.diversity_score)

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Analysis Results</h2>
          <button className="modal-close" onClick={onClose} title="Close modal">×</button>
        </div>

        <div className="modal-body">
          <div className="metrics-cards">
            <div className="metric-card">
              <div className="metric-label">DIVERSITY SCORE</div>
              <div className="metric-value">{results.diversity_score.toFixed(2)}</div>
              <div className="metric-bar">
                <div 
                  className="metric-fill" 
                  style={{ width: `${results.diversity_score * 100}%` }}
                ></div>
              </div>
              <div className="metric-percent">{Math.round(results.diversity_score * 100)}%</div>
              <div className="diversity-label">{diversityLabel}</div>
              <div className="metric-description">
                How different your solutions are (0=identical, 1=completely different)
              </div>
            </div>
          </div>

          <div className="interpretation-section">
            <p className="interpretation-text">{interpretation}</p>
          </div>

          <div className="modal-footer">
            <button 
              className="btn btn-download"
              onClick={() => downloadJSON(results, `metrics-${timestamp}.json`)}
              title="Download results as JSON"
            >
              ↓ JSON
            </button>
            <button 
              className="btn btn-download"
              onClick={() => downloadCSV(results.solutions || [], `solutions-${timestamp}.csv`)}
              title="Download results as CSV"
            >
              ↓ CSV
            </button>
            <button 
              className="btn btn-close"
              onClick={onClose}
              title="Close modal"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

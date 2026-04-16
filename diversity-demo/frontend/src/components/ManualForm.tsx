import { useState } from 'react'
import { Solution } from '../api'
import './Form.css'

interface Props {
  onSubmit: (solutions: Solution[], mission?: string, goal?: string) => void
  loading: boolean
  onToast?: (message: string, type: 'error' | 'success' | 'info') => void
}

export default function ManualForm({ onSubmit, loading, onToast }: Props) {
  const [solutions, setSolutions] = useState<Solution[]>([{ title: '', description: '' }])
  const [mission, setMission] = useState('')
  const [goal, setGoal] = useState('')

  const handleAddSolution = () => {
    setSolutions([...solutions, { title: '', description: '' }])
  }

  const handleRemoveSolution = (index: number) => {
    setSolutions(solutions.filter((_, i) => i !== index))
  }

  const handleSolutionChange = (index: number, field: keyof Solution, value: string) => {
    const updated = [...solutions]
    updated[index] = { ...updated[index], [field]: value }
    setSolutions(updated)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const validSolutions = solutions.filter(
      s => s.title.trim().length >= 2 && s.description.trim().length >= 10
    )
    
    if (validSolutions.length < 2) {
      const message = 'Please enter at least 2 complete solutions (title + description)'
      if (onToast) {
        onToast(message, 'error')
      } else {
        alert(message)
      }
      return
    }
    
    onSubmit(validSolutions, mission || undefined, goal || undefined)
  }

  return (
    <form onSubmit={handleSubmit} className="form">
      <div className="form-section">
        <label>Mission (optional)</label>
        <input
          type="text"
          value={mission}
          onChange={(e) => setMission(e.target.value)}
          placeholder="What problem are you solving?"
          className="form-input"
        />
      </div>

      <div className="form-section">
        <label>Goal (optional)</label>
        <input
          type="text"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="What's the desired outcome?"
          className="form-input"
        />
      </div>

      <div className="form-section">
        <label className="section-label">Solutions ({solutions.length})</label>
        <div className="solutions-list">
          {solutions.map((solution, index) => (
            <div key={index} className="solution-item">
              <div className="solution-header">
                <span className="solution-number">{index + 1}</span>
              </div>
              <div className="solution-wrap">
                <input
                  type="text"
                  value={solution.title}
                  onChange={(e) => handleSolutionChange(index, 'title', e.target.value)}
                  placeholder="Title"
                  className="form-input solution-title"
                />
                <textarea
                  value={solution.description}
                  onChange={(e) => handleSolutionChange(index, 'description', e.target.value)}
                  placeholder="Description"
                  className="form-textarea solution-textarea"
                  rows={2}
                />
              </div>
              {/* Remove button only shown if more than 1 solution exists */}
              {solutions.length > 1 && (
                <button
                  type="button"
                  onClick={() => handleRemoveSolution(index)}
                  className="remove-btn"
                  title="Remove this solution"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>

        {/* Button to add new solution field */}
        <button
          type="button"
          onClick={handleAddSolution}
          className="btn btn-secondary"
        >
          + Add Solution
        </button>
      </div>

      {/* Submit button with loading state */}
      <button
        type="submit"
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? 'Analyzing...' : 'Analyze'}
      </button>
    </form>
  )
}

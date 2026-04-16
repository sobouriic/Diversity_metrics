import { useState, useRef } from 'react'
import './Form.css'
import type { Solution } from '../api'

interface Props {
  onUploadSolutions: (solutions: Solution[]) => void
  loading: boolean
  onToast?: (message: string, type: 'error' | 'success' | 'info') => void
}

export default function ExperimentForm({ onUploadSolutions, loading, onToast }: Props) {
  const [uploadedData, setUploadedData] = useState<any[]>([])
  const [solutionCount, setSolutionCount] = useState(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const formatJsonParseError = (fileName: string, error: unknown) => {
    const defaultMessage = `Failed to parse ${fileName}. Please upload a valid JSON file.`

    if (error instanceof Error && error.message) {
      return `Failed to parse ${fileName}: ${error.message}`
    }

    return defaultMessage
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    const allData: any[] = []
    const parseErrors: string[] = []
    let totalSolutions = 0
    let filesProcessed = 0

    Array.from(files).forEach((file) => {
      const reader = new FileReader()
      reader.onload = (event) => {
        try {
          const data = JSON.parse(event.target?.result as string)
          
          if (data.solutions && Array.isArray(data.solutions)) {
            allData.push({ filename: file.name, data })
            totalSolutions += data.solutions.length
            filesProcessed++
            
            if (filesProcessed === files.length) {
              setUploadedData(allData)
              setSolutionCount(totalSolutions)
              if (allData.length > 0) {
                const message = `✓ Loaded ${allData.length} file(s) with ${totalSolutions} total solutions`
                if (onToast) {
                  onToast(message, 'success')
                } else {
                  alert(message)
                }
              }

              if (parseErrors.length > 0) {
                const errorMessage = parseErrors.join(' ')
                if (onToast) {
                  onToast(errorMessage, 'error')
                } else {
                  alert(errorMessage)
                }
              }
            }
          } else {
            parseErrors.push(
              `${file.name} is valid JSON but does not contain a top-level "solutions" array.`
            )
            filesProcessed++

            if (filesProcessed === files.length) {
              setUploadedData(allData)
              setSolutionCount(totalSolutions)
              const errorMessage = parseErrors.join(' ')
              if (onToast) {
                onToast(errorMessage, 'error')
              } else {
                alert(errorMessage)
              }
            }
          }
        } catch (error) {
          console.error(`Error parsing ${file.name}:`, error)
          parseErrors.push(formatJsonParseError(file.name, error))
          filesProcessed++

          if (filesProcessed === files.length) {
            setUploadedData(allData)
            setSolutionCount(totalSolutions)

            const errorMessage = parseErrors.join(' ')
            if (onToast) {
              onToast(errorMessage, 'error')
            } else {
              alert(errorMessage)
            }
          }
        }
      }
      reader.readAsText(file)
    })
  }

  const handleUploadAnalyze = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!uploadedData || uploadedData.length === 0 || !onUploadSolutions) {
      const message = 'Please upload at least one results.json file first'
      if (onToast) {
        onToast(message, 'error')
      } else {
        alert(message)
      }
      return
    }
    
    const allSolutions: Solution[] = []
    
    uploadedData.forEach(({ data }) => {
      const solutions = data.solutions.map((s: any, idx: number) => {
        const title = s.name || s.title || `Solution ${idx + 1}`
        let desc = s.description || ''
        
        if (typeof desc === 'object') {
          desc = JSON.stringify(desc)
        }
        
        if (!desc || desc.trim().length < 10) {
          desc = `This is a solution approach designed to address identified challenges and opportunities within the domain.`
        }
        
        return {
          title: title.trim(),
          description: desc.trim()
        }
      })
      
      allSolutions.push(...solutions)
    })
    
    console.log(`Analyzing ${allSolutions.length} solutions from ${uploadedData.length} file(s)`)
    onUploadSolutions(allSolutions)
  }

  return (
    <form onSubmit={handleUploadAnalyze} className="form">
      <div className="form-section">
        <label>Upload results.json files</label>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          multiple
          onChange={handleFileUpload}
          className="form-input"
          style={{ padding: '12px', border: '2px dashed #cccccc', borderRadius: '4px', cursor: 'pointer' }}
        />
        <p className="form-hint">Select one or more results.json files from your Aideator experiment folders</p>
        
        {solutionCount > 0 && (
          <p style={{ color: '#4caf50', fontWeight: 'bold', marginTop: '10px' }}>
            ✓ Loaded {uploadedData.length} file(s) with {solutionCount} total solutions
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={loading || solutionCount === 0}
        className="btn btn-primary"
      >
        {loading ? 'Analyzing...' : 'Analyze All'}
      </button>
    </form>
  )
}

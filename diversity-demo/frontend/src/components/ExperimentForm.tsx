import { useState, useRef } from 'react'
import './Form.css'
import type { Solution } from '../api'

interface Props {
  onUploadSolutions: (solutions: Solution[]) => void
  loading: boolean
  onToast?: (message: string, type: 'error' | 'success' | 'info') => void
}

const DEFAULT_DESCRIPTION =
  'This is a solution approach designed to address identified challenges and opportunities within the domain.'
const MAX_UPLOAD_FILES = 20
const MAX_UPLOAD_FILE_BYTES = 10 * 1024 * 1024

const normalizeSolution = (raw: any, index: number): Solution => {
  const titleValue = raw?.name ?? raw?.title ?? `Solution ${index + 1}`
  const title = String(titleValue).trim() || `Solution ${index + 1}`

  let descriptionValue = raw?.description ?? ''
  if (typeof descriptionValue === 'object' && descriptionValue !== null) {
    descriptionValue = JSON.stringify(descriptionValue)
  }

  const descriptionText = String(descriptionValue ?? '').trim()
  const description =
    descriptionText.length >= 10 ? descriptionText : DEFAULT_DESCRIPTION

  return { title, description }
}

const dedupeSolutions = (solutions: Solution[]): Solution[] => {
  const seen = new Set<string>()
  const deduped: Solution[] = []

  solutions.forEach((solution) => {
    const key = `${solution.title.toLowerCase()}::${solution.description.toLowerCase()}`
    if (seen.has(key)) return
    seen.add(key)
    deduped.push(solution)
  })

  return deduped
}

const extractSolutionsFromTree = (payload: any): Solution[] => {
  const extracted: Solution[] = []

  const traverse = (node: any) => {
    if (Array.isArray(node)) {
      node.forEach(traverse)
      return
    }

    if (!node || typeof node !== 'object') {
      return
    }

    const nodeType =
      typeof node.type === 'string' ? node.type.toLowerCase().trim() : ''
    if (nodeType === 'solution') {
      extracted.push(normalizeSolution(node, extracted.length))
    }

    Object.values(node).forEach((value) => {
      if (value && typeof value === 'object') {
        traverse(value)
      }
    })
  }

  traverse(payload)
  return dedupeSolutions(extracted)
}

const extractSolutionsFromPayload = (payload: any): Solution[] => {
  if (!payload || typeof payload !== 'object') {
    return []
  }

  if (Array.isArray(payload.solutions)) {
    return dedupeSolutions(
      payload.solutions.map((solution: any, idx: number) =>
        normalizeSolution(solution, idx)
      )
    )
  }

  return extractSolutionsFromTree(payload)
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

    const selectedFiles = Array.from(files).slice(0, MAX_UPLOAD_FILES)
    if (files.length > MAX_UPLOAD_FILES) {
      onToast?.(
        `Only the first ${MAX_UPLOAD_FILES} files were processed.`,
        'info'
      )
    }

    const allData: any[] = []
    const parseErrors: string[] = []
    let totalSolutions = 0
    let filesProcessed = 0

    const finalizeIfDone = () => {
      if (filesProcessed !== selectedFiles.length) return

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

    selectedFiles.forEach((file) => {
      if (file.size > MAX_UPLOAD_FILE_BYTES) {
        parseErrors.push(
          `${file.name} exceeds 10MB and was skipped.`
        )
        filesProcessed++
        finalizeIfDone()
        return
      }

      const reader = new FileReader()
      reader.onload = (event) => {
        try {
          const data = JSON.parse(event.target?.result as string)
          const solutions = extractSolutionsFromPayload(data)

          if (solutions.length > 0) {
            allData.push({
              filename: file.name,
              data: { ...data, solutions },
            })
            totalSolutions += solutions.length
          } else {
            parseErrors.push(
              `${file.name} did not contain any solution posts (type="solution").`
            )
          }

          filesProcessed++
          finalizeIfDone()
        } catch (error) {
          console.error(`Error parsing ${file.name}:`, error)
          parseErrors.push(formatJsonParseError(file.name, error))
          filesProcessed++
          finalizeIfDone()
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
      allSolutions.push(...(data.solutions as Solution[]))
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

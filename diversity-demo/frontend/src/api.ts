import axios from 'axios'

// Support dynamic API base URL for server deployments
// Uses environment variable VITE_API_BASE if provided, otherwise defaults to localhost
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8004/api'

export interface Solution {
  title: string
  description: string
}

export interface MetricsResponse {
  diversity_score: number
  solutions: Array<{
    id: string
    title: string
    description: string
    status: string
  }>
  validation_report: {
    valid: boolean
    checks_passed: number
    warnings: string[]
    details: Record<string, any>
  }
  metadata: Record<string, any>
}

function formatApiErrorDetail(detail: unknown, fallback: string): string {
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const messages = detail
      .map((item) => {
        if (typeof item === 'string') return item
        if (item && typeof item === 'object') {
          const obj = item as Record<string, unknown>
          const path = Array.isArray(obj.loc) ? obj.loc.join(' -> ') : null
          const msg = typeof obj.msg === 'string' ? obj.msg : null
          if (path && msg) return `${path}: ${msg}`
          if (msg) return msg
        }
        return null
      })
      .filter((msg): msg is string => Boolean(msg))

    if (messages.length > 0) {
      return messages.join('; ')
    }
  }

  if (detail && typeof detail === 'object') {
    const obj = detail as Record<string, unknown>
    if (typeof obj.detail === 'string' && obj.detail.trim()) {
      return obj.detail
    }
    try {
      return JSON.stringify(detail)
    } catch {
      return fallback
    }
  }

  return fallback
}

/**
 * API client for diversity metrics backend
 */
export const apiClient = {
  analyzeSolutions: async (
    solutions: Solution[],
    mission?: string,
    goal?: string
  ): Promise<MetricsResponse> => {
    try {
      const response = await axios.post(`${API_BASE}/analyze`, {
        solutions,
        mission,
        goal
      }, {
        timeout: 300000
      })
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          formatApiErrorDetail(
            error.response.data?.detail,
            'Failed to analyze solutions'
          )
        )
      } else if (axios.isAxiosError(error) && error.code === 'ECONNABORTED') {
        throw new Error('Analysis timed out. Please try with fewer or shorter solutions.')
      } else if (axios.isAxiosError(error)) {
        throw new Error('Failed to connect to analysis server. Please ensure backend is running.')
      }
      throw error
    }
  },


  analyzeExperiment: async (
    folderPath: string,
    condition: number,
    domain: string
  ): Promise<MetricsResponse> => {
    try {
      const response = await axios.post(`${API_BASE}/analyze-experiment`, {
        folder_path: folderPath,
        condition,
        domain
      }, {
        timeout: 600000 // 10 minute timeout for experiment analysis
      })
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        throw new Error(
          formatApiErrorDetail(
            error.response.data?.detail,
            'Failed to analyze experiment'
          )
        )
      } else if (axios.isAxiosError(error) && error.code === 'ECONNABORTED') {
        throw new Error('Analysis timed out. Experiment folder may be too large.')
      } else if (axios.isAxiosError(error)) {
        throw new Error('Failed to connect to analysis server. Please ensure backend is running.')
      }
      throw error
    }
  }
}

import axios from 'axios'

const API_BASE = 'http://localhost:8004/api'

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
        throw new Error(error.response.data.detail || 'Failed to analyze solutions')
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
        throw new Error(error.response.data.detail || 'Failed to analyze experiment')
      } else if (axios.isAxiosError(error) && error.code === 'ECONNABORTED') {
        throw new Error('Analysis timed out. Experiment folder may be too large.')
      } else if (axios.isAxiosError(error)) {
        throw new Error('Failed to connect to analysis server. Please ensure backend is running.')
      }
      throw error
    }
  }
}

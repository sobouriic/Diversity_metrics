export const downloadJSON = (data: unknown, filename: string) => {
  const json = JSON.stringify(data, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export const downloadCSV = (data: unknown[], filename: string) => {
  if (!Array.isArray(data) || data.length === 0) {
    alert('No data to export')
    return
  }

  const keys = new Set<string>()
  data.forEach(item => {
    if (typeof item === 'object' && item !== null) {
      Object.keys(item).forEach(key => keys.add(key))
    }
  })

  const headers = Array.from(keys)
  const rows = data.map(item => 
    headers.map(header => {
      const value = (item as Record<string, unknown>)[header]
      if (value === null || value === undefined) return ''
      if (typeof value === 'object') return JSON.stringify(value)
      return String(value)
    })
  )

  const csv = [
    headers.join(','),
    ...rows.map(row => 
      row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(',')
    )
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export const generateTimestamp = () => {
  return new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
}

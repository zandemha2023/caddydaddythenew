const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function startDesignSession(prompt: string, projectId?: string) {
  const response = await fetch(`${API_URL}/api/v1/design/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, project_id: projectId }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to start session' }))
    throw new Error(error.detail || 'Failed to start session')
  }

  return response.json()
}

export async function sendMessage(sessionId: string, message: string) {
  const response = await fetch(`${API_URL}/api/v1/design/process`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to send message' }))
    throw new Error(error.detail || 'Failed to send message')
  }

  return response.json()
}

export async function getDesignStatus(sessionId: string) {
  const response = await fetch(`${API_URL}/api/v1/design/${sessionId}/status`)

  if (!response.ok) {
    throw new Error('Failed to get design status')
  }

  return response.json()
}

export async function downloadFile(sessionId: string) {
  const response = await fetch(`${API_URL}/api/v1/design/${sessionId}/download`)

  if (!response.ok) {
    throw new Error('Failed to download file')
  }

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `design-${sessionId}.stl`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  window.URL.revokeObjectURL(url)
}

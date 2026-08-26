import type { Exchange } from './types'

// Empty in dev (Vite's proxy handles relative /chat, /history same-origin).
// Set at Docker build time (frontend/Dockerfile, VITE_API_BASE_URL) so the
// static production build calls the backend's own origin directly — there's
// no dev-proxy equivalent for `serve -s dist`, see CLAUDE.md's Task 6 gap.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export async function sendChatMessage(prompt: string): Promise<Exchange> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  })

  if (!res.ok) {
    throw new Error(`Chat request failed: ${res.status} ${res.statusText}`)
  }

  return res.json()
}

export async function getHistory(): Promise<Exchange[]> {
  const res = await fetch(`${API_BASE}/history`)

  if (!res.ok) {
    throw new Error(`Failed to load history: ${res.status} ${res.statusText}`)
  }

  return res.json()
}

export async function deleteExchange(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/history/${id}`, { method: 'DELETE' })

  if (!res.ok) {
    throw new Error(`Failed to delete message: ${res.status} ${res.statusText}`)
  }
}

export async function clearHistory(): Promise<void> {
  const res = await fetch(`${API_BASE}/history`, { method: 'DELETE' })

  if (!res.ok) {
    throw new Error(`Failed to clear history: ${res.status} ${res.statusText}`)
  }
}

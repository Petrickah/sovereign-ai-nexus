import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

type FetchCall = { url: string; method: string }

function mockFetch(handlers: {
  history?: unknown[]
  onChat?: (prompt: string) => unknown
  onDeleteOne?: () => void
  onDeleteAll?: () => void
}) {
  const calls: FetchCall[] = []

  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    const method = init?.method ?? 'GET'
    calls.push({ url, method })

    if (url.endsWith('/history') && method === 'GET') {
      return jsonResponse(handlers.history ?? [])
    }
    if (url.endsWith('/chat') && method === 'POST') {
      const { prompt } = JSON.parse(String(init?.body))
      // A real delay, not an instantly-resolved promise — otherwise the
      // pending/"Thinking…" state can collapse into the same microtask
      // flush as the response and never actually appear for the test to
      // observe, which isn't representative of a real network round-trip.
      await new Promise((resolve) => setTimeout(resolve, 10))
      return jsonResponse(handlers.onChat?.(prompt))
    }
    if (url.endsWith('/history') && method === 'DELETE') {
      handlers.onDeleteAll?.()
      return jsonResponse({ deleted: 1 })
    }
    if (/\/history\/\d+$/.test(url) && method === 'DELETE') {
      handlers.onDeleteOne?.()
      return jsonResponse({ id: 1 })
    }

    throw new Error(`Unhandled fetch: ${method} ${url}`)
  })

  vi.stubGlobal('fetch', fetchMock)
  return calls
}

function jsonResponse(body: unknown) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  })
}

beforeEach(() => {
  vi.restoreAllMocks()
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('sending a message', () => {
  it('shows a pending state then renders the assistant response', async () => {
    const user = userEvent.setup()
    mockFetch({
      history: [],
      onChat: (prompt) => ({
        id: 1,
        prompt,
        response: 'Hello there',
        created_at: '2026-08-26T10:00:00Z',
      }),
    })

    render(<App />)
    await waitFor(() => expect(screen.queryByText(/thinking/i)).not.toBeInTheDocument())

    await user.type(screen.getByPlaceholderText(/type a message/i), 'hi')
    await user.click(screen.getByRole('button', { name: /send/i }))

    expect(await screen.findByText('Thinking…')).toBeInTheDocument()
    expect(await screen.findByText('Hello there')).toBeInTheDocument()
    expect(screen.queryByText('Thinking…')).not.toBeInTheDocument()
  })
})

describe('deleting a single exchange', () => {
  it('removes just that exchange and calls DELETE /history/:id', async () => {
    const user = userEvent.setup()
    const onDeleteOne = vi.fn()
    const calls = mockFetch({
      history: [
        { id: 1, prompt: 'first', response: 'first response', created_at: '2026-08-26T10:00:00Z' },
      ],
      onDeleteOne,
    })

    render(<App />)
    await screen.findByText('first response')

    await user.click(screen.getByRole('button', { name: /delete this exchange/i }))

    await waitFor(() => expect(onDeleteOne).toHaveBeenCalledTimes(1))
    expect(screen.queryByText('first response')).not.toBeInTheDocument()
    expect(calls.some((c) => c.method === 'DELETE' && c.url.endsWith('/history/1'))).toBe(true)
  })
})

describe('clearing all history', () => {
  it('does nothing on cancel, clears everything on confirm', async () => {
    const user = userEvent.setup()
    const onDeleteAll = vi.fn()
    mockFetch({
      history: [
        { id: 1, prompt: 'first', response: 'first response', created_at: '2026-08-26T10:00:00Z' },
      ],
      onDeleteAll,
    })

    render(<App />)
    await screen.findByText('first response')

    await user.click(screen.getByRole('button', { name: /clear all/i }))
    const confirmBar = await screen.findByText(/delete entire conversation/i)

    await user.click(within(confirmBar.closest('span')!).getByRole('button', { name: /cancel/i }))
    expect(screen.queryByText(/delete entire conversation/i)).not.toBeInTheDocument()
    expect(screen.getByText('first response')).toBeInTheDocument()
    expect(onDeleteAll).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: /clear all/i }))
    await user.click(screen.getByRole('button', { name: /yes, delete/i }))

    await waitFor(() => expect(onDeleteAll).toHaveBeenCalledTimes(1))
    expect(screen.queryByText('first response')).not.toBeInTheDocument()
  })
})

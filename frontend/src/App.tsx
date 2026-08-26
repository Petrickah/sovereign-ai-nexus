import { useEffect, useState } from 'react'
import ChatHistory from './components/ChatHistory'
import ChatInput from './components/ChatInput'
import { sendChatMessage, getHistory, deleteExchange, clearHistory } from './api'
import type { Exchange, ExchangeItem } from './types'
import './App.css'

function App() {
  const [exchanges, setExchanges] = useState<Exchange[]>([])
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [confirmingClear, setConfirmingClear] = useState(false)

  useEffect(() => {
    getHistory()
      .then(setExchanges)
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load history.'))
  }, [])

  const handleSend = async (prompt: string) => {
    setError(null)
    setPendingPrompt(prompt)

    try {
      const exchange = await sendChatMessage(prompt)
      setExchanges((prev) => [...prev, exchange])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setPendingPrompt(null)
    }
  }

  const handleDelete = async (id: number) => {
    const previous = exchanges
    setExchanges((prev) => prev.filter((exchange) => exchange.id !== id))

    try {
      await deleteExchange(id)
    } catch (err) {
      setExchanges(previous)
      setError(err instanceof Error ? err.message : 'Failed to delete message.')
    }
  }

  const handleClearAll = async () => {
    const previous = exchanges
    setConfirmingClear(false)
    setExchanges([])

    try {
      await clearHistory()
    } catch (err) {
      setExchanges(previous)
      setError(err instanceof Error ? err.message : 'Failed to clear history.')
    }
  }

  const items: ExchangeItem[] =
    pendingPrompt !== null
      ? [...exchanges, { id: null, prompt: pendingPrompt, response: null, created_at: new Date().toISOString() }]
      : exchanges

  return (
    <div className="chat-app">
      {exchanges.length > 0 && (
        <div className="chat-toolbar">
          {confirmingClear ? (
            <span className="chat-confirm-clear">
              Delete entire conversation?
              <button className="chat-confirm-yes" onClick={handleClearAll}>
                Yes, delete
              </button>
              <button className="chat-confirm-no" onClick={() => setConfirmingClear(false)}>
                Cancel
              </button>
            </span>
          ) : (
            <button className="chat-clear-all" onClick={() => setConfirmingClear(true)}>
              Clear all
            </button>
          )}
        </div>
      )}
      <ChatHistory items={items} onDelete={handleDelete} />
      {error && <p className="chat-error">{error}</p>}
      <ChatInput pending={pendingPrompt !== null} onSubmit={handleSend} />
    </div>
  )
}

export default App

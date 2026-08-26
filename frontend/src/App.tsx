import { useState } from 'react'
import ChatHistory from './components/ChatHistory'
import ChatInput from './components/ChatInput'
import { sendChatMessage } from './api'
import type { ChatMessage } from './types'
import './App.css'

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSend = async (prompt: string) => {
    setMessages((prev) => [...prev, { role: 'user', content: prompt }])
    setError(null)
    setPending(true)

    try {
      const res = await sendChatMessage(prompt)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.response }])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.')
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="chat-app">
      <ChatHistory messages={messages} pending={pending} />
      {error && <p className="chat-error">{error}</p>}
      <ChatInput pending={pending} onSubmit={handleSend} />
    </div>
  )
}

export default App

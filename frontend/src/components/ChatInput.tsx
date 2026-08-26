import { useState } from 'react'
import type { KeyboardEvent } from 'react'

interface ChatInputProps {
  pending: boolean
  onSubmit: (prompt: string) => void
}

function ChatInput({ pending, onSubmit }: ChatInputProps) {
  const [value, setValue] = useState('')

  const submit = () => {
    const prompt = value.trim()
    if (!prompt || pending) return
    onSubmit(prompt)
    setValue('')
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="chat-input-bar">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={pending}
        placeholder="Type a message…"
        rows={2}
      />
      <button onClick={submit} disabled={pending || !value.trim()}>
        Send
      </button>
    </div>
  )
}

export default ChatInput

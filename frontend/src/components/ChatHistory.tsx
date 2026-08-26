import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ChatMessage } from '../types'

interface ChatHistoryProps {
  messages: ChatMessage[]
  pending: boolean
}

function ChatHistory({ messages, pending }: ChatHistoryProps) {
  return (
    <div className="chat-history">
      {messages.map((message, i) => (
        <div key={i} className={`chat-message chat-message-${message.role}`}>
          {message.role === 'assistant' ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          ) : (
            <p>{message.content}</p>
          )}
        </div>
      ))}
      {pending && (
        <div className="chat-message chat-message-assistant chat-message-pending">
          <p>Thinking…</p>
        </div>
      )}
    </div>
  )
}

export default ChatHistory

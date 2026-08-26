import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ExchangeItem } from '../types'

interface ChatHistoryProps {
  items: ExchangeItem[]
  onDelete: (id: number) => void
}

function ChatHistory({ items, onDelete }: ChatHistoryProps) {
  return (
    <div className="chat-history">
      {items.map((item) => (
        <div key={item.id ?? 'pending'} className="chat-exchange">
          <div className="chat-message chat-message-user">
            <p>{item.prompt}</p>
          </div>
          {item.response !== null ? (
            <>
              <div className="chat-message chat-message-assistant">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{item.response}</ReactMarkdown>
              </div>
              <button
                className="chat-exchange-delete"
                onClick={() => onDelete(item.id)}
                aria-label="Delete this exchange"
              >
                Delete
              </button>
            </>
          ) : (
            <div className="chat-message chat-message-assistant chat-message-pending">
              <p>Thinking…</p>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default ChatHistory

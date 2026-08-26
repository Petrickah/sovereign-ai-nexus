export interface Exchange {
  id: number
  prompt: string
  response: string
  created_at: string
}

export interface PendingExchange {
  id: null
  prompt: string
  response: null
  created_at: string
}

export type ExchangeItem = Exchange | PendingExchange

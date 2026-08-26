import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ChatInput from './ChatInput'

describe('ChatInput', () => {
  it('submits on Enter and clears the field', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<ChatInput pending={false} onSubmit={onSubmit} />)

    const textarea = screen.getByPlaceholderText(/type a message/i)
    await user.type(textarea, 'hello{Enter}')

    expect(onSubmit).toHaveBeenCalledWith('hello')
    expect(textarea).toHaveValue('')
  })

  it('inserts a newline on Shift+Enter instead of submitting', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<ChatInput pending={false} onSubmit={onSubmit} />)

    const textarea = screen.getByPlaceholderText(/type a message/i)
    await user.type(textarea, 'line one{Shift>}{Enter}{/Shift}line two')

    expect(onSubmit).not.toHaveBeenCalled()
    expect(textarea).toHaveValue('line one\nline two')
  })

  it('disables the textarea and send button while pending', () => {
    render(<ChatInput pending={true} onSubmit={vi.fn()} />)

    expect(screen.getByPlaceholderText(/type a message/i)).toBeDisabled()
    expect(screen.getByRole('button', { name: /send/i })).toBeDisabled()
  })

  it('does not submit an empty or whitespace-only prompt', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    render(<ChatInput pending={false} onSubmit={onSubmit} />)

    await user.type(screen.getByPlaceholderText(/type a message/i), '   {Enter}')

    expect(onSubmit).not.toHaveBeenCalled()
  })
})

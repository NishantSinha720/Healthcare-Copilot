import { useState } from 'react'
import type { FormEvent } from 'react'
import { Bot, Send, User, AlertCircle, Loader2 } from 'lucide-react'

import apiClient from '../api/client'

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
  tool?: string
  confirmationRequired?: boolean
}

type AgentResponse = {
  question?: string
  answer?: string
  tool?: string
  data?: unknown
  confirmation_required?: boolean
}

function extractAnswer(data: AgentResponse): string {
  if (typeof data.answer === 'string' && data.answer.trim()) {
    return data.answer
  }

  return 'The AI agent returned a response without an answer.'
}

export default function AICopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        'Hello. I am your Healthcare Copilot. Ask me about your appointments, medical records, prescriptions, or uploaded medical documents.',
    },
  ])

  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const trimmedQuestion = question.trim()

    if (!trimmedQuestion || loading) {
      return
    }

    setError('')

    setMessages((current) => [
      ...current,
      {
        role: 'user',
        content: trimmedQuestion,
      },
    ])

    setQuestion('')
    setLoading(true)

    try {
      const response = await apiClient.post<AgentResponse>('/ai/agent/', {
        question: trimmedQuestion,
      })

      const result = response.data

      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: extractAnswer(result),
          tool: result.tool,
          confirmationRequired: result.confirmation_required === true,
        },
      ])
    } catch (requestError: unknown) {
      let message = 'Unable to contact the Healthcare Copilot.'

      if (
        typeof requestError === 'object' &&
        requestError !== null &&
        'response' in requestError
      ) {
        const response = (
          requestError as {
            response?: {
              data?: {
                detail?: string
                error?: string
              }
            }
          }
        ).response

        message =
          response?.data?.detail ??
          response?.data?.error ??
          'The AI agent rejected the request.'
      }

      setError(message)

      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: 'I could not process that request.',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <h1>AI Copilot</h1>
          <p>
            Ask questions about your authorized healthcare information.
          </p>
        </div>
      </div>

      <div className="ai-panel">
        <div className="ai-header">
          <div className="ai-avatar">
            <Bot size={24} />
          </div>

          <div>
            <h2>Healthcare Copilot</h2>
            <p>Powered by your authorized healthcare data</p>
          </div>
        </div>

        {error && (
          <div className="error-state" role="alert">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <div className="ai-messages">
          {messages.map((message, index) => (
            <div
              className={`ai-message ${
                message.role === 'user'
                  ? 'ai-message-user'
                  : 'ai-message-assistant'
              }`}
              key={`${message.role}-${index}`}
            >
              <div className="ai-message-icon">
                {message.role === 'user' ? (
                  <User size={18} />
                ) : (
                  <Bot size={18} />
                )}
              </div>

              <div className="ai-message-content">
                <p>{message.content}</p>

                {message.tool && (
                  <small>
                    Tool used: <strong>{message.tool}</strong>
                  </small>
                )}

                {message.confirmationRequired && (
                  <div className="ai-confirmation">
                    Explicit confirmation is required before this sensitive
                    action can be completed.
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="ai-message ai-message-assistant">
              <div className="ai-message-icon">
                <Bot size={18} />
              </div>

              <div className="ai-message-content">
                <p className="ai-loading">
                  <Loader2 size={16} className="spin" />
                  Processing your question...
                </p>
              </div>
            </div>
          )}
        </div>

        <form className="ai-input-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask about your medications, appointments, records..."
            disabled={loading}
            aria-label="Ask Healthcare Copilot"
          />

          <button
            type="submit"
            className="primary-button"
            disabled={loading || !question.trim()}
          >
            {loading ? (
              <Loader2 size={18} className="spin" />
            ) : (
              <Send size={18} />
            )}
            Send
          </button>
        </form>

        <div className="ai-disclaimer">
          <strong>Important:</strong> Healthcare Copilot only uses authorized
          healthcare information and does not replace professional medical
          advice.
        </div>
      </div>
    </section>
  )
}


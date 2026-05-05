import { useState, useEffect } from 'react'
import MergePanel from './MergePanel'

interface ChatPaneProps {
  documentId: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export default function ChatPane({ documentId }: ChatPaneProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [selectedModel, setSelectedModel] = useState('gemini-3.1-flash-lite-preview')
  const [loading, setLoading] = useState(false)
  const [conversation, setConversation] = useState<any>(null)

  useEffect(() => {
    createConversation()
  }, [documentId])

  const createConversation = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/conversations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'Study Session',
          document_id: documentId,
        }),
      })
      const data = await response.json()
      setConversation(data)
      setMessages([])
    } catch (error) {
      console.error('Error creating conversation:', error)
    }
  }

  const handleSendMessage = async () => {
    if (!input.trim() || !conversation || loading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      created_at: new Date().toISOString(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/conversations/${conversation.id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: input,
          model: selectedModel,
        }),
      })
      const result = await response.json()

      if (result.assistant_message) {
        const assistantMessage: Message = {
          id: result.assistant_message.id,
          role: 'assistant',
          content: result.assistant_message.content,
          created_at: new Date().toISOString(),
        }
        setMessages(prev => [...prev, assistantMessage])
      }
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="px-4 py-4 border-b border-gray-200 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Chat Assistant</h3>
        <select
          value={selectedModel}
          onChange={e => setSelectedModel(e.target.value)}
          className="w-full px-3 py-1 text-xs border border-gray-300 rounded bg-white text-gray-900 hover:border-gray-400 transition-colors"
        >
          <optgroup label="Google Gemini">
            <option>gemini-3.1-flash-lite-preview</option>
            <option>gemini-3.1-pro-preview</option>
            <option>gemini-2.5-flash-image</option>
            <option>gemini-pro-latest</option>
          </optgroup>
          <optgroup label="OpenAI">
            <option>gpt-3.5-turbo</option>
            <option>gpt-4</option>
          </optgroup>
          <optgroup label="Local">
            <option>ollama</option>
          </optgroup>
        </select>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center">
            <div className="text-gray-500">
              <p className="text-sm font-medium mb-1">No messages yet</p>
              <p className="text-xs text-gray-400">Ask a question to get started</p>
            </div>
          </div>
        ) : (
          messages.map(msg => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-xs px-4 py-2 rounded-lg text-sm ${
                  msg.role === 'user'
                    ? 'bg-gray-900 text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-900 rounded-bl-none'
                }`}
              >
                <div className="whitespace-pre-wrap break-words leading-relaxed">
                  {msg.content}
                </div>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg rounded-bl-none">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="px-4 py-4 border-t border-gray-200 bg-gray-50">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && !loading && handleSendMessage()}
            placeholder="Ask something..."
            className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            disabled={loading}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !input.trim()}
            className="px-4 py-2 text-sm bg-gray-900 text-white rounded hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

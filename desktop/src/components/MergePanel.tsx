import { useState } from 'react'

interface MergePanelProps {
  conversationId: string
  onMergeComplete: () => void
}

interface MergeSuggestion {
  parent_id: string
  fork_id: string
  new_messages: Array<{ id: string; role: string; content: string }>
  suggestion: string
}

export default function MergePanel({ conversationId, onMergeComplete }: MergePanelProps) {
  const [suggestion, setSuggestion] = useState<MergeSuggestion | null>(null)
  const [loading, setLoading] = useState(false)

  const handleViewMerge = async () => {
    setLoading(true)
    try {
      const data = await window.api.request('POST', `/api/conversations/${conversationId}/merge`)
      setSuggestion(data)
    } catch (error) {
      console.error('Error fetching merge suggestions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleConfirmMerge = async () => {
    try {
      await window.api.request('POST', `/api/conversations/${conversationId}/merge-confirm`)
      setSuggestion(null)
      onMergeComplete()
    } catch (error) {
      console.error('Error confirming merge:', error)
    }
  }

  if (!suggestion) {
    return (
      <button
        onClick={handleViewMerge}
        disabled={loading}
        className="w-full px-3 py-2 text-sm bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded transition-colors"
      >
        {loading ? 'Loading...' : 'View Merge Options'}
      </button>
    )
  }

  return (
    <div className="p-3 bg-green-900 bg-opacity-30 rounded">
      <div className="mb-3">
        <p className="text-sm font-semibold mb-2">Merge Suggestion</p>
        <p className="text-xs text-gray-300 mb-2">{suggestion.suggestion}</p>
      </div>

      {suggestion.new_messages.length > 0 && (
        <div className="mb-3 bg-gray-800 p-2 rounded text-xs max-h-40 overflow-y-auto">
          {suggestion.new_messages.map(msg => (
            <div key={msg.id} className="mb-1">
              <span className="text-gray-400">{msg.role}:</span>
              <p className="text-gray-300">{msg.content}</p>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={handleConfirmMerge}
          className="flex-1 px-2 py-1 text-xs bg-green-600 hover:bg-green-700 rounded transition-colors"
        >
          Merge
        </button>
        <button
          onClick={() => setSuggestion(null)}
          className="flex-1 px-2 py-1 text-xs bg-gray-600 hover:bg-gray-700 rounded transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}

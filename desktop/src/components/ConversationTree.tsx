import { useEffect, useState } from 'react'

interface ConvNode {
  id: string
  name: string
  is_fork: boolean
  message_count: number
  children: ConvNode[]
}

interface ConversationTreeProps {
  conversationId: string
  onSelectConversation: (id: string) => void
  selectedId: string
}

export default function ConversationTree({
  conversationId,
  onSelectConversation,
  selectedId,
}: ConversationTreeProps) {
  const [tree, setTree] = useState<ConvNode | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTree()
  }, [conversationId])

  const fetchTree = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/conversations/${conversationId}/tree`)
      const data = await response.json()
      setTree(data)
    } catch (error) {
      console.error('Error fetching conversation tree:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderNode = (node: ConvNode, depth: number = 0) => (
    <div key={node.id} style={{ marginLeft: `${depth * 20}px` }}>
      <button
        onClick={() => onSelectConversation(node.id)}
        className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
          selectedId === node.id
            ? 'bg-blue-600 text-white'
            : 'text-gray-300 hover:bg-gray-700'
        }`}
      >
        <span>{node.is_fork ? '↳ ' : ''}{node.name}</span>
        <span className="text-xs text-gray-400 ml-2">({node.message_count})</span>
      </button>
      {node.children.map(child => renderNode(child, depth + 1))}
    </div>
  )

  if (loading) return <div className="text-sm text-gray-500">Loading tree...</div>
  if (!tree) return <div className="text-sm text-gray-500">No conversation</div>

  return <div className="space-y-1">{renderNode(tree)}</div>
}

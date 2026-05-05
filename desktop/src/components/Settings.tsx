import { useState, useEffect } from 'react'

interface SettingsProps {
  onClose: () => void
  theme: string
  onThemeChange: (theme: string) => void
}

interface Rule {
  id: string
  name: string
  content: string
  active: boolean
}

export default function Settings({ onClose, theme, onThemeChange }: SettingsProps) {
  const [rules, setRules] = useState<Rule[]>([])
  const [showNewRule, setShowNewRule] = useState(false)
  const [newRuleName, setNewRuleName] = useState('')
  const [newRuleContent, setNewRuleContent] = useState('')

  useEffect(() => {
    fetchRules()
  }, [])

  const fetchRules = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/rules/')
      const data = await response.json()
      setRules(data)
    } catch (error) {
      console.error('Error fetching rules:', error)
    }
  }

  const handleAddRule = async () => {
    if (!newRuleName.trim() || !newRuleContent.trim()) return

    try {
      await fetch('http://127.0.0.1:8000/api/rules/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newRuleName,
          content: newRuleContent,
          active: true,
        }),
      })
      setNewRuleName('')
      setNewRuleContent('')
      setShowNewRule(false)
      fetchRules()
    } catch (error) {
      console.error('Error creating rule:', error)
    }
  }

  const handleDeleteRule = async (id: string) => {
    try {
      await fetch(`http://127.0.0.1:8000/api/rules/${id}`, {
        method: 'DELETE',
      })
      fetchRules()
    } catch (error) {
      console.error('Error deleting rule:', error)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-96 max-h-96 overflow-y-auto shadow-xl">
        <div className="p-6 border-b border-gray-200 flex items-center justify-between bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-900">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            ✕
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Theme */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Theme</label>
            <select
              value={theme}
              onChange={e => onThemeChange(e.target.value)}
              className="w-full px-3 py-2 bg-white border border-gray-300 rounded text-sm text-gray-900 hover:border-gray-400"
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="nord">Nord</option>
              <option value="dracula">Dracula</option>
            </select>
          </div>

          {/* Rules */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <label className="block text-sm font-semibold text-gray-900">Custom Rules</label>
              <button
                onClick={() => setShowNewRule(true)}
                className="text-xs px-2 py-1 bg-gray-900 text-white hover:bg-gray-800 rounded"
              >
                + Add
              </button>
            </div>

            {showNewRule && (
              <div className="bg-gray-50 p-3 rounded mb-3 border border-gray-200">
                <input
                  type="text"
                  value={newRuleName}
                  onChange={e => setNewRuleName(e.target.value)}
                  placeholder="Rule name"
                  className="w-full px-2 py-1 bg-white border border-gray-300 rounded text-sm text-gray-900 mb-2"
                />
                <textarea
                  value={newRuleContent}
                  onChange={e => setNewRuleContent(e.target.value)}
                  placeholder="Rule content"
                  className="w-full px-2 py-1 bg-white border border-gray-300 rounded text-sm text-gray-900 h-20 mb-2"
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleAddRule}
                    className="flex-1 px-2 py-1 text-xs bg-gray-900 text-white hover:bg-gray-800 rounded"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setShowNewRule(false)}
                    className="flex-1 px-2 py-1 text-xs bg-gray-200 text-gray-900 hover:bg-gray-300 rounded"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            <div className="space-y-2">
              {rules.map(rule => (
                <div
                  key={rule.id}
                  className="bg-gray-50 p-2 rounded text-sm border border-gray-200"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-xs text-gray-900">{rule.name}</span>
                    <button
                      onClick={() => handleDeleteRule(rule.id)}
                      className="text-xs text-red-600 hover:text-red-700"
                    >
                      Delete
                    </button>
                  </div>
                  <p className="text-xs text-gray-600 line-clamp-2">{rule.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

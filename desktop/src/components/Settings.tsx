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
      const data = await window.api.request('GET', '/api/rules/')
      setRules(data)
    } catch (error) {
      console.error('Error fetching rules:', error)
    }
  }

  const handleAddRule = async () => {
    if (!newRuleName.trim() || !newRuleContent.trim()) return

    try {
      await window.api.request('POST', '/api/rules/', {
        name: newRuleName,
        content: newRuleContent,
        active: true,
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
      await window.api.request('DELETE', `/api/rules/${id}`)
      fetchRules()
    } catch (error) {
      console.error('Error deleting rule:', error)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg w-96 max-h-96 overflow-y-auto">
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-200"
          >
            ✕
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Theme */}
          <div>
            <label className="block text-sm font-semibold mb-2">Theme</label>
            <select
              value={theme}
              onChange={e => onThemeChange(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-sm text-gray-100"
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="nord">Nord</option>
              <option value="dracula">Dracula</option>
            </select>
          </div>

          {/* Rules */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-semibold">Rules</label>
              <button
                onClick={() => setShowNewRule(true)}
                className="text-xs px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded"
              >
                + Add Rule
              </button>
            </div>

            {showNewRule && (
              <div className="bg-gray-700 p-3 rounded mb-3">
                <input
                  type="text"
                  value={newRuleName}
                  onChange={e => setNewRuleName(e.target.value)}
                  placeholder="Rule name"
                  className="w-full px-2 py-1 bg-gray-800 border border-gray-600 rounded text-sm text-gray-100 mb-2"
                />
                <textarea
                  value={newRuleContent}
                  onChange={e => setNewRuleContent(e.target.value)}
                  placeholder="Rule content"
                  className="w-full px-2 py-1 bg-gray-800 border border-gray-600 rounded text-sm text-gray-100 h-20 mb-2"
                />
                <div className="flex gap-2">
                  <button
                    onClick={handleAddRule}
                    className="flex-1 px-2 py-1 text-xs bg-green-600 hover:bg-green-700 rounded"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setShowNewRule(false)}
                    className="flex-1 px-2 py-1 text-xs bg-gray-600 hover:bg-gray-500 rounded"
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
                  className="bg-gray-700 p-2 rounded text-sm"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-xs">{rule.name}</span>
                    <button
                      onClick={() => handleDeleteRule(rule.id)}
                      className="text-xs text-red-400 hover:text-red-300"
                    >
                      Delete
                    </button>
                  </div>
                  <p className="text-xs text-gray-300 line-clamp-2">{rule.content}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

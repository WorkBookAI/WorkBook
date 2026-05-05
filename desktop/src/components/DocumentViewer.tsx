import { useState, useEffect } from 'react'

interface DocumentViewerProps {
  document: {
    id: string
    name: string
    file_type: string
    size: number
  }
}

export default function DocumentViewer({ document }: DocumentViewerProps) {
  const [content, setContent] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(0)

  useEffect(() => {
    fetchDocumentContent()
  }, [document.id])

  const fetchDocumentContent = async () => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/documents/${document.id}`)
      const data = await response.json()
      setContent(data)
      setCurrentPage(0)
    } catch (error) {
      console.error('Error fetching document:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600">Loading document...</p>
          </div>
        </div>
      )
    }

    if (!content || !content.content || content.content.length === 0) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-600">
            <p>No content extracted</p>
            <p className="text-sm text-gray-500 mt-2">Document may still be processing</p>
          </div>
        </div>
      )
    }

    const currentContent = content.content[currentPage]

    return (
      <div className="h-full flex flex-col">
        {/* Page Header */}
        <div className="px-8 py-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{document.name}</h2>
            <p className="text-xs text-gray-500 mt-1">Page {currentPage + 1} of {content.content.length}</p>
          </div>
          {content.content.length > 1 && (
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                disabled={currentPage === 0}
                className="px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                ← Previous
              </button>
              <button
                onClick={() => setCurrentPage(Math.min(content.content.length - 1, currentPage + 1))}
                disabled={currentPage === content.content.length - 1}
                className="px-3 py-1 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next →
              </button>
            </div>
          )}
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-3xl mx-auto">
            <div className="prose prose-sm max-w-none">
              {currentContent && (
                <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                  {currentContent.text || 'No text content'}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return <div className="h-full flex flex-col bg-white">{renderContent()}</div>
}

import { useState, useEffect } from 'react'
import * as pdfjsLib from 'pdfjs-dist'

interface DocumentViewerProps {
  document: {
    id: string
    name: string
    file_type: string
    size: number
  }
}

interface DocumentContent {
  type: string
  full_text?: string
  content?: any[]
  pages?: number
  slides?: number
}

pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`

export default function DocumentViewer({ document }: DocumentViewerProps) {
  const [content, setContent] = useState<DocumentContent | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(0)

  useEffect(() => {
    fetchDocumentContent()
  }, [document.id])

  const fetchDocumentContent = async () => {
    try {
      const data = await window.api.request('GET', `/api/documents/${document.id}`)
      setContent(data)
      setCurrentPage(0)
    } catch (error) {
      console.error('Error fetching document:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderContent = () => {
    if (loading) return <div className="text-center">Loading...</div>
    if (!content) return <div className="text-center text-gray-500">Failed to load content</div>

    switch (document.file_type) {
      case 'pdf':
      case 'docx':
      case 'pptx':
        return (
          <div className="space-y-4">
            {content.content && content.content.length > 0 ? (
              <>
                <div className="text-sm text-gray-400 mb-2">
                  Page {currentPage + 1} of {content.content.length}
                </div>
                <div className="bg-gray-700 p-4 rounded text-sm whitespace-pre-wrap break-words">
                  {content.content[currentPage]?.text || 'No content'}
                </div>
                {content.content.length > 1 && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                      disabled={currentPage === 0}
                      className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 rounded text-sm"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() => setCurrentPage(Math.min(content.content.length - 1, currentPage + 1))}
                      disabled={currentPage === content.content.length - 1}
                      className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 rounded text-sm"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div>No content extracted</div>
            )}
          </div>
        )
      case 'py':
      case 'js':
      case 'ts':
      case 'java':
      case 'cpp':
      case 'c':
      case 'go':
      case 'rs':
        return (
          <pre className="bg-gray-700 p-4 rounded text-sm overflow-auto">
            <code>{content.full_text}</code>
          </pre>
        )
      case 'txt':
      case 'md':
        return (
          <div className="bg-gray-700 p-4 rounded text-sm whitespace-pre-wrap break-words">
            {content.full_text}
          </div>
        )
      default:
        return <div className="text-center text-gray-500">Preview not available for {document.file_type}</div>
    }
  }

  return (
    <div className="flex-1 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h2 className="font-semibold truncate">{document.name}</h2>
        <div className="text-xs text-gray-400 mt-1">
          {document.file_type.toUpperCase()} • {(document.size / 1024).toFixed(2)} KB
        </div>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {renderContent()}
      </div>
    </div>
  )
}

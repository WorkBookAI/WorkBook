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
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDocumentContent()
  }, [document.id])

  const fetchDocumentContent = async () => {
    setError(null)
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/documents/${document.id}`)
      if (!response.ok) {
        throw new Error(`Failed to load document: ${response.statusText}`)
      }
      const data = await response.json()
      setContent(data)
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      console.error('Error fetching document:', err)
      setError(errorMsg)
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

    if (error) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center bg-red-50 p-8 rounded-lg max-w-md">
            <p className="text-red-700 font-semibold mb-2">Error Loading Document</p>
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        </div>
      )
    }

    if (!content) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center text-gray-600">
            <p>Failed to load document</p>
          </div>
        </div>
      )
    }

    const isPptx = document.file_type === 'pptx'
    const isPdf = document.file_type === 'pdf'
    const fileUrl = `http://127.0.0.1:8000/api/documents/${document.id}/file`
    const pdfUrl = isPptx ? `http://127.0.0.1:8000/api/documents/${document.id}/pdf` : fileUrl

    return (
      <div className="h-full flex flex-col">
        <div className="px-8 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-900">{document.name}</h2>
          {isPptx && <p className="text-xs text-gray-500 mt-1">Converting to PDF...</p>}
        </div>

        <div className="flex-1 overflow-hidden bg-gray-100">
          {isPdf || isPptx ? (
            <object
              data={pdfUrl}
              type="application/pdf"
              className="w-full h-full"
            >
              <div className="flex items-center justify-center h-full">
                <div className="text-center bg-yellow-50 p-8 rounded-lg">
                  <p className="text-yellow-700 font-semibold mb-2">PDF Viewer Unavailable</p>
                  <p className="text-yellow-600 text-sm mb-4">Could not display the PDF in this browser</p>
                  <a
                    href={pdfUrl}
                    download
                    className="text-blue-600 hover:text-blue-800 underline"
                  >
                    Download PDF
                  </a>
                </div>
              </div>
            </object>
          ) : (
            <div className="h-full overflow-y-auto p-8">
              <div className="max-w-4xl mx-auto bg-white rounded-lg p-8 shadow-sm">
                <div className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {content.full_text || content.content_extracted || 'No content available'}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return <div className="h-full flex flex-col bg-white">{renderContent()}</div>
}

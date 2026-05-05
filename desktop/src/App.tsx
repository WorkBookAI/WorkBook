import { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar'
import DocumentViewer from './components/DocumentViewer'
import ChatPane from './components/ChatPane'
import Settings from './components/Settings'
import './App.css'

interface Document {
  id: string
  name: string
  file_type: string
  size: number
  created_at: string
}

function App() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null)
  const [showSettings, setShowSettings] = useState(false)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/documents/')
      const data = await response.json()
      setDocuments(data)
    } catch (error) {
      console.error('Error fetching documents:', error)
    }
  }

  const handleUploadDocument = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    try {
      await fetch('http://127.0.0.1:8000/api/documents/upload', {
        method: 'POST',
        body: formData,
      })
      fetchDocuments()
    } catch (error) {
      console.error('Error uploading document:', error)
    }
  }

  const handleSelectDocument = (docId: string) => {
    setSelectedDocId(docId)
  }

  const selectedDoc = documents.find(d => d.id === selectedDocId)

  return (
    <div className="flex h-screen w-screen bg-gray-50">
      {/* Left Sidebar - Files */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">WorkBook</h1>
          <p className="text-xs text-gray-500 mt-1">Study Assistant</p>
        </div>

        <Sidebar
          documents={documents}
          selectedDocId={selectedDocId}
          onSelectDocument={handleSelectDocument}
          onUpload={handleUploadDocument}
          onSettings={() => setShowSettings(true)}
        />
      </div>

      {/* Center - Document Viewer */}
      <div className="flex-1 bg-white border-r border-gray-200 flex flex-col overflow-hidden">
        {selectedDoc ? (
          <DocumentViewer document={selectedDoc} />
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
            <div className="text-center max-w-md">
              <div className="mb-6">
                <svg className="w-20 h-20 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">No Document Selected</h2>
              <p className="text-gray-600 mb-6">Upload a document or select one from the left sidebar to begin studying</p>
              <button
                onClick={() => document.querySelector('input[type="file"]')?.click()}
                className="px-6 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors font-medium"
              >
                Upload Document
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Right Sidebar - Chat */}
      {selectedDoc && (
        <div className="w-96 bg-white border-l border-gray-200 flex flex-col">
          <ChatPane documentId={selectedDocId} />
        </div>
      )}

      {showSettings && (
        <Settings
          onClose={() => setShowSettings(false)}
          theme="light"
          onThemeChange={() => {}}
        />
      )}
    </div>
  )
}

export default App

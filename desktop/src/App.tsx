import { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar'
import DocumentViewer from './components/DocumentViewer'
import ChatPane from './components/ChatPane'
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
  const [conversations, setConversations] = useState([])

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const data = await window.api.request('GET', '/api/documents/')
      setDocuments(data)
    } catch (error) {
      console.error('Error fetching documents:', error)
    }
  }

  const handleUploadDocument = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://127.0.0.1:8000/api/documents/upload', {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
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
    <div className="flex h-screen w-screen bg-gray-900 text-gray-100">
      <Sidebar
        documents={documents}
        selectedDocId={selectedDocId}
        onSelectDocument={handleSelectDocument}
        onUpload={handleUploadDocument}
      />

      <div className="flex-1 flex">
        {selectedDoc ? (
          <>
            <DocumentViewer document={selectedDoc} />
            <ChatPane documentId={selectedDocId} />
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4">Welcome to WorkBook</h2>
              <p className="text-gray-400 mb-6">Upload a document or select one from the sidebar to get started</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

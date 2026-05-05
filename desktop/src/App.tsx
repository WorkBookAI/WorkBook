import { useEffect, useState } from 'react'
import Sidebar from './components/Sidebar'
import DocumentViewer from './components/DocumentViewer'
import ChatPane from './components/ChatPane'
import Settings from './components/Settings'
import { ThemeName, styleMap } from './themes'
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
  const [theme, setTheme] = useState<ThemeName>('dark')
  const [showSettings, setShowSettings] = useState(false)

  useEffect(() => {
    fetchDocuments()
    // Load theme from localStorage
    const savedTheme = localStorage.getItem('theme') as ThemeName
    if (savedTheme) setTheme(savedTheme)
  }, [])

  useEffect(() => {
    // Apply theme
    const style = document.createElement('style')
    style.textContent = styleMap[theme]
    document.head.appendChild(style)
    localStorage.setItem('theme', theme)
    return () => style.remove()
  }, [theme])

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
        onSettings={() => setShowSettings(true)}
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

      {showSettings && (
        <Settings
          onClose={() => setShowSettings(false)}
          theme={theme}
          onThemeChange={setTheme}
        />
      )}
    </div>
  )
}

export default App

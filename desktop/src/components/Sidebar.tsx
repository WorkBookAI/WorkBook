import { useState } from 'react'

interface SidebarProps {
  documents: any[]
  selectedDocId: string | null
  onSelectDocument: (docId: string) => void
  onUpload: (file: File) => void
}

export default function Sidebar({
  documents,
  selectedDocId,
  onSelectDocument,
  onUpload,
}: SidebarProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      onUpload(files[0])
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUpload(e.target.files[0])
    }
  }

  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">WorkBook</h1>
      </div>

      {/* Upload Area */}
      <div
        className={`m-4 p-4 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
          isDragging
            ? 'border-blue-500 bg-blue-500 bg-opacity-10'
            : 'border-gray-600 hover:border-gray-500'
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          className="hidden"
          onChange={handleFileInput}
          accept=".pdf,.docx,.pptx,.py,.js,.ts,.java,.cpp,.md,.txt,.png,.jpg,.jpeg"
        />
        <label htmlFor="file-input" className="block cursor-pointer">
          <div className="text-sm font-medium">Drag files here</div>
          <div className="text-xs text-gray-400 mt-1">or click to select</div>
        </label>
      </div>

      {/* Documents List */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 py-2">
          <h2 className="text-sm font-semibold text-gray-400 mb-2">Documents</h2>
          {documents.length === 0 ? (
            <p className="text-xs text-gray-500">No documents yet</p>
          ) : (
            <div className="space-y-1">
              {documents.map(doc => (
                <button
                  key={doc.id}
                  onClick={() => onSelectDocument(doc.id)}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                    selectedDocId === doc.id
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700'
                  }`}
                  title={doc.name}
                >
                  <div className="truncate">{doc.name}</div>
                  <div className="text-xs text-gray-400">{doc.file_type.toUpperCase()}</div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Settings */}
      <div className="p-4 border-t border-gray-700">
        <button className="w-full px-3 py-2 text-sm rounded bg-gray-700 hover:bg-gray-600 transition-colors">
          Settings
        </button>
      </div>
    </div>
  )
}

import { useState } from 'react'

interface SidebarProps {
  documents: any[]
  selectedDocId: string | null
  onSelectDocument: (docId: string) => void
  onUpload: (file: File) => void
  onSettings: () => void
}

export default function Sidebar({
  documents,
  selectedDocId,
  onSelectDocument,
  onUpload,
  onSettings,
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
    <div className="flex-1 flex flex-col">
      {/* Upload Area */}
      <div className="p-4">
        <div
          className={`p-4 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
            isDragging
              ? 'border-gray-900 bg-gray-100'
              : 'border-gray-300 hover:border-gray-400'
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
            <svg className="w-6 h-6 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            <div className="text-sm font-medium text-gray-900">Add File</div>
            <div className="text-xs text-gray-500 mt-1">or drag here</div>
          </label>
        </div>
      </div>

      {/* Documents List */}
      <div className="flex-1 overflow-y-auto px-4 py-2">
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Documents</h3>
        {documents.length === 0 ? (
          <p className="text-xs text-gray-500 text-center py-8">No documents yet</p>
        ) : (
          <div className="space-y-1">
            {documents.map(doc => (
              <button
                key={doc.id}
                onClick={() => onSelectDocument(doc.id)}
                className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                  selectedDocId === doc.id
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                title={doc.name}
              >
                <div className="truncate font-medium">{doc.name}</div>
                <div className="text-xs text-gray-500">{doc.file_type.toUpperCase()}</div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Settings */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={onSettings}
          className="w-full px-3 py-2 text-sm rounded bg-gray-100 text-gray-900 hover:bg-gray-200 transition-colors font-medium"
        >
          ⚙️ Settings
        </button>
      </div>
    </div>
  )
}

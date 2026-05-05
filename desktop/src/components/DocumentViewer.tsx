interface DocumentViewerProps {
  document: {
    id: string
    name: string
    file_type: string
    size: number
  }
}

export default function DocumentViewer({ document }: DocumentViewerProps) {
  return (
    <div className="flex-1 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h2 className="font-semibold truncate">{document.name}</h2>
        <div className="text-xs text-gray-400 mt-1">
          {document.file_type.toUpperCase()} • {(document.size / 1024).toFixed(2)} KB
        </div>
      </div>

      <div className="flex-1 overflow-auto flex items-center justify-center">
        <div className="text-center text-gray-500">
          <p className="mb-2">Document Preview</p>
          <p className="text-sm">Phase 2: Implement PDF/DOCX/PPTX viewers</p>
        </div>
      </div>
    </div>
  )
}

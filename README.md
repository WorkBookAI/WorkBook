# WorkBook

An AI-powered study companion with intelligent context management, document processing, and conversation branching.

## Features

- **Document Support**: Load and process PDF, DOCX, PPTX, code files, and plain text
- **Multi-LLM Support**: Works with local models (Ollama, LM Studio) and APIs (OpenAI, Anthropic)
- **Smart Chat**: Context-aware conversations with your study materials
- **Conversation Forking**: Branch conversations to explore different topics without losing context
- **Tool Calls**: Built-in tools for extracting context, adding notes, web search, summarization, and source citing
- **Rules System**: Define permanent rules for consistent AI behavior
- **Multiple Themes**: Dark, Light, Nord, and Dracula themes
- **Cross-Platform**: Windows, Linux, and macOS support

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.8+
- Electron (installed via npm)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

Backend runs on `http://localhost:8000`

### Frontend Setup

```bash
cd desktop
npm install
npm run dev
```

The app will start in dev mode with hot reload.

## Building

### Build Desktop App

```bash
cd desktop
npm run build
npm start
```

### Production Build

```bash
cd desktop
npm run build
npx electron-builder
```

## Configuration

### API Keys

API keys are stored locally in `~/.workbook/config.json` (encrypted).

To configure an API key:
1. Open Settings in the app
2. Add your API key for OpenAI or Anthropic

### Local Models

- **Ollama**: Must be running on `http://localhost:11434`
- **LM Studio**: Must be running on `http://localhost:1234`

Models are auto-detected when the app starts.

## Database

SQLite database is stored at `~/.workbook/workbook.db` and includes:
- Documents and their extracted content
- Conversations and messages
- Rules and configurations
- Notes on materials

## Architecture

```
WorkBook/
├── desktop/          # Electron + React + TypeScript
│   └── src/
│       ├── components/
│       ├── App.tsx
│       └── themes.ts
├── backend/          # FastAPI + SQLAlchemy
│   └── app/
│       ├── api/      # REST endpoints
│       ├── db/       # Database models
│       ├── core/     # LLM, document processing
│       └── tools/    # Tool implementations
└── WORKBOOK_PLAN/    # Planning documents
```

## API Endpoints

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List documents
- `GET /api/documents/{id}` - Get document
- `GET /api/documents/{id}/search?q=...` - Search document
- `DELETE /api/documents/{id}` - Delete document

### Conversations
- `POST /api/conversations` - Create conversation
- `GET /api/conversations` - List conversations
- `GET /api/conversations/{id}` - Get conversation with messages
- `POST /api/conversations/{id}/messages` - Add message and get LLM response
- `POST /api/conversations/{id}/fork?message_id=...` - Fork conversation
- `POST /api/conversations/{id}/merge` - Get merge suggestions
- `POST /api/conversations/{id}/merge-confirm` - Confirm merge
- `GET /api/conversations/{id}/tree` - Get branching tree

### Tools
- `POST /api/tools/extract-context` - Extract context from documents
- `POST /api/tools/suggest-note` - Add note to material
- `POST /api/tools/search-web` - Search the web
- `POST /api/tools/summarize` - Summarize material with chat context
- `POST /api/tools/answer-from-source` - Answer question from sources

### Rules
- `GET /api/rules` - List rules
- `POST /api/rules` - Create rule
- `PUT /api/rules/{id}` - Update rule
- `DELETE /api/rules/{id}` - Delete rule
- `GET /api/rules/export/memory` - Export as MEMORY.md format

### Models
- `GET /api/models` - List available models
- `POST /api/models/test` - Test model connection
- `POST /api/models/configure` - Configure API key

## Development

### Adding New Tools

Create a new file in `backend/app/tools/` and add the endpoint in `backend/app/api/tools.py`.

### Adding Components

New React components go in `desktop/src/components/`. Follow existing patterns.

### Database Changes

Update `backend/app/db/models.py`, then the database will auto-migrate on next run.

## Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed
- Check port 8000 is not in use
- Verify all dependencies: `pip install -r requirements.txt`

### No local models detected
- Ensure Ollama or LM Studio is running
- Check endpoints: `http://localhost:11434` (Ollama) or `http://localhost:1234` (LM Studio)

### Can't connect to API
- Verify API key is set in Settings
- Check network connection
- Ensure backend is running

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
# WorkBook Architecture

## Overview

WorkBook is a full-stack application split into frontend (Electron + React) and backend (FastAPI + SQLAlchemy).

## Backend Architecture

### Core Layers

**API Layer** (`/app/api/`)
- Documents: Upload, search, delete
- Chats: Manage conversations, messages, forking
- Tools: Execute context tools
- Models: Configure and test LLMs
- Rules: Manage system rules

**Core Services** (`/app/core/`)
- `llm.py`: LLM provider abstraction (Ollama, LM Studio, OpenAI, Anthropic)
- `document_processor.py`: Extract text/images from documents
- `search.py`: Full-text search
- `config.py`: Configuration management

**Tools** (`/app/tools/`)
- `extract_context.py`: Find relevant document excerpts
- `suggest_note.py`: Propose notes for materials
- `search_web.py`: Web search (stub for external API)
- `summarize.py`: Summarize with chat history
- `answer_from_source.py`: Answer with citations

**Database Layer** (`/app/db/`)
- SQLAlchemy ORM models
- SQLite database in `~/.workbook/workbook.db`

### Data Flow

1. **Document Upload**
   - File → `documents.py` (upload endpoint)
   - Extract via `DocumentProcessor`
   - Store in DB with indexed content

2. **Chat**
   - User message → `chats.py`
   - Build message history + context
   - Call LLM via `LLMManager`
   - Store user + assistant messages in DB
   - Return response

3. **Tool Execution**
   - Message contains tool request → `tools.py`
   - Execute tool logic (extract, note, summarize, etc.)
   - Return results to LLM context

## Frontend Architecture

### Component Hierarchy

```
App
├── Sidebar (documents, conversations, settings button)
├── DocumentViewer (preview)
├── ChatPane (messages, fork button)
│   └── MergePanel (merge suggestions)
├── ConversationTree (branching view)
├── Settings (rules, themes)
└── Theme Manager
```

### State Management

- **React hooks** for local component state
- **localStorage** for theme/preferences
- **API calls** via `window.api.request()` (Electron IPC bridge)

### Styling

- **Tailwind CSS** for utilities
- **CSS variables** for theme switching
- **Themes**: Dark, Light, Nord, Dracula

## IPC Bridge (Electron)

- Main process (`main.ts`) handles HTTP requests from renderer
- Renderer (`App.tsx`) calls `window.api.request(method, url, data)`
- All requests proxied to backend on `http://127.0.0.1:8000`

## LLM Integration

### Provider Pattern

Each provider implements `LLMProvider` interface:
- `async chat()` - single response
- `async stream()` - streaming response

Providers:
- `OllamaProvider` - `/api/chat` endpoint
- `LMStudioProvider` - OpenAI-compatible `/v1/chat/completions`
- `OpenAIProvider` - OpenAI SDK
- `AnthropicProvider` - Anthropic SDK

### Auto-Detection

`LLMManager.detect_local_models()` pings both Ollama and LM Studio endpoints.

## Database Schema

### Documents
- id, name, file_type, path, size, content_extracted, metadata

### Conversations
- id, name, document_id, parent_conversation_id, is_merged_to_parent

### Messages
- id, conversation_id, role, content, model_used, tokens_used, tools_called, cited_sources

### Notes
- id, document_id, page_number, content, added_by

### Rules
- id, name, content, active, created_at

## Tool Calls System

Tools are stateless functions that:
1. Receive input via API
2. Execute logic (search, process, etc.)
3. Return structured output
4. Can modify DB (notes, rules)

System prompt includes tool descriptions for LLMs.

## Conversation Branching

**Fork**: Deep copy all messages up to fork point into new conversation
**Merge**: Copy new messages from fork into parent, mark fork as merged

Tree structure preserved via `parent_conversation_id` foreign key.

## Configuration

Stored in `~/.workbook/config.json`:
```json
{
  "api_keys": {
    "openai": "...",
    "anthropic": "..."
  },
  "local_models": {},
  "theme": "dark"
}
```

API keys encrypted at rest (future enhancement).

## Cross-Platform Considerations

- **Paths**: Use `Path.home()` for user directory
- **Database**: SQLite (no external dependencies)
- **Electron**: Native APIs work on all platforms
- **Styling**: CSS variables for theme consistency

## Future Extensibility

- **New Tools**: Add to `/app/tools/`, register in `/app/api/tools.py`
- **New Providers**: Implement `LLMProvider` in `llm.py`
- **New Document Types**: Update `DocumentProcessor`
- **New Themes**: Add to `themes.ts` and `styleMap`

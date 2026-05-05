# Contributing to WorkBook

Thank you for interest in contributing! Here's how to help.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork>`
3. Create a branch: `git checkout -b feature/your-feature`

## Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

### Frontend
```bash
cd desktop
npm install
npm run dev
```

## Code Style

- **Python**: Follow PEP 8, use type hints
- **TypeScript/React**: Use ESLint, Prettier setup (run before commit)
- **Commit messages**: Short, imperative, focus on what not why

## Adding Features

1. **Backend**: Create new endpoints in `/app/api/`, database models in `/app/db/models.py`
2. **Frontend**: Add components in `/desktop/src/components/`
3. **Tests**: Add tests in `/backend/tests/` if applicable

## Testing

```bash
# Backend (add tests as needed)
cd backend
pytest

# Frontend
cd desktop
npm test
```

## Submitting Changes

1. Push to your fork
2. Create a Pull Request with:
   - Clear title
   - Description of what changed and why
   - Link any related issues
3. Wait for review and feedback
4. Address feedback and push updates

## Architecture Notes

- **Backend**: FastAPI with SQLAlchemy ORM, modular by feature
- **Frontend**: React + TypeScript with component-based structure
- **Database**: SQLite with auto-migration
- **LLM Integration**: Abstracted via provider pattern for easy additions

## Questions?

Open an issue with the `question` label.

## Code of Conduct

- Be respectful
- Assume good intent
- Focus on the work, not the person

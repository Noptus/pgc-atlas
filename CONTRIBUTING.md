# Contributing to PGC Atlas

Thank you for your interest in contributing to PGC Atlas!

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

## Development Setup

```bash
# Backend
pip install -e ".[dev]"
uvicorn api.app:app --reload

# Frontend
cd dashboard
npm install
npm run dev
```

## Code Style

- **Python**: Follow PEP 8, use type hints, write docstrings
- **TypeScript**: Use strict mode, prefer functional components
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)

## Adding a New Visualization

1. Create a data generator in `pgc_explorer/` (return Plotly-compatible dicts)
2. Add an API endpoint in `api/routes/plots.py`
3. Create a React component in `dashboard/src/components/`
4. Add mock data generation in `dashboard/src/api/client.ts`

## Reporting Issues

Please include:
- Steps to reproduce
- Expected vs actual behavior
- Browser/Python version
- Relevant error messages

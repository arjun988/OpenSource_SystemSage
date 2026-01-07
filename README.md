# OpenSource SystemSage 🤖

An advanced AI-powered system assistant built with Electron, React, and Flask. Features voice commands, system control, file operations, and intelligent conversation capabilities.

## 🚀 Features

- **Voice Commands**: Speech-to-text with continuous transcription
- **System Control**: Volume, brightness, and application management
- **File Operations**: Create, edit, and manage files/folders
- **AI Conversations**: Powered by Google Gemini 2.0 Flash
- **Command Mode**: Execute system commands and scripts
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## 🛠️ Installation

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py
```

### Frontend Tests

```bash
cd frontend
# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run linting
npm run lint
```

### Full Test Suite

```bash
# Backend tests
cd backend && pytest --cov=. --cov-report=xml

# Frontend tests
cd ../frontend && npm run test:coverage && npm run test:e2e
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
gemini_gpt_key=your_google_gemini_api_key_here
FLASK_ENV=development
```

### Test Configuration

- **Backend**: `pytest.ini` and `conftest.py`
- **Frontend**: `jest.config.js` and `playwright.config.js`
- **Coverage**: 80% threshold for both frontend and backend

## 🏗️ Development

### Running the Application

```bash
# Start both frontend and backend
cd frontend
npm run start

# Or run separately:
# Terminal 1: Backend
cd backend
python app.py

# Terminal 2: Frontend
cd frontend
npm run start:react
```

### Building for Production

```bash
cd frontend
npm run build
```

## 📊 Testing Strategy

### Backend Testing (Flask API)
- **Unit Tests**: Individual function testing with mocks
- **Integration Tests**: API endpoint testing
- **Database Tests**: SQLite operations
- **External API Tests**: Gemini AI integration
- **System Operation Tests**: Volume, brightness, file operations

### Frontend Testing (React/Electron)
- **Component Tests**: React component rendering and interactions
- **Integration Tests**: Component communication
- **E2E Tests**: Full user workflow testing with Playwright
- **Accessibility Tests**: ARIA labels and keyboard navigation

### Coverage Requirements
- **Backend**: 80% coverage (functions, lines, statements)
- **Frontend**: 70% coverage (React components and utilities)

## 🚀 CI/CD Pipeline

### GitHub Actions Workflows

1. **Backend Tests**: Python 3.8, 3.9, 3.10, 3.11 with pytest-cov
2. **Frontend Tests**: Node.js 16, 18, 20 with Jest and Playwright
3. **E2E Tests**: Full-stack integration testing
4. **Linting**: ESLint for frontend, flake8/black for backend
5. **Security**: Dependency vulnerability scanning
6. **Build**: Package building and distribution

### Quality Gates

- ✅ All tests pass
- ✅ Coverage thresholds met
- ✅ No linting errors
- ✅ Security scan clean
- ✅ Build successful

## 📈 Test Coverage

### Backend Coverage Areas
- Flask API endpoints (`/chat`, `/command`, `/health`)
- System command handlers (volume, brightness, file ops)
- Database operations (SQLite chat history)
- External integrations (Gemini AI, speech recognition)
- Error handling and edge cases

### Frontend Coverage Areas
- React components (App, ChatWindow)
- User interactions (typing, clicking, voice input)
- State management (messages, modes, recording)
- API communication (fetch requests)
- UI responsiveness and accessibility

## 🐛 Debugging Tests

### Common Issues

```bash
# Backend test issues
# Check Python path
python -c "import sys; print(sys.path)"

# Frontend test issues
# Clear Jest cache
npm test -- --clearCache

# E2E test issues
# Check if dev server is running
curl http://localhost:3000
```

### Test Data

- Mock API responses for external services
- Test fixtures for consistent data
- Environment-specific configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Run tests
npm run test:coverage  # frontend
pytest --cov=.        # backend

# 3. Add tests for new code
# 4. Commit with descriptive message
git commit -m "Add new feature with tests

- Implement feature X
- Add tests for Y
- Update documentation

Closes #123"

# 5. Push and create PR
git push origin feature/new-feature
```

## 📝 API Documentation

### Backend Endpoints

- `POST /chat` - Send chat messages
- `POST /command` - Execute system commands
- `POST /transcribe` - Speech-to-text transcription
- `GET /chat_history` - Retrieve conversation history
- `GET /health` - Health check

### Frontend Components

- **App**: Main application container
- **ChatWindow**: Primary chat interface with voice/text input

## 🔒 Security

- Environment variables for API keys
- Input validation and sanitization
- Secure file operations
- Dependency vulnerability scanning
- No sensitive data in logs

## 📄 License

ISC License - see LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for conversational capabilities
- Electron for cross-platform desktop app framework
- React for modern UI development
- Flask for robust backend API

---

**Made with ❤️ for the open source community**

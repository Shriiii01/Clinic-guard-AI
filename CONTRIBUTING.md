# Contributing to ClinicGuard-AI

Thank you for your interest in contributing to ClinicGuard-AI! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

We welcome contributions from the community! Here are the main ways you can contribute:

### 🐛 Bug Reports
- Use the [GitHub Issues](https://github.com/Shriiii01/Clinic-guard-AI/issues) page
- Include a clear description of the bug
- Provide steps to reproduce the issue
- Include system information and error logs

### 💡 Feature Requests
- Use the [GitHub Issues](https://github.com/Shriiii01/Clinic-guard-AI/issues) page
- Describe the feature and its benefits
- Include use cases and examples
- Consider implementation complexity

### 📝 Code Contributions
- Fork the repository
- Create a feature branch
- Make your changes
- Add tests for new functionality
- Submit a pull request

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git
- Docker (optional)
- Twilio Account (for testing)
- ElevenLabs API Key (for testing)

### Local Development
1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Clinic-guard-AI.git
   cd Clinic-guard-AI
   ```

2. **Set up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r server/requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run Development Server**
   ```bash
   cd server
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New functionality includes tests
- [ ] Documentation is updated
- [ ] No sensitive data is included

### Pull Request Process
1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clear, readable code
   - Add comments for complex logic
   - Follow existing code patterns

3. **Test Your Changes**
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=server
   
   # Run linting
   flake8 server/
   black server/
   ```

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format
We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add JWT authentication
fix(tts): resolve audio generation timeout
docs(readme): update installation instructions
```

## 🧪 Testing Guidelines

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_conversation.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=server --cov-report=html
```

### Writing Tests
- Test both success and failure cases
- Use descriptive test names
- Mock external dependencies
- Test edge cases and error conditions

### Test Structure
```python
def test_feature_name():
    """Test description."""
    # Arrange
    # Act
    # Assert
```

## 📚 Code Style Guidelines

### Python Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Keep functions small and focused
- Use descriptive variable names

### Code Formatting
```bash
# Format code
black server/
isort server/

# Check formatting
black --check server/
isort --check-only server/
```

### Linting
```bash
# Run linter
flake8 server/

# Type checking
mypy server/
```

## 🔒 Security Guidelines

### Sensitive Information
- Never commit API keys, passwords, or tokens
- Use environment variables for configuration
- Update `.env.example` with new variables
- Add new sensitive files to `.gitignore`

### Security Best Practices
- Validate all inputs
- Use parameterized queries for database operations
- Implement proper authentication and authorization
- Follow OWASP security guidelines

## 📖 Documentation Guidelines

### Code Documentation
- Use docstrings for functions and classes
- Follow Google or NumPy docstring format
- Include examples for complex functions

### README Updates
- Update README.md for new features
- Include setup instructions for new dependencies
- Update API documentation

## 🏷️ Issue Labels

We use the following labels to categorize issues:

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority: high`: High priority issues
- `priority: low`: Low priority issues

## 🎯 Getting Help

### Questions and Discussions
- Use [GitHub Discussions](https://github.com/Shriiii01/Clinic-guard-AI/discussions)
- Check existing issues and discussions
- Be specific about your question

### Community Guidelines
- Be respectful and inclusive
- Help others when you can
- Follow the project's code of conduct
- Provide constructive feedback

## 📄 License

By contributing to ClinicGuard-AI, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- The project README
- Release notes
- GitHub contributors page

Thank you for contributing to ClinicGuard-AI! 🏥 
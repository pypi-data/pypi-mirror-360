# Contributing to fp-admin

Thank you for your interest in contributing to fp-admin! This document provides guidelines and information for contributors.

## 🚧 Project Status

fp-admin is currently in **beta development**. This means:

- APIs may change between versions
- Features are being actively developed
- We welcome feedback and contributions
- Production use is not yet recommended

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)
- [Community](#community)

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Git
- uv (recommended) or pip
- Node.js 18+ (for UI development)

### Quick Setup

```bash
# Fork and clone the repository
git clone https://github.com/esmairi/fp-admin.git
cd fp-admin

# Install dependencies
uv sync --all-extras --dev

# Install pre-commit hooks
uv run pre-commit install

# Set up the database
fp-admin make-migrations --name initial
fp-admin migrate

# Run tests to verify setup
pytest
```

## 🔧 Development Setup

### Backend Development

The backend is built with FastAPI, SQLModel, and Pydantic:

```bash
# Install backend dependencies
uv sync --all-extras --dev

# Run the development server
python main.py

# Run tests
pytest

# Run linting
uv run pre-commit run --all-files
```

### Frontend Development

The UI is a separate React project:

```bash
# Clone the UI repository
git clone https://github.com/esmairi/fp-admin-ui.git
cd fp-admin-ui

# Install dependencies
npm install

# Start development server
npm run dev
```

### Database Setup

```bash
# Create initial migration
fp-admin make-migrations --name initial

# Apply migrations
fp-admin migrate

# Create superuser
fp-admin createsuperuser
```

## 📝 Code Style

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Use meaningful variable and function names
- Keep functions small and focused

```python
from typing import List, Optional
from pydantic import BaseModel

def process_user_data(user_id: int, include_metadata: bool = False) -> Optional[dict]:
    """
    Process user data and return formatted information.

    Args:
        user_id: The ID of the user to process
        include_metadata: Whether to include metadata in the result

    Returns:
        Formatted user data or None if user not found
    """
    # Implementation here
    pass
```

### TypeScript/JavaScript Code

- Follow ESLint configuration
- Use TypeScript for all new code
- Write JSDoc comments for public functions
- Use meaningful variable names
- Prefer functional components in React

```typescript
/**
 * Process form data and return validation results
 * @param data - The form data to validate
 * @param schema - The validation schema
 * @returns Validation result with errors if any
 */
export const validateFormData = (
  data: FormData,
  schema: ValidationSchema
): ValidationResult => {
  // Implementation here
};
```

### Git Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(admin): add new field type for file uploads`
- `fix(validation): resolve email validation regex issue`
- `docs(readme): update installation instructions`
- `test(fields): add unit tests for multi-choice fields`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m e2e

# Run with coverage
pytest --cov=fp_admin --cov-report=html

# Run specific test file
pytest tests/unit/admin/fields/test_base.py

# Run with verbose output
pytest -v
```

### Writing Tests

- Write tests for all new functionality
- Maintain >90% code coverage
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup

```python
import pytest
from fp_admin.admin.fields import FieldView

class TestFieldView:
    """Test cases for FieldView class."""

    def test_text_field_creation(self) -> None:
        """Test basic text field creation."""
        field = FieldView.text_field("name", "Full Name", required=True)

        assert field.name == "name"
        assert field.title == "Full Name"
        assert field.field_type == "text"
        assert field.required is True
```

### Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows
- **Performance Tests**: Test performance characteristics

## 📤 Submitting Changes

### 1. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write your code following the style guidelines
- Add tests for new functionality
- Update documentation if needed
- Ensure all tests pass

### 3. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with conventional commit message
git commit -m "feat(admin): add new field type for file uploads"

# Push to your fork
git push origin feature/your-feature-name
```

### 4. Create a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the PR template
5. Submit the PR

### 5. PR Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 🐛 Issue Guidelines

### Reporting Bugs

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - Operating system
   - fp-admin version
   - Dependencies versions

2. **Steps to Reproduce**
   - Clear, step-by-step instructions
   - Minimal code example
   - Expected vs actual behavior

3. **Error Information**
   - Full error traceback
   - Log files if applicable
   - Screenshots if UI-related

### Example Bug Report

```markdown
## Bug Description
The email validation field is not working correctly.

## Environment
- Python: 3.12.0
- OS: Ubuntu 22.04
- fp-admin: 0.0.3beta

## Steps to Reproduce
1. Create a new field with email validation
2. Enter invalid email format
3. Submit the form

## Expected Behavior
Form should show validation error for invalid email

## Actual Behavior
Form accepts invalid email without error

## Code Example
```python
field = FieldView.email_field("email", "Email")
```

## Error Information
No error messages, but validation is not working
```

## 💡 Feature Requests

### Guidelines for Feature Requests

1. **Clear Description**: Explain what you want to achieve
2. **Use Case**: Describe why this feature is needed
3. **Examples**: Provide code examples of how it would be used
4. **Alternatives**: Consider existing solutions
5. **Implementation**: Suggest implementation approach if possible

### Example Feature Request

```markdown
## Feature Description
Add support for image cropping in file upload fields

## Use Case
Users need to crop profile pictures and product images before upload

## Proposed API
```python
field = FieldView.image_field(
    "avatar",
    "Profile Picture",
    crop_enabled=True,
    crop_aspect_ratio="1:1"
)
```

## Implementation Notes
- Could use a JavaScript cropping library
- Need to handle server-side image processing
- Should support multiple aspect ratios
```

## 📚 Documentation

### Contributing to Documentation

We welcome documentation improvements:

1. **Code Examples**: Clear, working examples
2. **Tutorials**: Step-by-step guides
3. **API Reference**: Comprehensive documentation
4. **Best Practices**: Development guidelines

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep examples up-to-date
- Use proper markdown formatting
- Add screenshots for UI features

## 🤝 Community

### Getting Help

- **GitHub Issues**: [Report bugs and request features](https://github.com/esmairi/fp-admin/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/esmairi/fp-admin/discussions)
- **Discord**: Join our community server (link TBD)

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) for details.

### Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes
- Project documentation
- Community acknowledgments

## 🎯 Development Priorities

Current development priorities:

1. **API Stability**: Stabilizing the core API
2. **Field Types**: Expanding field type support
3. **UI Components**: Enhancing React components
4. **Documentation**: Comprehensive guides and examples
5. **Testing**: Improving test coverage
6. **Performance**: Optimizing for large datasets

## 📞 Contact

- **Maintainers**: [@esmairi](https://github.com/esmairi)
- **Issues**: [GitHub Issues](https://github.com/esmairi/fp-admin/issues)
- **Discussions**: [GitHub Discussions](https://github.com/esmairi/fp-admin/discussions)

---

Thank you for contributing to fp-admin! 🚀

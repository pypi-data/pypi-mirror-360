# Contributing to DUKE Agents

First off, thank you for considering contributing to DUKE Agents! It's people like you that make DUKE Agents such a great tool. We welcome contributions from everyone, whether it's a bug report, feature request, documentation improvement, or code contribution.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Guidelines](#development-guidelines)
  - [Code Style](#code-style)
  - [Type Hints](#type-hints)
  - [Documentation](#documentation)
  - [Testing](#testing)
  - [Commit Messages](#commit-messages)
- [Project Structure](#project-structure)
- [Release Process](#release-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to smasson@duke-ai.io.

### Our Standards

- **Be Respectful**: Treat everyone with respect. No harassment, discrimination, or inappropriate behavior.
- **Be Collaborative**: Work together to resolve conflicts and assume good intentions.
- **Be Professional**: Keep discussions focused on the project and constructive.
- **Be Inclusive**: Welcome newcomers and help them get started.

## Getting Started

1. **Fork the Repository**: Click the "Fork" button on the [DUKE Agents GitHub page](https://github.com/elmasson/duke-agents)
2. **Clone Your Fork**: 
   ```bash
   git clone https://github.com/YOUR-USERNAME/duke-agents.git
   cd duke-agents
   ```
3. **Add Upstream Remote**:
   ```bash
   git remote add upstream https://github.com/elmasson/duke-agents.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip and virtualenv
- Git
- A Mistral API key for testing

### Setting Up Your Development Environment

1. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Development Dependencies**:
   ```bash
   pip install -e ".[dev,docs]"
   ```

3. **Install Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   MISTRAL_API_KEY=your_test_api_key
   DUKE_ENV=development
   ```

5. **Verify Installation**:
   ```bash
   # Run tests
   pytest
   
   # Check code style
   black --check src/
   flake8 src/
   mypy src/
   ```

### IDE Setup

#### VS Code

1. Install Python extension
2. Use the provided `.vscode/settings.json`:
   ```json
   {
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": false,
     "python.linting.flake8Enabled": true,
     "python.formatting.provider": "black",
     "python.testing.pytestEnabled": true,
     "editor.formatOnSave": true
   }
   ```

#### PyCharm

1. Set the project interpreter to your virtual environment
2. Enable Black formatter: Settings → Tools → Black
3. Configure pytest as the test runner

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

1. **Clear Title**: Summarize the issue
2. **Description**: What you expected vs. what happened
3. **Steps to Reproduce**: Minimal code example
4. **Environment**: Python version, OS, DUKE Agents version
5. **Stack Trace**: Full error message if applicable

**Bug Report Template**:
```markdown
### Description
Brief description of the bug

### Steps to Reproduce
1. Code example:
   ```python
   # Your code here
   ```
2. Run the code
3. See error

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Environment
- DUKE Agents version: X.X.X
- Python version: 3.X
- OS: [Windows/Mac/Linux]
- Mistral API version: X.X.X
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

1. **Use Case**: Why is this enhancement needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Mockups, diagrams, examples

### Pull Requests

1. **Create a Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

2. **Make Your Changes**: Follow the development guidelines below

3. **Test Your Changes**:
   ```bash
   # Run all tests
   pytest
   
   # Run specific test file
   pytest tests/test_specific.py
   
   # Run with coverage
   pytest --cov=duke_agents --cov-report=html
   ```

4. **Update Documentation**: If you're changing functionality, update:
   - Docstrings
   - README.md if needed
   - Example scripts if applicable

5. **Commit Your Changes**: Use meaningful commit messages (see below)

6. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**: Go to GitHub and create a PR from your fork

#### PR Checklist

- [ ] Tests pass locally (`pytest`)
- [ ] Code follows style guidelines (`black`, `flake8`, `mypy`)
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] PR description explains the changes
- [ ] Breaking changes are noted
- [ ] New dependencies are justified

## Development Guidelines

### Code Style

We use several tools to maintain code quality:

1. **Black** for code formatting:
   ```bash
   black src/ tests/
   ```

2. **isort** for import sorting:
   ```bash
   isort src/ tests/
   ```

3. **Flake8** for linting:
   ```bash
   flake8 src/ tests/
   ```

4. **MyPy** for type checking:
   ```bash
   mypy src/
   ```

#### Style Guidelines

- Line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public functions/classes
- Keep functions focused and small
- Avoid deep nesting (max 3 levels)

### Type Hints

All code must include type hints:

```python
from typing import Dict, List, Optional, Union

def process_data(
    input_data: Dict[str, Any],
    options: Optional[List[str]] = None
) -> Union[str, Dict[str, Any]]:
    """Process input data with optional parameters.
    
    Args:
        input_data: The data to process
        options: Optional processing options
        
    Returns:
        Processed result as string or dictionary
    """
    ...
```

### Documentation

#### Docstring Format

We use Google-style docstrings:

```python
def complex_function(param1: str, param2: int = 0) -> Dict[str, Any]:
    """Brief description of function.
    
    Longer description if needed, explaining the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2. Defaults to 0.
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result["status"])
        success
    """
    ...
```

#### Documentation Updates

- Update docstrings when changing function signatures
- Add examples for complex functionality
- Keep README.md examples up to date
- Document breaking changes in CHANGELOG.md

### Testing

#### Writing Tests

1. **Test File Naming**: `test_<module_name>.py`
2. **Test Class Naming**: `Test<ClassName>`
3. **Test Method Naming**: `test_<method_name>_<scenario>`

Example test:

```python
import pytest
from duke_agents import AtomicAgent
from duke_agents.models import AtomicInput, AtomicOutput

class TestAtomicAgent:
    """Test cases for AtomicAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create a test agent."""
        return AtomicAgent("test_agent")
    
    def test_process_valid_input(self, agent, mock_llm_response):
        """Test processing with valid input."""
        input_data = AtomicInput(
            task_id="test_001",
            parameters={"key": "value"}
        )
        
        result = agent.process(input_data)
        
        assert isinstance(result, AtomicOutput)
        assert result.success is True
        assert result.task_id == "test_001"
    
    def test_process_invalid_input(self, agent):
        """Test processing with invalid input."""
        with pytest.raises(ValueError):
            agent.process(None)
    
    @pytest.mark.parametrize("retry_count,expected_calls", [
        (1, 1),
        (3, 3),
        (5, 5),
    ])
    def test_retry_behavior(self, agent, retry_count, expected_calls, mock_llm):
        """Test retry behavior with different counts."""
        agent.max_retries = retry_count
        # ... test implementation
```

#### Test Coverage

- Aim for >90% code coverage
- Test edge cases and error conditions
- Use mocks for external dependencies (LLM calls, file I/O)
- Test both success and failure paths

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Maintenance tasks
- `perf`: Performance improvements

#### Examples

```
feat(agents): add async support for AtomicAgent

- Implement async process method
- Add tests for async behavior
- Update documentation

Closes #123
```

```
fix(memory): prevent memory leak in long workflows

The WorkflowMemory class was retaining references to all
intermediate results. This implements automatic pruning
of old records based on configurable limits.

Fixes #456
```

## Project Structure

```
duke-agents/
├── src/duke_agents/       # Main package source
│   ├── agents/           # Agent implementations
│   ├── models/           # Pydantic models
│   ├── orchestration/    # Workflow orchestration
│   ├── executors/        # Code execution
│   ├── llm/             # LLM integrations
│   └── config.py        # Configuration
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── fixtures/       # Test fixtures
├── examples/           # Example scripts
├── docs/              # Sphinx documentation
├── scripts/           # Development scripts
└── benchmarks/        # Performance benchmarks
```

### Adding New Features

1. **New Agent Type**:
   - Extend `BaseAgent` in `agents/`
   - Create models in `models/`
   - Add tests in `tests/unit/agents/`
   - Update documentation

2. **New LLM Provider**:
   - Implement client in `llm/`
   - Add configuration options
   - Create adapter tests
   - Document usage

3. **New Workflow Feature**:
   - Modify `orchestration/`
   - Update models if needed
   - Add comprehensive tests
   - Provide examples

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Release Steps

1. **Update Version**: 
   - `src/duke_agents/__version__.py`
   - `pyproject.toml`

2. **Update CHANGELOG.md**: Document all changes

3. **Create Release PR**: 
   ```bash
   git checkout -b release/vX.Y.Z
   ```

4. **Run Full Test Suite**:
   ```bash
   tox  # Runs tests on all Python versions
   ```

5. **Tag Release**:
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push upstream --tags
   ```

6. **Deploy to PyPI**: Automated via GitHub Actions

## Community

### Getting Help

- **Documentation**: [GitHub Docs](https://github.com/elmasson/duke-agents/tree/main/docs)
- **Discussions**: [GitHub Discussions](https://github.com/elmasson/duke-agents/discussions)
- **Issues**: [GitHub Issues](https://github.com/elmasson/duke-agents/issues)

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Email**: smasson@duke-ai.io for sensitive matters

### Recognition

Contributors will be:
- Listed in the AUTHORS file
- Mentioned in release notes
- Given credit in documentation

## Advanced Topics

### Performance Optimization

When contributing performance improvements:

1. **Benchmark First**: Measure current performance
2. **Profile Code**: Identify bottlenecks
3. **Implement Changes**: Focus on hot paths
4. **Benchmark Again**: Prove improvement
5. **Document Results**: Include benchmark data in PR

### Security Considerations

- Never commit API keys or secrets
- Validate all user inputs
- Use secure defaults
- Document security implications
- Report security issues privately to smasson@duke-ai.io

### Backward Compatibility

- Deprecate before removing
- Provide migration guides
- Use feature flags for breaking changes
- Maintain compatibility for 2 minor versions

---

Thank you for contributing to DUKE Agents! Your efforts help make this project better for everyone. If you have questions, don't hesitate to ask in the discussions or reach out to the maintainers.

Happy coding! 🚀
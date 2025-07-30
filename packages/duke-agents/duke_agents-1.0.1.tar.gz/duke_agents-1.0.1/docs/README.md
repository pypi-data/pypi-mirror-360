# DUKE Agents Documentation

This directory contains the documentation for DUKE Agents, built with Sphinx.

## Setting Up ReadTheDocs

To set up ReadTheDocs for this project:

1. **Create ReadTheDocs Account**
   - Go to [readthedocs.org](https://readthedocs.org)
   - Sign up or log in with your GitHub account

2. **Import the Project**
   - Click "Import a Project"
   - Select the duke-agents repository from GitHub
   - Use these settings:
     - Name: `duke-agents`
     - Repository URL: `https://github.com/elmasson/duke-agents`
     - Repository type: Git
     - Default branch: main

3. **Configure the Build**
   - The `.readthedocs.yaml` file is already configured
   - It will automatically:
     - Use Python 3.11
     - Install dependencies from requirements.txt
     - Build HTML, PDF, and EPUB formats

4. **Update Links**
   Once ReadTheDocs is set up and building successfully:
   - Update README.md to use the ReadTheDocs URL
   - Update pyproject.toml Documentation URL
   - Update CONTRIBUTING.md links

## Building Documentation Locally

### Prerequisites

Install documentation dependencies:

```bash
pip install -e ".[docs]"
```

### Building HTML Documentation

```bash
cd docs
make html
```

The built documentation will be in `docs/_build/html/`.

### Building Other Formats

```bash
# PDF (requires LaTeX)
make latexpdf

# EPUB
make epub

# Clean build files
make clean
```

### Live Reload for Development

Use sphinx-autobuild for live reload:

```bash
pip install sphinx-autobuild
sphinx-autobuild docs docs/_build/html
```

Then open http://localhost:8000 in your browser.

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation index
├── installation.md      # Installation guide
├── quickstart.md        # Quick start guide
├── examples.md          # Usage examples
├── concepts.md          # Core concepts
├── agents.md            # Agent documentation
├── orchestration.md     # Orchestration guide
├── memory.md            # Memory management
├── configuration.md     # Configuration options
├── api/                 # API reference (auto-generated)
│   ├── agents.rst
│   ├── models.rst
│   ├── orchestration.rst
│   ├── executors.rst
│   └── llm.rst
├── contributing.md      # Link to CONTRIBUTING.md
└── changelog.md         # Link to CHANGELOG.md
```

## Adding New Documentation

1. **Create new .md or .rst file** in the appropriate location
2. **Add to toctree** in index.rst or relevant parent document
3. **Follow style guide**:
   - Use clear, concise language
   - Include code examples
   - Add cross-references
   - Test all code snippets

## API Documentation

API documentation is auto-generated from docstrings using autodoc.

To update API docs:
1. Ensure all code has proper docstrings
2. Run `make html` to regenerate

## Style Guide

- Use Markdown for narrative documentation
- Use reStructuredText for complex formatting
- Follow Google-style docstrings in code
- Include examples in all user-facing docs
- Keep line length under 80 characters
- Use semantic line breaks

## Troubleshooting

### Common Issues

1. **ImportError during build**
   - Ensure duke-agents is installed: `pip install -e .`
   - Check Python path in conf.py

2. **Missing sphinx-rtd-theme**
   - Install docs dependencies: `pip install -r docs/requirements.txt`

3. **LaTeX errors (PDF build)**
   - Install LaTeX: `apt-get install texlive-full` (Linux)
   - Or use Docker: `docker run --rm -v $(pwd):/docs sphinxdoc/sphinx-latexpdf make latexpdf`

## Maintenance

- Review and update documentation with each release
- Check for broken links regularly
- Keep examples up to date with API changes
- Monitor ReadTheDocs build status

## Getting Help

- Sphinx documentation: https://www.sphinx-doc.org/
- ReadTheDocs documentation: https://docs.readthedocs.io/
- Open an issue for documentation problems
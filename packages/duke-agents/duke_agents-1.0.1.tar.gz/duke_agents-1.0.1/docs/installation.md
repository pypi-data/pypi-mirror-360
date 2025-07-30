# Installation

This guide will help you install DUKE Agents and set up your environment.

## Requirements

- Python 3.8 or higher
- pip package manager
- Mistral API key

## Installing from PyPI

The easiest way to install DUKE Agents is from PyPI:

```bash
pip install duke-agents
```

## Installing from Source

To install the latest development version:

```bash
git clone https://github.com/elmasson/duke-agents.git
cd duke-agents
pip install -e .
```

## Installing with Development Dependencies

If you plan to contribute to DUKE Agents:

```bash
git clone https://github.com/elmasson/duke-agents.git
cd duke-agents
pip install -e ".[dev,docs]"
```

## Setting Up Your API Key

DUKE Agents requires a Mistral API key. You can obtain one from [console.mistral.ai](https://console.mistral.ai).

### Option 1: Environment Variable

```bash
export MISTRAL_API_KEY="your-api-key-here"
```

### Option 2: .env File

Create a `.env` file in your project root:

```env
MISTRAL_API_KEY=your-api-key-here
```

### Option 3: In Your Code

```python
import os
os.environ["MISTRAL_API_KEY"] = "your-api-key-here"
```

## Verifying Installation

To verify your installation:

```python
import duke_agents
print(duke_agents.__version__)

# Test basic functionality
from duke_agents import AtomicAgent, ContextManager, Orchestrator

context = ContextManager("Test installation")
orchestrator = Orchestrator(context)
agent = AtomicAgent("test_agent")

print("Installation successful!")
```

## Troubleshooting

### ImportError

If you get an import error, ensure duke-agents is installed:

```bash
pip show duke-agents
```

### API Key Error

If you get an API key error, verify your key is set:

```python
import os
print("API Key set:", "MISTRAL_API_KEY" in os.environ)
```

### Dependencies Issues

If you have dependency conflicts:

```bash
pip install --upgrade duke-agents
# or for a clean install
pip uninstall duke-agents
pip install duke-agents
```

## Next Steps

- Read the [Quick Start Guide](quickstart.md)
- Explore [Examples](examples.md)
- Learn about [Core Concepts](concepts.md)
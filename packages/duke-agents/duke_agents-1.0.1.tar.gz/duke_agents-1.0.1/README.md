# DUKE Agents

[![PyPI version](https://badge.fury.io/py/duke-agents.svg)](https://badge.fury.io/py/duke-agents)
[![Python Support](https://img.shields.io/pypi/pyversions/duke-agents.svg)](https://pypi.org/project/duke-agents/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-GitHub-blue.svg)](https://github.com/elmasson/duke-agents/tree/main/docs)
[![Downloads](https://pepy.tech/badge/duke-agents)](https://pepy.tech/project/duke-agents)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

DUKE Agents is an advanced AI agent framework implementing the IPO (Input-Process-Output) architecture with enriched memory and feedback loops. It provides autonomous agents powered by Mistral LLMs for complex task execution, enabling developers to build sophisticated AI-driven workflows with minimal effort.

## 🎯 Why DUKE Agents?

- **Production-Ready**: Built with enterprise-grade reliability and error handling
- **Memory-Enhanced**: Persistent memory across workflow steps enables context-aware processing
- **Self-Correcting**: Automatic retry with satisfaction scoring ensures quality outputs
- **Fully Typed**: Complete type annotations for better IDE support and fewer runtime errors
- **Extensible**: Easy to create custom agents and extend functionality
- **Secure**: Sandboxed code execution and configurable security policies

## 🚀 Features

### Core Capabilities

- **🏗️ IPO Architecture**: Structured Input-Process-Output workflow with memory persistence
- **🤖 Multiple Agent Types**: 
  - `AtomicAgent`: For discrete, well-defined tasks
  - `CodeActAgent`: For code generation and execution
  - Custom agents through simple inheritance
- **🧠 Mistral Integration**: Native support for all Mistral models including Codestral
- **💾 Memory Management**: Rich workflow memory with feedback loops and context propagation
- **🔄 Auto-correction**: Built-in retry logic with configurable satisfaction thresholds
- **🎭 Flexible Orchestration**: 
  - Linear workflows for predefined sequences
  - LLM-driven dynamic agent selection
- **✅ Type Safety**: Full Pydantic models for robust data validation

### Advanced Features

- **📊 Workflow Visualization**: Export workflows as diagrams
- **🔍 Debugging Tools**: Comprehensive logging and memory inspection
- **⚡ Async Support**: Asynchronous agent execution for better performance
- **🛡️ Security**: Sandboxed execution environment for generated code
- **📈 Metrics**: Built-in performance tracking and optimization hints
- **🔌 Extensible**: Plugin system for custom functionality

## 📦 Installation

### Standard Installation

```bash
pip install duke-agents
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/elmasson/duke-agents.git
cd duke-agents

# Install in development mode with all dependencies
pip install -e ".[dev,docs]"
```

### Prerequisites

- Python 3.8 or higher
- Mistral API key (get one at [console.mistral.ai](https://console.mistral.ai))

## 🔧 Quick Start

### 1. Set Up Your Environment

```python
import os
from duke_agents import ContextManager, Orchestrator

# Set your Mistral API key
os.environ["MISTRAL_API_KEY"] = "your-api-key"

# Or use a .env file
# MISTRAL_API_KEY=your-api-key
```

### 2. Basic Agent Usage

```python
from duke_agents import AtomicAgent, ContextManager, Orchestrator

# Initialize context manager
context = ContextManager("Process customer feedback")

# Create orchestrator
orchestrator = Orchestrator(context)

# Create and register an agent
agent = AtomicAgent("feedback_analyzer")
orchestrator.register_agent(agent)

# Define workflow
workflow = [{
    'agent': 'feedback_analyzer',
    'input_type': 'atomic',
    'input_data': {
        'task_id': 'analyze_001',
        'parameters': {
            'feedback': 'Great product but shipping was slow',
            'analyze': ['sentiment', 'topics', 'actionable_insights']
        }
    }
}]

# Execute workflow
results = orchestrator.execute_linear_workflow(workflow)

# Access results
if results[0].success:
    print(f"Analysis: {results[0].result}")
    print(f"Confidence: {results[0].satisfaction_score}")
```

### 3. Code Generation and Execution

```python
from duke_agents import CodeActAgent, ContextManager, Orchestrator

# Create a code generation agent
context = ContextManager("Data Analysis Assistant")
orchestrator = Orchestrator(context)

code_agent = CodeActAgent("data_analyst", model="codestral-latest")
orchestrator.register_agent(code_agent)

# Generate and execute code
workflow = [{
    'agent': 'data_analyst',
    'input_type': 'codeact',
    'input_data': {
        'prompt': '''Create a function that:
        1. Loads sales data from a CSV file
        2. Calculates total revenue by product category
        3. Identifies top 5 performing products
        4. Generates a summary report with visualizations''',
        'context_data': {
            'csv_path': 'sales_data.csv',
            'date_column': 'transaction_date'
        }
    }
}]

results = orchestrator.execute_linear_workflow(workflow)

if results[0].success:
    print(f"Generated Code:\n{results[0].generated_code}")
    print(f"\nExecution Output:\n{results[0].execution_result}")
```

### 4. Multi-Agent Workflows

```python
# Create multiple specialized agents
data_agent = AtomicAgent("data_processor")
analysis_agent = CodeActAgent("analyzer")
report_agent = AtomicAgent("report_generator")

# Register all agents
for agent in [data_agent, analysis_agent, report_agent]:
    orchestrator.register_agent(agent)

# Define multi-step workflow
workflow = [
    {
        'agent': 'data_processor',
        'input_type': 'atomic',
        'input_data': {
            'task_id': 'load_data',
            'parameters': {'source': 'database', 'table': 'sales_2024'}
        }
    },
    {
        'agent': 'analyzer',
        'input_type': 'codeact',
        'input_data': {
            'prompt': 'Analyze the sales data and identify trends, anomalies, and opportunities'
        }
    },
    {
        'agent': 'report_generator',
        'input_type': 'atomic',
        'input_data': {
            'task_id': 'create_report',
            'parameters': {'format': 'pdf', 'include_visuals': True}
        }
    }
]

# Execute the complete workflow
results = orchestrator.execute_linear_workflow(workflow)
```

### 5. Custom Agent Creation

```python
from duke_agents.agents import BaseAgent
from duke_agents.models import AtomicInput, AtomicOutput
from pydantic import BaseModel

class TranslationOutput(BaseModel):
    translated_text: str
    source_language: str
    target_language: str
    confidence: float

class TranslationAgent(BaseAgent):
    """Custom agent for language translation."""
    
    def __init__(self, name: str, model: str = "mistral-large"):
        super().__init__(name, model)
        self.agent_type = "translator"
    
    def process(self, input_data: AtomicInput, context_data: dict = None) -> TranslationOutput:
        # Custom processing logic
        prompt = f"""Translate the following text to {input_data.parameters.get('target_language', 'English')}:
        
        {input_data.parameters['text']}
        
        Also identify the source language."""
        
        response = self.llm_client.complete(prompt)
        
        # Parse response and create output
        return TranslationOutput(
            translated_text=response['translation'],
            source_language=response['source_language'],
            target_language=input_data.parameters['target_language'],
            confidence=0.95
        )

# Use the custom agent
translator = TranslationAgent("translator")
orchestrator.register_agent(translator)
```

## 📖 Advanced Usage

### Dynamic Workflow with LLM-Driven Orchestration

```python
# Let the LLM decide which agents to use
context = ContextManager("Solve user problem: analyze and visualize climate data")

# Register multiple specialized agents
agents = {
    'data_fetcher': AtomicAgent("data_fetcher"),
    'data_cleaner': AtomicAgent("data_cleaner"),
    'statistician': CodeActAgent("statistician"),
    'visualizer': CodeActAgent("visualizer"),
    'reporter': AtomicAgent("reporter")
}

for agent in agents.values():
    orchestrator.register_agent(agent)

# Execute LLM-driven workflow
results = orchestrator.execute_llm_driven_workflow(
    user_request="Fetch climate data for the last 10 years, clean it, perform statistical analysis, create visualizations, and generate a comprehensive report",
    max_steps=10
)
```

### Memory and Context Management

```python
# Access workflow memory
memory = context.memory

# Inspect memory records
for record in memory.agent_records:
    print(f"Agent: {record.agent_name}")
    print(f"Input: {record.input_summary}")
    print(f"Output: {record.output_summary}")
    print(f"Timestamp: {record.timestamp}")
    print("---")

# Add custom feedback
memory.add_feedback("visualization", "Excellent charts, very clear and informative", 0.95)

# Get memory summary for LLM context
summary = memory.get_summary()
```

### Configuration and Customization

```python
from duke_agents.config import DukeConfig

# Custom configuration
config = DukeConfig(
    mistral_api_key="your-key",
    default_model="mistral-large",
    temperature=0.7,
    max_retries=5,
    satisfaction_threshold=0.8,
    code_execution_timeout=60,  # seconds
    enable_sandboxing=True
)

# Create orchestrator with custom config
orchestrator = Orchestrator(context, config=config)
```

### Error Handling and Debugging

```python
# Enable detailed logging
import logging
logging.getLogger('duke_agents').setLevel(logging.DEBUG)

# Execute with error handling
try:
    results = orchestrator.execute_linear_workflow(workflow)
except Exception as e:
    # Access detailed error information
    print(f"Workflow failed: {e}")
    
    # Inspect partial results
    for i, record in enumerate(context.memory.agent_records):
        if record.error:
            print(f"Step {i} failed: {record.error}")

# Export workflow for debugging
orchestrator.export_workflow("debug_workflow.json")
```

## 🏗️ Architecture

### Component Overview

```
duke-agents/
├── agents/              # Agent implementations
│   ├── base_agent.py    # Abstract base class
│   ├── atomic_agent.py  # Simple task execution
│   └── codeact_agent.py # Code generation/execution
├── models/              # Data models
│   ├── atomic_models.py # Input/Output for AtomicAgent
│   ├── codeact_models.py # Input/Output for CodeActAgent
│   └── memory.py        # Memory management
├── orchestration/       # Workflow management
│   ├── context_manager.py # Context and memory
│   └── orchestrator.py    # Workflow execution
├── executors/           # Code execution
│   └── code_executor.py  # Safe code execution
├── llm/                 # LLM integration
│   └── mistral_client.py # Mistral API client
└── config.py            # Configuration
```

### Design Principles

1. **Separation of Concerns**: Each component has a single, well-defined responsibility
2. **Extensibility**: Easy to add new agent types and capabilities
3. **Type Safety**: Full type hints and runtime validation
4. **Memory-First**: All operations consider memory and context
5. **Fail-Safe**: Graceful error handling and recovery

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=duke_agents

# Run specific test file
pytest tests/test_agents.py

# Run with verbose output
pytest -v
```

## 📊 Performance Considerations

- **Concurrent Execution**: Agents can run in parallel when dependencies allow
- **Caching**: LLM responses are cached to reduce API calls
- **Memory Optimization**: Automatic memory pruning for long workflows
- **Batch Processing**: Support for processing multiple inputs efficiently

## 🔒 Security

- **Sandboxed Execution**: Code runs in isolated environments
- **Input Validation**: All inputs are validated before processing
- **API Key Protection**: Secure handling of sensitive credentials
- **Rate Limiting**: Built-in rate limiting for API calls
- **Audit Logging**: Complete audit trail of all operations

## 📚 Documentation

- **[Full Documentation](https://github.com/elmasson/duke-agents/tree/main/docs)**: Comprehensive guides and API reference (ReadTheDocs coming soon)
- **[Examples](https://github.com/elmasson/duke-agents/tree/main/examples)**: Ready-to-run example scripts
- **[API Reference](https://github.com/elmasson/duke-agents/tree/main/docs/api)**: Detailed API documentation
- **[Contributing Guide](CONTRIBUTING.md)**: How to contribute to the project

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Code style and standards
- Development setup
- Testing requirements
- Pull request process
- Issue reporting

## 📈 Roadmap

- [ ] **v1.1**: Async/await support throughout
- [ ] **v1.2**: Additional LLM providers (OpenAI, Anthropic)
- [ ] **v1.3**: Web UI for workflow design
- [ ] **v1.4**: Distributed agent execution
- [ ] **v2.0**: Agent marketplace and sharing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Mistral AI](https://mistral.ai) models
- Inspired by IPO (Input-Process-Output) architecture
- Thanks to all [contributors](https://github.com/elmasson/duke-agents/graphs/contributors)

## 📬 Support

- **Documentation**: [GitHub Docs](https://github.com/elmasson/duke-agents/tree/main/docs)
- **Issues**: [GitHub Issues](https://github.com/elmasson/duke-agents/issues)
- **Discussions**: [GitHub Discussions](https://github.com/elmasson/duke-agents/discussions)
- **Email**: smasson@duke-ai.io

---

Made with ❤️ by the DUKE Analytics team
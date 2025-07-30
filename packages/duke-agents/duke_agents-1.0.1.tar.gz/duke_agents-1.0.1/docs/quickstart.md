# Quick Start Guide

This guide will help you get started with DUKE Agents in minutes.

## Your First Agent

Let's create a simple agent that processes text:

```python
from duke_agents import AtomicAgent, ContextManager, Orchestrator
import os

# Set your API key
os.environ["MISTRAL_API_KEY"] = "your-api-key"

# Initialize the context manager
context = ContextManager("Text Processing Workflow")

# Create an orchestrator
orchestrator = Orchestrator(context)

# Create and register an agent
text_agent = AtomicAgent("text_processor")
orchestrator.register_agent(text_agent)

# Define a workflow
workflow = [{
    'agent': 'text_processor',
    'input_type': 'atomic',
    'input_data': {
        'task_id': 'summarize_001',
        'parameters': {
            'text': 'Your long text here...',
            'action': 'summarize'
        }
    }
}]

# Execute the workflow
results = orchestrator.execute_linear_workflow(workflow)

# Check results
if results[0].success:
    print(f"Summary: {results[0].result}")
```

## Code Generation Agent

Create an agent that generates and executes code:

```python
from duke_agents import CodeActAgent, ContextManager, Orchestrator

# Create a code generation agent
context = ContextManager("Code Generation")
orchestrator = Orchestrator(context)

code_agent = CodeActAgent("code_generator")
orchestrator.register_agent(code_agent)

# Generate code
workflow = [{
    'agent': 'code_generator',
    'input_type': 'codeact',
    'input_data': {
        'prompt': 'Create a function to calculate fibonacci numbers'
    }
}]

results = orchestrator.execute_linear_workflow(workflow)

if results[0].success:
    print(f"Generated Code:\n{results[0].generated_code}")
    print(f"Execution Result: {results[0].execution_result}")
```

## Multi-Agent Workflow

Chain multiple agents together:

```python
# Create multiple agents
analyzer = AtomicAgent("analyzer")
processor = CodeActAgent("processor")
reporter = AtomicAgent("reporter")

# Register all agents
for agent in [analyzer, processor, reporter]:
    orchestrator.register_agent(agent)

# Define multi-step workflow
workflow = [
    {
        'agent': 'analyzer',
        'input_type': 'atomic',
        'input_data': {
            'task_id': 'analyze_data',
            'parameters': {'data': 'raw_data.csv'}
        }
    },
    {
        'agent': 'processor',
        'input_type': 'codeact',
        'input_data': {
            'prompt': 'Process the analyzed data and create visualizations'
        }
    },
    {
        'agent': 'reporter',
        'input_type': 'atomic',
        'input_data': {
            'task_id': 'create_report',
            'parameters': {'format': 'pdf'}
        }
    }
]

# Execute the complete workflow
results = orchestrator.execute_linear_workflow(workflow)
```

## Accessing Memory

Inspect the workflow memory:

```python
# Access memory after workflow execution
memory = context.memory

# View all agent records
for record in memory.agent_records:
    print(f"Agent: {record.agent_name}")
    print(f"Input: {record.input_summary}")
    print(f"Output: {record.output_summary}")
    print(f"Success: {record.success}")
    print("---")

# Get memory summary
summary = memory.get_summary()
print(f"Memory Summary: {summary}")
```

## Error Handling

Handle errors gracefully:

```python
try:
    results = orchestrator.execute_linear_workflow(workflow)
    
    for i, result in enumerate(results):
        if not result.success:
            print(f"Step {i} failed: {result.error}")
        else:
            print(f"Step {i} succeeded")
            
except Exception as e:
    print(f"Workflow failed: {e}")
    # Access partial results from memory
    for record in context.memory.agent_records:
        if record.error:
            print(f"Error in {record.agent_name}: {record.error}")
```

## Configuration

Customize agent behavior:

```python
from duke_agents.config import DukeConfig

# Create custom configuration
config = DukeConfig(
    default_model="mistral-large",
    temperature=0.7,
    max_retries=3,
    satisfaction_threshold=0.8
)

# Use configuration
orchestrator = Orchestrator(context, config=config)
```

## Next Steps

- Explore [Advanced Examples](examples.md)
- Learn about [Custom Agents](agents.md)
- Understand [Memory Management](memory.md)
- Read about [Orchestration](orchestration.md)
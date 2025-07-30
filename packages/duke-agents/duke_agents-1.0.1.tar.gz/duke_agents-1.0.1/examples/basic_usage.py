"""Basic usage example for DUKE Agents."""
import os
from duke_agents import AtomicAgent, CodeActAgent, ContextManager, Orchestrator


def main():
    """Demonstrate basic DUKE Agents usage."""
    # Ensure API key is set
    if not os.getenv("MISTRAL_API_KEY"):
        print("Please set MISTRAL_API_KEY environment variable")
        return

    # Initialize context for the workflow
    context = ContextManager("Analyze customer feedback and generate insights")

    # Create orchestrator
    orchestrator = Orchestrator(context)

    # Create agents
    data_agent = AtomicAgent("data_processor")
    code_agent = CodeActAgent("insight_generator")

    # Register agents
    orchestrator.register_agent(data_agent)
    orchestrator.register_agent(code_agent)

    # Define workflow
    workflow = [
        {
            'agent': 'data_processor',
            'input_type': 'atomic',
            'input_data': {
                'task_id': 'load_feedback',
                'parameters': {
                    'source': 'customer_reviews.csv',
                    'filters': {'rating': '<3'}
                }
            }
        },
        {
            'agent': 'insight_generator',
            'input_type': 'codeact',
            'input_data': {
                'prompt': 'Generate code to analyze negative feedback patterns and create a summary report'
            }
        }
    ]

    # Execute workflow
    print("Executing workflow...")
    results = orchestrator.execute_linear_workflow(workflow)

    # Display results
    for i, result in enumerate(results):
        print(f"\nStep {i + 1} - Agent: {workflow[i]['agent']}")
        print(f"Success: {result.success}")
        print(f"Satisfaction Score: {result.satisfaction_score}")

        if result.success:
            if hasattr(result, 'generated_code'):
                print(f"Generated Code:\n{result.generated_code[:200]}...")
            else:
                print(f"Result: {result.result}")
        else:
            print(f"Error: {result.error}")


if __name__ == "__main__":
    main()
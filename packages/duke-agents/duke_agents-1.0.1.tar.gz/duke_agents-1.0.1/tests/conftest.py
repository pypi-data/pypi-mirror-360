"""Pytest configuration and fixtures for duke_agents tests."""

import pytest
import os
from unittest.mock import Mock


@pytest.fixture
def mock_mistral_api_key(monkeypatch):
    """Mock Mistral API key for tests."""
    monkeypatch.setenv("MISTRAL_API_KEY", "test-api-key-12345")
    
    
@pytest.fixture
def mock_config(monkeypatch):
    """Mock configuration values for tests."""
    monkeypatch.setenv("MISTRAL_API_KEY", "test-api-key")
    monkeypatch.setenv("DUKE_MAX_RETRIES", "3")
    monkeypatch.setenv("DUKE_SATISFACTION_THRESHOLD", "0.7")
    monkeypatch.setenv("DUKE_CODE_EXECUTION_TIMEOUT", "30")
    monkeypatch.setenv("DUKE_ENABLE_SANDBOXED_EXECUTION", "true")


@pytest.fixture
def mock_llm_client():
    """Mock MistralClient for tests."""
    client = Mock()
    client.generate.return_value = "Generated response"
    client.generate_code.return_value = "<execute>print('Hello')</execute>"
    return client


@pytest.fixture
def sample_workflow():
    """Sample workflow for testing."""
    return [
        {
            'agent': 'data_processor',
            'input_type': 'atomic',
            'input_data': {
                'task_id': 'task_001',
                'parameters': {'data': [1, 2, 3]}
            }
        },
        {
            'agent': 'code_generator',
            'input_type': 'codeact',
            'input_data': {
                'prompt': 'Generate analysis code'
            }
        }
    ]


@pytest.fixture(autouse=True)
def reset_agent_registry():
    """Reset the agent registry before each test."""
    from duke_agents.agents.utils import _agent_registry
    _agent_registry.clear()
    
    # Re-register default agents
    from duke_agents.agents import AtomicAgent, CodeActAgent
    from duke_agents.agents.utils import register_agent
    register_agent(AtomicAgent)
    register_agent(CodeActAgent)
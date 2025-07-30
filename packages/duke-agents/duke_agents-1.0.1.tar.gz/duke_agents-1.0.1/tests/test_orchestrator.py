"""Tests for duke_agents orchestration module."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from duke_agents.orchestration import ContextManager, Orchestrator
from duke_agents.agents import AtomicAgent, CodeActAgent
from duke_agents.models import AtomicOutput, CodeActOutput


class TestContextManager:
    """Test cases for ContextManager."""
    
    def test_context_manager_init(self):
        """Test ContextManager initialization."""
        cm = ContextManager("Test question")
        
        assert cm.workflow_memory.user_question == "Test question"
        assert cm.global_context == {}
        assert cm.agent_contexts == {}
    
    def test_get_memory(self):
        """Test getting workflow memory."""
        cm = ContextManager("Test")
        memory = cm.get_memory()
        
        assert memory.user_question == "Test"
        assert len(memory.records) == 0
    
    def test_update_global_context(self):
        """Test updating global context."""
        cm = ContextManager("Test")
        
        cm.update_global_context({"key1": "value1"})
        assert cm.global_context == {"key1": "value1"}
        
        cm.update_global_context({"key2": "value2"})
        assert cm.global_context == {"key1": "value1", "key2": "value2"}
    
    def test_get_agent_context(self):
        """Test getting agent-specific context."""
        cm = ContextManager("Test")
        
        # Set global context
        cm.update_global_context({"global_key": "global_value"})
        
        # Get context for new agent
        context = cm.get_agent_context("agent1")
        assert context == {"global_key": "global_value"}
        
        # Update agent-specific context
        cm.update_agent_context("agent1", {"agent_key": "agent_value"})
        
        # Get merged context
        context = cm.get_agent_context("agent1")
        assert context == {
            "global_key": "global_value",
            "agent_key": "agent_value"
        }
    
    def test_add_user_feedback(self):
        """Test adding user feedback."""
        cm = ContextManager("Test")
        
        cm.add_user_feedback("Great job!")
        assert cm.workflow_memory.user_feedback == "Great job!"
    
    def test_add_agent_feedback(self):
        """Test adding agent-specific feedback."""
        cm = ContextManager("Test")
        memory = cm.get_memory()
        
        # Add a memory record first
        from duke_agents.models import MemoryRecord
        record = MemoryRecord(
            agent_name="agent1",
            input_summary={},
            output_summary={}
        )
        memory.add_record(record)
        
        # Add feedback
        cm.add_agent_feedback("agent1", "Good work")
        assert memory.records[0].feedback == "Good work"
    
    def test_save_and_load_state(self, tmp_path):
        """Test saving and loading state."""
        # Create and populate context manager
        cm1 = ContextManager("Test question")
        cm1.update_global_context({"key": "value"})
        cm1.update_agent_context("agent1", {"agent_key": "agent_value"})
        cm1.add_user_feedback("Test feedback")
        
        # Save state
        filepath = tmp_path / "test_state.json"
        cm1.save_state(str(filepath))
        
        # Load state
        cm2 = ContextManager.load_state(str(filepath))
        
        # Verify loaded state
        assert cm2.workflow_memory.user_question == "Test question"
        assert cm2.workflow_memory.user_feedback == "Test feedback"
        assert cm2.global_context == {"key": "value"}
        assert cm2.agent_contexts == {"agent1": {"agent_key": "agent_value"}}


class TestOrchestrator:
    """Test cases for Orchestrator."""
    
    def test_orchestrator_init(self):
        """Test Orchestrator initialization."""
        cm = ContextManager("Test")
        
        with patch('duke_agents.orchestration.orchestrator.MistralClient'):
            orchestrator = Orchestrator(cm)
            
            assert orchestrator.context_manager == cm
            assert orchestrator.agents == {}
            assert hasattr(orchestrator, 'llm_client')
    
    def test_register_agent(self):
        """Test agent registration."""
        cm = ContextManager("Test")
        
        with patch('duke_agents.orchestration.orchestrator.MistralClient'):
            orchestrator = Orchestrator(cm)
            
            agent = AtomicAgent("test_agent")
            orchestrator.register_agent(agent)
            
            assert "test_agent" in orchestrator.agents
            assert orchestrator.agents["test_agent"] == agent
    
    @patch('duke_agents.orchestration.orchestrator.MistralClient')
    def test_execute_linear_workflow_atomic(self, mock_client_class):
        """Test linear workflow execution with AtomicAgent."""
        cm = ContextManager("Test")
        orchestrator = Orchestrator(cm)
        
        # Create and register mock agent
        agent = Mock(spec=AtomicAgent)
        agent.name = "test_agent"
        agent.run.return_value = AtomicOutput(
            success=True,
            result="Test result",
            satisfaction_score=0.9,
            memory=cm.get_memory()
        )
        orchestrator.register_agent(agent)
        
        # Define workflow
        workflow = [{
            'agent': 'test_agent',
            'input_type': 'atomic',
            'input_data': {
                'task_id': 'task_001',
                'parameters': {'key': 'value'}
            }
        }]
        
        # Execute workflow
        results = orchestrator.execute_linear_workflow(workflow)
        
        # Assertions
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].result == "Test result"
        agent.run.assert_called_once()
    
    @patch('duke_agents.orchestration.orchestrator.MistralClient')
    def test_execute_linear_workflow_codeact(self, mock_client_class):
        """Test linear workflow execution with CodeActAgent."""
        cm = ContextManager("Test")
        orchestrator = Orchestrator(cm)
        
        # Create and register mock agent
        agent = Mock(spec=CodeActAgent)
        agent.name = "code_agent"
        agent.run.return_value = CodeActOutput(
            success=True,
            generated_code="print('Hello')",
            execution_result="Hello",
            satisfaction_score=0.9,
            memory=cm.get_memory()
        )
        orchestrator.register_agent(agent)
        
        # Define workflow
        workflow = [{
            'agent': 'code_agent',
            'input_type': 'codeact',
            'input_data': {
                'prompt': 'Generate hello world'
            }
        }]
        
        # Execute workflow
        results = orchestrator.execute_linear_workflow(workflow)
        
        # Assertions
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].generated_code == "print('Hello')"
        agent.run.assert_called_once()
    
    @patch('duke_agents.orchestration.orchestrator.MistralClient')
    def test_execute_linear_workflow_with_failure(self, mock_client_class):
        """Test linear workflow with agent failure."""
        cm = ContextManager("Test")
        orchestrator = Orchestrator(cm)
        
        # Create agents - one fails, one should not be called
        agent1 = Mock(spec=AtomicAgent)
        agent1.name = "agent1"
        agent1.run.return_value = AtomicOutput(
            success=False,
            result=None,
            error="Test error",
            satisfaction_score=0.0,
            memory=cm.get_memory()
        )
        
        agent2 = Mock(spec=AtomicAgent)
        agent2.name = "agent2"
        
        orchestrator.register_agent(agent1)
        orchestrator.register_agent(agent2)
        
        # Define workflow without continue_on_failure
        workflow = [
            {
                'agent': 'agent1',
                'input_type': 'atomic',
                'input_data': {'task_id': 'task1', 'parameters': {}}
            },
            {
                'agent': 'agent2',
                'input_type': 'atomic',
                'input_data': {'task_id': 'task2', 'parameters': {}}
            }
        ]
        
        # Execute workflow
        results = orchestrator.execute_linear_workflow(workflow)
        
        # Only first agent should have been called
        assert len(results) == 1
        assert results[0].success is False
        agent1.run.assert_called_once()
        agent2.run.assert_not_called()
    
    @patch('duke_agents.orchestration.orchestrator.MistralClient')
    def test_execute_llm_driven_workflow(self, mock_client_class):
        """Test LLM-driven workflow execution."""
        # Setup mock LLM client
        mock_llm = Mock()
        mock_client_class.return_value = mock_llm
        
        # First call returns an action, second call returns complete
        mock_llm.generate.side_effect = [
            '{"action": "execute", "agent": "test_agent", "parameters": {"key": "value"}, "reasoning": "test"}',
            '{"action": "complete", "reasoning": "done"}'
        ]
        
        cm = ContextManager("Test")
        orchestrator = Orchestrator(cm)
        
        # Register mock agent
        agent = Mock(spec=AtomicAgent)
        agent.name = "test_agent"
        agent.run.return_value = AtomicOutput(
            success=True,
            result="Test result",
            satisfaction_score=0.9,
            memory=cm.get_memory()
        )
        orchestrator.register_agent(agent)
        
        # Execute LLM-driven workflow
        results = orchestrator.execute_llm_driven_workflow(max_steps=5)
        
        # Assertions
        assert len(results) == 1
        assert results[0].success is True
        assert mock_llm.generate.call_count == 2
        agent.run.assert_called_once()
    
    def test_execute_workflow_unregistered_agent(self):
        """Test workflow execution with unregistered agent."""
        cm = ContextManager("Test")
        
        with patch('duke_agents.orchestration.orchestrator.MistralClient'):
            orchestrator = Orchestrator(cm)
            
            workflow = [{
                'agent': 'nonexistent_agent',
                'input_type': 'atomic',
                'input_data': {'task_id': 'task1', 'parameters': {}}
            }]
            
            with pytest.raises(ValueError, match="Agent 'nonexistent_agent' not registered"):
                orchestrator.execute_linear_workflow(workflow)


if __name__ == "__main__":
    pytest.main([__file__])
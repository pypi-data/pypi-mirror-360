"""Tests for duke_agents agents module."""

import pytest
from unittest.mock import Mock, patch
from duke_agents.agents import AtomicAgent, CodeActAgent, BaseAgent
from duke_agents.models import AtomicInput, AtomicOutput, CodeActInput, CodeActOutput, WorkflowMemory


class TestAtomicAgent:
    """Test cases for AtomicAgent."""
    
    def test_atomic_agent_init(self):
        """Test AtomicAgent initialization."""
        agent = AtomicAgent(name="test_agent", max_retries=5, satisfaction_threshold=0.8)
        
        assert agent.name == "test_agent"
        assert agent.max_retries == 5
        assert agent.satisfaction_threshold == 0.8
    
    def test_atomic_agent_default_process(self):
        """Test default process method."""
        agent = AtomicAgent()
        memory = WorkflowMemory(user_question="test")
        
        input_data = AtomicInput(
            task_id="test_task",
            parameters={"key": "value"},
            context={},
            memory=memory
        )
        
        result = agent.process(input_data)
        
        assert isinstance(result, str)
        assert "test_task" in result
        assert "{'key': 'value'}" in result
    
    def test_atomic_agent_run_success(self):
        """Test successful agent run."""
        agent = AtomicAgent()
        memory = WorkflowMemory(user_question="test")
        
        input_data = AtomicInput(
            task_id="test_task",
            parameters={"action": "test"},
            context={},
            memory=memory
        )
        
        # Mock process and evaluate_satisfaction
        with patch.object(agent, 'process', return_value="Success result"):
            with patch.object(agent, 'evaluate_satisfaction', return_value=0.9):
                result = agent.run(input_data)
        
        assert result.success is True
        assert result.result == "Success result"
        assert result.satisfaction_score == 0.9
        assert result.error is None
        assert len(result.memory.records) == 1
    
    def test_atomic_agent_run_low_satisfaction(self):
        """Test agent run with low satisfaction score."""
        agent = AtomicAgent(satisfaction_threshold=0.8)
        memory = WorkflowMemory(user_question="test")
        
        input_data = AtomicInput(
            task_id="test_task",
            parameters={"action": "test"},
            context={},
            memory=memory
        )
        
        # Mock process with low satisfaction
        with patch.object(agent, 'process', return_value="Poor result"):
            with patch.object(agent, 'evaluate_satisfaction', return_value=0.3):
                result = agent.run(input_data)
        
        assert result.success is False
        assert result.satisfaction_score == 0.0
        assert "Failed after" in result.error
        assert "Satisfaction score too low" in result.error
    
    def test_atomic_agent_run_with_exception(self):
        """Test agent run with exception."""
        agent = AtomicAgent(max_retries=2)
        memory = WorkflowMemory(user_question="test")
        
        input_data = AtomicInput(
            task_id="test_task",
            parameters={"action": "test"},
            context={},
            memory=memory
        )
        
        # Mock process to raise exception
        with patch.object(agent, 'process', side_effect=ValueError("Test error")):
            result = agent.run(input_data)
        
        assert result.success is False
        assert result.satisfaction_score == 0.0
        assert "ValueError: Test error" in result.error
        assert result.debug_info["attempts"] == 2
    
    def test_evaluate_satisfaction_default(self):
        """Test default satisfaction evaluation."""
        agent = AtomicAgent()
        memory = WorkflowMemory(user_question="test")
        
        input_data = AtomicInput(
            task_id="test",
            parameters={},
            context={},
            memory=memory
        )
        
        # Test with None result
        assert agent.evaluate_satisfaction(None, input_data) == 0.0
        
        # Test with error in result
        assert agent.evaluate_satisfaction("Error occurred", input_data) == 0.3
        
        # Test with normal result
        assert agent.evaluate_satisfaction("Success", input_data) == 0.8


class TestCodeActAgent:
    """Test cases for CodeActAgent."""
    
    def test_codeact_agent_init(self):
        """Test CodeActAgent initialization."""
        with patch('duke_agents.agents.codeact_agent.MistralClient'):
            with patch('duke_agents.agents.codeact_agent.CodeExecutor'):
                agent = CodeActAgent(name="code_agent")
                
                assert agent.name == "code_agent"
                assert hasattr(agent, 'llm_client')
                assert hasattr(agent, 'code_executor')
    
    def test_codeact_agent_prepare_prompt(self):
        """Test prompt preparation."""
        with patch('duke_agents.agents.codeact_agent.MistralClient'):
            with patch('duke_agents.agents.codeact_agent.CodeExecutor'):
                agent = CodeActAgent()
                
                memory = WorkflowMemory(user_question="test question")
                context = {"var": "value"}
                
                prompt = agent._prepare_prompt(
                    "Generate code",
                    context,
                    memory,
                    "Previous error",
                    1
                )
                
                assert "Memory Context:" in prompt
                assert "test question" in prompt
                assert "Current Task: Generate code" in prompt
                assert "Data Context:" in prompt
                assert "var: value" in prompt
                assert "Previous attempt failed" in prompt
                assert "This is attempt 2" in prompt
    
    @patch('duke_agents.agents.codeact_agent.MistralClient')
    @patch('duke_agents.agents.codeact_agent.CodeExecutor')
    @patch('duke_agents.agents.codeact_agent.extract_code_block')
    def test_codeact_agent_run_success(self, mock_extract, mock_executor_class, mock_client_class):
        """Test successful code generation and execution."""
        # Setup mocks
        mock_llm = Mock()
        mock_llm.generate_code.return_value = "<execute>print('Hello')</execute>"
        mock_llm.generate.return_value = "satisfaction_score: 0.9\nreason: Good code"
        mock_client_class.return_value = mock_llm
        
        mock_executor = Mock()
        mock_executor.execute.return_value = ("Hello", "Hello", True)
        mock_executor_class.return_value = mock_executor
        
        mock_extract.return_value = "print('Hello')"
        
        # Create agent and input
        agent = CodeActAgent()
        memory = WorkflowMemory(user_question="test")
        
        input_data = CodeActInput(
            prompt="Generate hello world",
            data_context={},
            memory=memory
        )
        
        # Run agent
        result = agent.run(input_data)
        
        # Assertions
        assert result.success is True
        assert result.generated_code == "print('Hello')"
        assert result.execution_result == "Hello"
        assert result.satisfaction_score >= 0.7
        assert len(result.memory.records) == 1
    
    def test_process_not_implemented(self):
        """Test that process method raises NotImplementedError."""
        with patch('duke_agents.agents.codeact_agent.MistralClient'):
            with patch('duke_agents.agents.codeact_agent.CodeExecutor'):
                agent = CodeActAgent()
                
                with pytest.raises(NotImplementedError):
                    agent.process()


class TestBaseAgent:
    """Test cases for BaseAgent."""
    
    def test_create_memory_record(self):
        """Test memory record creation."""
        # Create a concrete implementation
        class ConcreteAgent(BaseAgent):
            def process(self, *args, **kwargs):
                return "result"
            
            def evaluate_satisfaction(self, result, *args, **kwargs):
                return 0.8
        
        agent = ConcreteAgent(name="test_agent")
        
        input_data = {
            "task_id": "123",
            "parameters": {"key": "value"},
            "memory": "should_be_excluded",
            "long_text": "a" * 200
        }
        
        output_data = {
            "result": "success",
            "score": 0.9,
            "debug_info": "should_be_excluded",
            "long_output": "b" * 200
        }
        
        record = agent.create_memory_record(input_data, output_data)
        
        assert record.agent_name == "test_agent"
        assert record.input_summary["task_id"] == "123"
        assert record.input_summary["parameters"] == {"key": "value"}
        assert "memory" not in record.input_summary
        assert len(record.input_summary["long_text"]) == 100
        
        assert record.output_summary["result"] == "success"
        assert record.output_summary["score"] == 0.9
        assert "debug_info" not in record.output_summary
        assert len(record.output_summary["long_output"]) == 100


if __name__ == "__main__":
    pytest.main([__file__])
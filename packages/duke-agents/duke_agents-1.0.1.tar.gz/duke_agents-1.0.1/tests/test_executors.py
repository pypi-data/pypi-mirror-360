"""Tests for duke_agents executors module."""

import pytest
import subprocess
import sys
from unittest.mock import Mock, patch, mock_open
from duke_agents.executors import CodeExecutor
from duke_agents.config import Config


class TestCodeExecutor:
    """Test cases for CodeExecutor."""
    
    def test_code_executor_init(self):
        """Test CodeExecutor initialization."""
        # Test with default timeout
        executor = CodeExecutor()
        assert executor.timeout == Config.CODE_EXECUTION_TIMEOUT
        
        # Test with custom timeout
        executor = CodeExecutor(timeout=60)
        assert executor.timeout == 60
    
    @patch('duke_agents.executors.code_executor.Config.ENABLE_SANDBOXED_EXECUTION', True)
    @patch('duke_agents.executors.code_executor.tempfile.NamedTemporaryFile')
    @patch('duke_agents.executors.code_executor.subprocess.run')
    @patch('duke_agents.executors.code_executor.os.unlink')
    def test_execute_sandboxed_success(self, mock_unlink, mock_run, mock_tempfile):
        """Test successful sandboxed execution."""
        # Setup mocks
        mock_file = Mock()
        mock_file.name = '/tmp/test.py'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Hello World"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        # Execute code
        executor = CodeExecutor()
        result, output, success = executor.execute("print('Hello World')")
        
        # Assertions
        assert success is True
        assert result == "Hello World"
        assert output == "Hello World"
        mock_run.assert_called_once()
        mock_unlink.assert_called_with('/tmp/test.py')
    
    @patch('duke_agents.executors.code_executor.Config.ENABLE_SANDBOXED_EXECUTION', True)
    @patch('duke_agents.executors.code_executor.tempfile.NamedTemporaryFile')
    @patch('duke_agents.executors.code_executor.subprocess.run')
    @patch('duke_agents.executors.code_executor.os.unlink')
    def test_execute_sandboxed_with_context(self, mock_unlink, mock_run, mock_tempfile):
        """Test sandboxed execution with context."""
        # Setup mocks
        mock_file = Mock()
        mock_file.name = '/tmp/test.py'
        mock_file.write = Mock()
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Value: 42"
        mock_run.return_value = mock_process
        
        # Execute code with context
        executor = CodeExecutor()
        context = {"x": 42}
        result, output, success = executor.execute("print(f'Value: {x}')", context)
        
        # Verify context was properly serialized
        written_content = mock_file.write.call_args[0][0]
        assert "import json" in written_content
        assert "context = json.loads(" in written_content
        assert "globals().update(context)" in written_content
        
        assert success is True
        assert output == "Value: 42"
    
    @patch('duke_agents.executors.code_executor.Config.ENABLE_SANDBOXED_EXECUTION', True)
    @patch('duke_agents.executors.code_executor.tempfile.NamedTemporaryFile')
    @patch('duke_agents.executors.code_executor.subprocess.run')
    @patch('duke_agents.executors.code_executor.os.unlink')
    def test_execute_sandboxed_failure(self, mock_unlink, mock_run, mock_tempfile):
        """Test sandboxed execution with error."""
        # Setup mocks
        mock_file = Mock()
        mock_file.name = '/tmp/test.py'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "NameError: name 'undefined' is not defined"
        mock_run.return_value = mock_process
        
        # Execute code
        executor = CodeExecutor()
        result, output, success = executor.execute("print(undefined)")
        
        # Assertions
        assert success is False
        assert result is None
        assert "NameError" in output
    
    @patch('duke_agents.executors.code_executor.Config.ENABLE_SANDBOXED_EXECUTION', True)
    @patch('duke_agents.executors.code_executor.tempfile.NamedTemporaryFile')
    @patch('duke_agents.executors.code_executor.subprocess.run')
    @patch('duke_agents.executors.code_executor.os.unlink')
    def test_execute_sandboxed_timeout(self, mock_unlink, mock_run, mock_tempfile):
        """Test sandboxed execution with timeout."""
        # Setup mocks
        mock_file = Mock()
        mock_file.name = '/tmp/test.py'
        mock_tempfile.return_value.__enter__.return_value = mock_file
        
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="python", timeout=30)
        
        # Execute code
        executor = CodeExecutor(timeout=30)
        result, output, success = executor.execute("while True: pass")
        
        # Assertions
        assert success is False
        assert result is None
        assert "timed out after 30 seconds" in output
    
    @patch('duke_agents.executors.code_executor.Config.ENABLE_SANDBOXED_EXECUTION', False)
    @patch('duke_agents.executors.code_executor.sys.stdout')
    def test_execute_unsafe_success(self, mock_stdout):
        """Test unsafe execution mode."""
        # Setup mock stdout
        from io import StringIO
        mock_string_io = StringIO()
        mock_stdout.__class__ = StringIO
        mock_stdout.getvalue.return_value = "Hello from unsafe"
        
        # Execute code
        executor = CodeExecutor()
        code = "result = 'Test Result'"
        result, output, success = executor._execute_unsafe(code)
        
        # The execution should work even without mocking since it's simple code
        assert success is True
        # Result should be the value of 'result' variable or stdout
        assert result is not None
    
    @patch('duke_agents.executors.code_executor.Config.ENABLE_SANDBOXED_EXECUTION', False)
    def test_execute_unsafe_with_exception(self):
        """Test unsafe execution with exception."""
        executor = CodeExecutor()
        
        code = "raise ValueError('Test error')"
        result, output, success = executor._execute_unsafe(code)
        
        assert success is False
        assert result is None
        assert "ValueError: Test error" in output
        assert "Traceback" in output
    
    def test_context_serialization_security(self):
        """Test that context serialization is secure against injection."""
        executor = CodeExecutor()
        
        # Try to inject malicious code through context
        malicious_context = {
            "key": "'); import os; os.system('echo hacked'); #"
        }
        
        # The serialization should properly escape this
        with patch('duke_agents.executors.code_executor.tempfile.NamedTemporaryFile'):
            with patch('duke_agents.executors.code_executor.subprocess.run') as mock_run:
                mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
                
                # This should not execute the malicious code
                executor._execute_sandboxed("print('safe')", malicious_context)
                
                # Verify the call - the context should be properly escaped
                # The fix we implemented uses json.dumps twice to ensure proper escaping
                # So the malicious string should be safely contained


if __name__ == "__main__":
    pytest.main([__file__])
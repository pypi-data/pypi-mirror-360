"""Tests for the A2ARegisterTool class."""

import pytest
from unittest.mock import Mock
from uagent_a2a_adapter import A2ARegisterTool


class TestA2ARegisterTool:
    """Test cases for A2ARegisterTool."""
    
    def test_register_tool_invoke_with_defaults(self):
        """Test A2ARegisterTool invoke with default parameters."""
        mock_executor = Mock()
        tool = A2ARegisterTool()
        
        params = {
            "agent_executor": mock_executor,
            "name": "test_agent",
            "return_dict": True
        }
        
        result = tool.invoke(params)
        
        assert isinstance(result, dict)
        assert result["agent_name"] == "test_agent"
        assert result["agent_port"] == 8000
        assert result["a2a_port"] == 9999
        assert result["description"] == "A2A Agent: test_agent"
        assert result["mailbox_enabled"] is True
    
    def test_register_tool_invoke_with_custom_params(self):
        """Test A2ARegisterTool invoke with custom parameters."""
        mock_executor = Mock()
        tool = A2ARegisterTool()
        
        params = {
            "agent_executor": mock_executor,
            "name": "custom_agent",
            "description": "Custom description",
            "port": 8002,
            "a2a_port": 9002,
            "mailbox": False,
            "seed": "custom_seed",
            "return_dict": True
        }
        
        result = tool.invoke(params)
        
        assert result["agent_name"] == "custom_agent"
        assert result["description"] == "Custom description"
        assert result["agent_port"] == 8002
        assert result["a2a_port"] == 9002
        assert result["mailbox_enabled"] is False
    
    def test_register_tool_invoke_string_return(self):
        """Test A2ARegisterTool invoke returning string."""
        mock_executor = Mock()
        tool = A2ARegisterTool()
        
        params = {
            "agent_executor": mock_executor,
            "name": "string_agent",
            "return_dict": False
        }
        
        result = tool.invoke(params)
        
        assert isinstance(result, str)
        assert "Created A2A uAgent 'string_agent'" in result

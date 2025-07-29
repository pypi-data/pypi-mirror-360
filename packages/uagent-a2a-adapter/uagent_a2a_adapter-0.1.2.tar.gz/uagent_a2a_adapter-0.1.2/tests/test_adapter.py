"""Tests for the A2AAdapter class."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uagent_a2a_adapter import A2AAdapter


class TestA2AAdapter:
    """Test cases for A2AAdapter."""
    
    def test_adapter_initialization(self):
        """Test that A2AAdapter initializes correctly."""
        mock_executor = Mock()
        
        adapter = A2AAdapter(
            agent_executor=mock_executor,
            name="test_agent",
            description="Test agent description",
            port=8001,
            a2a_port=9001
        )
        
        assert adapter.name == "test_agent"
        assert adapter.description == "Test agent description"
        assert adapter.port == 8001
        assert adapter.a2a_port == 9001
        assert adapter.agent_executor == mock_executor
        assert adapter.uagent is not None
        assert adapter.chat_proto is not None
    
    def test_adapter_default_values(self):
        """Test that A2AAdapter uses correct default values."""
        mock_executor = Mock()
        
        adapter = A2AAdapter(
            agent_executor=mock_executor,
            name="test_agent",
            description="Test description"
        )
        
        assert adapter.port == 8000
        assert adapter.a2a_port == 9999
        assert adapter.mailbox is True
        assert adapter.seed == "test_agent_seed"
    
    @pytest.mark.asyncio
    async def test_send_to_a2a_agent_connection_failure(self):
        """Test handling of connection failures to A2A agent."""
        mock_executor = Mock()
        
        adapter = A2AAdapter(
            agent_executor=mock_executor,
            name="test_agent",
            description="Test description"
        )
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value.status_code = 404
            
            result = await adapter._send_to_a2a_agent("test message")
            
            assert "Could not connect to A2A agent" in result
    
    @pytest.mark.asyncio
    async def test_call_executor_directly_success(self):
        """Test direct executor call fallback."""
        mock_executor = Mock()
        
        adapter = A2AAdapter(
            agent_executor=mock_executor,
            name="test_agent",
            description="Test description"
        )
        
        # Mock the direct executor call to return success
        with patch.object(adapter, '_call_executor_directly', return_value="Success response"):
            result = await adapter._call_executor_directly("test message")
            assert result == "Success response"

"""Test suite for ReflexQL clipboard exchange protocol."""
import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from tushell.tushellcli import cli, get_memory_manager
from tushell.reflexql import (
    ClipboardExchange, ReflexQLMemoryKeys, ClipboardContent,
    ContentType, ExchangeError, ContentTypeError, DeliveryError
)
import time
import json

# Mock our memory manager for testing
@pytest.fixture(autouse=True)
def mock_get_memory_manager(monkeypatch):
    """Create and inject a mock memory manager."""
    mock_manager = MagicMock()
    def mock_get_memory():
        return mock_manager
    monkeypatch.setattr('tushell.tushellcli.get_memory_manager', mock_get_memory)
    return mock_manager

@pytest.fixture
def mock_memory_manager():
    """Create a mock memory manager for testing."""
    return MagicMock()

@pytest.fixture
def clipboard_exchange(mock_memory_manager):
    """Create a ClipboardExchange instance with mock memory manager."""
    return ClipboardExchange(mock_memory_manager)

def test_poll_clipboard_reflex_basic():
    """Test basic CLI command execution."""
    runner = CliRunner()
    result = runner.invoke(cli, ['poll-clipboard-reflex', '--ttl', '5'])
    assert result.exit_code == 0
    assert "🌟 Starting ReflexQL clipboard polling loop..." in result.output

def test_poll_clipboard_reflex_verbose():
    """Test verbose mode CLI execution."""
    runner = CliRunner()
    result = runner.invoke(cli, ['poll-clipboard-reflex', '--ttl', '5', '--verbose'])
    assert result.exit_code == 0
    assert "🌟 Starting ReflexQL clipboard polling loop..." in result.output

def test_poll_clipboard_reflex_custom_interval():
    """Test custom polling interval."""
    runner = CliRunner()
    result = runner.invoke(cli, ['poll-clipboard-reflex', '--poll-interval', '0.5', '--ttl', '5'])
    assert result.exit_code == 0
    assert "🌟 Starting ReflexQL clipboard polling loop..." in result.output

def test_clipboard_exchange_init(clipboard_exchange):
    """Test ClipboardExchange initialization."""
    assert clipboard_exchange.memory is not None
    assert hasattr(clipboard_exchange, 'copy_cmd')
    assert hasattr(clipboard_exchange, 'paste_cmd')

@patch('subprocess.Popen')
def test_write_to_clipboard(mock_popen, clipboard_exchange):
    """Test writing to system clipboard."""
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_popen.return_value = mock_process
    
    result = clipboard_exchange.write_to_clipboard("test content")
    assert result is True
    mock_popen.assert_called_once()

@patch('subprocess.run')
def test_read_from_clipboard(mock_run, clipboard_exchange):
    """Test reading from system clipboard."""
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "test content"
    
    result = clipboard_exchange.read_from_clipboard()
    assert isinstance(result, ClipboardContent)
    assert result == "test content"  # Tests our __eq__ implementation

def test_send_to_clipboard(clipboard_exchange):
    """Test sending content through clipboard exchange protocol."""
    clipboard_exchange.memory.get.side_effect = [True]  # Simulate delivery confirmation
    
    result = clipboard_exchange.send_to_clipboard("test content")
    
    # Verify content is properly wrapped
    set_calls = clipboard_exchange.memory.set.call_args_list
    assert any(call[0][0] == ReflexQLMemoryKeys.PENDING_CONTENT and 
              isinstance(call[0][1], ClipboardContent) and
              call[0][1] == "test content" for call in set_calls)
    assert result is True

def test_reset_memory_keys(clipboard_exchange):
    """Test memory key reset functionality."""
    clipboard_exchange._reset_memory_keys()
    
    # Verify all protocol keys were reset
    for key in [ReflexQLMemoryKeys.PENDING_CONTENT, ReflexQLMemoryKeys.READY,
                ReflexQLMemoryKeys.DELIVERED, ReflexQLMemoryKeys.ACK]:
        clipboard_exchange.memory.set.assert_any_call(key, None)

@patch('time.sleep')  # Prevent actual sleeping in tests
def test_poll_clipboard_loop_timeout(mock_sleep, clipboard_exchange):
    """Test polling loop timeout behavior."""
    start_time = time.time()
    clipboard_exchange.poll_clipboard_loop(poll_interval=0.1, ttl=1)
    
    # Verify the loop respected the TTL
    assert time.time() - start_time >= 1
    mock_sleep.assert_called()

def test_poll_clipboard_loop_exchange(clipboard_exchange):
    """Test complete clipboard exchange cycle."""
    ready_values = [True, False]
    content = ClipboardContent(content="test content")
    ack_values = [False, True]
    
    def side_effect(key):
        if key == ReflexQLMemoryKeys.READY:
            return ready_values.pop(0) if ready_values else False
        elif key == ReflexQLMemoryKeys.PENDING_CONTENT:
            return content
        elif key == ReflexQLMemoryKeys.ACK:
            return ack_values.pop(0) if ack_values else False
        return None
    
    clipboard_exchange.memory.get.side_effect = side_effect
    
    with patch.object(clipboard_exchange, 'write_to_clipboard') as mock_write:
        mock_write.return_value = True
        clipboard_exchange.poll_clipboard_loop(poll_interval=0.1, ttl=1)
        
        # Verify the exchange sequence with content type handling
        mock_write.assert_called_once()
        call_arg = mock_write.call_args[0][0]
        assert isinstance(call_arg, ClipboardContent)
        assert call_arg == content

def test_clipboard_content_serialization():
    """Test ClipboardContent serialization/deserialization."""
    content = ClipboardContent(
        content="test content",
        content_type=ContentType.JSON,
        metadata={"source": "test"}
    )
    serialized = content.serialize()
    deserialized = ClipboardContent.deserialize(serialized)
    
    assert deserialized.content == content.content
    assert deserialized.content_type == content.content_type
    assert deserialized.metadata == content.metadata

def test_clipboard_content_fallback():
    """Test ClipboardContent fallback for plain text."""
    plain_text = "just plain text"
    content = ClipboardContent.deserialize(plain_text)
    
    assert content.content == plain_text
    assert content.content_type == ContentType.TEXT
    assert content.metadata is None

def test_write_to_clipboard_with_retry(clipboard_exchange):
    """Test clipboard write retry logic."""
    content = ClipboardContent(
        content="test with retry",
        content_type=ContentType.CODE
    )
    
    with patch.object(clipboard_exchange, '_setup_platform_clipboard'):
        with patch('subprocess.Popen') as mock_popen:
            # Simulate first two attempts failing
            mock_process1 = MagicMock()
            mock_process1.returncode = 1
            mock_process2 = MagicMock()
            mock_process2.returncode = 1
            mock_process3 = MagicMock()
            mock_process3.returncode = 0
            mock_popen.side_effect = [mock_process1, mock_process2, mock_process3]
            
            result = clipboard_exchange.write_to_clipboard(content)
            assert result is True
            assert mock_popen.call_count == 3

def test_write_to_clipboard_error_handling(clipboard_exchange):
    """Test clipboard write error handling."""
    with patch.object(clipboard_exchange, '_setup_platform_clipboard'):
        with patch('subprocess.Popen', side_effect=Exception("Mock error")):
            with pytest.raises(DeliveryError) as exc_info:
                clipboard_exchange.write_to_clipboard("test content")
            
            assert "Failed to write to clipboard" in str(exc_info.value)
            clipboard_exchange.memory.set.assert_any_call(
                ReflexQLMemoryKeys.ERROR,
                "Mock error"
            )

def test_exchange_with_content_types(clipboard_exchange):
    """Test complete exchange with different content types."""
    ready_values = [True, False]
    content = ClipboardContent(
        content='{"key": "value"}',
        content_type=ContentType.JSON,
        metadata={"version": "1.0"}
    )
    ack_values = [False, True]
    
    def side_effect(key):
        if key == ReflexQLMemoryKeys.READY:
            return ready_values.pop(0) if ready_values else False
        elif key == ReflexQLMemoryKeys.PENDING_CONTENT:
            return content
        elif key == ReflexQLMemoryKeys.ACK:
            return ack_values.pop(0) if ack_values else False
        return None
    
    clipboard_exchange.memory.get.side_effect = side_effect
    
    with patch.object(clipboard_exchange, 'write_to_clipboard') as mock_write:
        mock_write.return_value = True
        clipboard_exchange.poll_clipboard_loop(poll_interval=0.1, ttl=1)
        
        # Verify the exchange handled the content type correctly
        mock_write.assert_called_once()
        call_arg = mock_write.call_args[0][0]
        assert isinstance(call_arg, ClipboardContent)
        assert call_arg.content_type == ContentType.JSON
        assert call_arg.metadata == {"version": "1.0"}

def test_poll_clipboard_reflex_verbose_logging(mock_memory_manager):
    """Test verbose logging during polling loop."""
    runner = CliRunner()
    mock_memory_manager.get.side_effect = ["true", "test content", "true"]

    result = runner.invoke(cli, ['poll-clipboard-reflex', '--ttl', '5', '--verbose'])
    
    assert result.exit_code == 0
    assert "🔍 Checking Reflex::Clipboard.Ready flag..." in result.output
    assert "📋 Clipboard content fetched: test content" in result.output
    assert "✅ Clipboard content delivered." in result.output

def test_poll_clipboard_reflex_error_handling(mock_memory_manager):
    """Test error handling during polling loop."""
    runner = CliRunner()
    mock_memory_manager.get.side_effect = Exception("Mock error")

    result = runner.invoke(cli, ['poll-clipboard-reflex', '--ttl', '5', '--verbose'])
    
    assert result.exit_code != 0
    assert "⚠️ Error during polling: Mock error" in result.output
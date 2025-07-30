"""
ReflexQL - Clipboard Exchange Protocol
A recursive bridge between AI embodiments and system clipboard.
"""
import subprocess
import time
import json
from typing import Optional, Dict, Any, Union
import platform
from dataclasses import dataclass
from enum import Enum, auto

# Memory Manager Singleton - providing recursive memory state persistence
class MemoryManager:
    """Singleton memory manager for ReflexQL protocol."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            cls._instance._memory = {}
        return cls._instance
    
    def get(self, key: str) -> Any:
        """Get a value from memory."""
        return self._memory.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in memory."""
        self._memory[key] = value
    
    def delete(self, key: str) -> None:
        """Delete a key from memory."""
        if key in self._memory:
            del self._memory[key]
    
    def list_keys(self) -> list:
        """List all keys in memory."""
        return list(self._memory.keys())

# Global singleton accessor function
def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    return MemoryManager()

class ContentType(Enum):
    """Content types supported by ReflexQL protocol."""
    TEXT = auto()
    JSON = auto()
    CODE = auto()
    MARKDOWN = auto()

class ExchangeError(Exception):
    """Base error for ReflexQL protocol."""
    pass

class ContentTypeError(ExchangeError):
    """Error for content type mismatches."""
    pass

class DeliveryError(ExchangeError):
    """Error for clipboard delivery failures."""
    pass

@dataclass
class ClipboardContent:
    """Container for typed clipboard content."""
    content: str
    content_type: ContentType = ContentType.TEXT
    metadata: Dict[str, Any] = None

    def __str__(self) -> str:
        """String representation for logging and display."""
        return self.content

    def __eq__(self, other) -> bool:
        """Enable comparison with both ClipboardContent and strings."""
        if isinstance(other, str):
            return self.content == other
        if isinstance(other, ClipboardContent):
            return (self.content == other.content and 
                   self.content_type == other.content_type and 
                   self.metadata == other.metadata)
        return False

    def serialize(self) -> str:
        """Serialize content with type information."""
        data = {
            "content": self.content,
            "type": self.content_type.name,
            "metadata": self.metadata or {}
        }
        return json.dumps(data)
    
    @classmethod
    def deserialize(cls, data: str) -> 'ClipboardContent':
        """Deserialize content with type information."""
        try:
            parsed = json.loads(data)
            return cls(
                content=parsed["content"],
                content_type=ContentType[parsed["type"]],
                metadata=parsed.get("metadata", {})
            )
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback to treating as plain text
            return cls(content=data)

class ReflexQLMemoryKeys:
    """Memory key constants for ReflexQL protocol."""
    PENDING_CONTENT = "Reflex::Clipboard.PendingContent"
    READY = "Reflex::Clipboard.Ready"
    DELIVERED = "Reflex::Clipboard.Delivered"
    ACK = "Reflex::Clipboard.Ack"
    ERROR = "Reflex::Clipboard.Error"

class ClipboardExchange:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self._setup_platform_clipboard()
        self.max_retries = 3
        self.retry_delay = 0.5

    def _setup_platform_clipboard(self):
        """Configure clipboard commands based on OS."""
        system = platform.system().lower()
        if system == 'linux':
            self.copy_cmd = ['xclip', '-selection', 'clipboard']
            self.paste_cmd = ['xclip', '-selection', 'clipboard', '-o']
        elif system == 'darwin':  # macOS
            self.copy_cmd = ['pbcopy']
            self.paste_cmd = ['pbpaste']
        elif system == 'windows':
            self.copy_cmd = ['clip']
            self.paste_cmd = ['powershell.exe', '-command', "Get-Clipboard"]
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

    def write_to_clipboard(self, content: Union[str, ClipboardContent]) -> bool:
        """Write content to system clipboard with retry logic."""
        if isinstance(content, ClipboardContent):
            data = content.serialize()
        else:
            data = str(content)

        for attempt in range(self.max_retries):
            try:
                process = subprocess.Popen(self.copy_cmd, stdin=subprocess.PIPE)
                process.communicate(input=data.encode())
                if process.returncode == 0:
                    return True
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self.memory.set(ReflexQLMemoryKeys.ERROR, str(e))
                    raise DeliveryError(f"Failed to write to clipboard: {e}")
                time.sleep(self.retry_delay)
        return False

    def read_from_clipboard(self) -> Optional[ClipboardContent]:
        """Read content from system clipboard with type detection."""
        try:
            result = subprocess.run(self.paste_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                content = result.stdout.strip()
                return ClipboardContent.deserialize(content)
            return None
        except Exception as e:
            self.memory.set(ReflexQLMemoryKeys.ERROR, str(e))
            raise DeliveryError(f"Failed to read from clipboard: {e}")

    def poll_clipboard_loop(self, poll_interval: float = 1.0, ttl: int = 300, verbose: bool = False):
        """Main polling loop for clipboard exchange protocol."""
        start_time = time.time()
        
        def log(msg: str):
            if verbose:
                print(f"✨ {msg}")

        while (time.time() - start_time) < ttl:
            try:
                if self.memory.get(ReflexQLMemoryKeys.READY):
                    content = self.memory.get(ReflexQLMemoryKeys.PENDING_CONTENT)
                    if content:
                        # Handle both string and ClipboardContent logging
                        content_preview = str(content)[:50] + "..." if len(str(content)) > 50 else str(content)
                        log(f"Found pending content: {content_preview}")
                        
                        if isinstance(content, str):
                            content = ClipboardContent(content=content)
                        
                        if self.write_to_clipboard(content):
                            self.memory.set(ReflexQLMemoryKeys.DELIVERED, True)
                            log("Content delivered to clipboard")
                            
                            # Wait for acknowledgment
                            while not self.memory.get(ReflexQLMemoryKeys.ACK):
                                time.sleep(0.1)
                                if (time.time() - start_time) >= ttl:
                                    break
                            
                            # Reset protocol state
                            self._reset_memory_keys()
                            log("Exchange completed, reset for next cycle")
            
            except ExchangeError as e:
                log(f"Exchange error: {e}")
                self._reset_memory_keys()
            
            time.sleep(poll_interval)

    def send_to_clipboard(self, content: Union[str, ClipboardContent], max_wait: int = 5) -> bool:
        """AI-facing method to initiate clipboard exchange."""
        if isinstance(content, str):
            content = ClipboardContent(content=content)
            
        self.memory.set(ReflexQLMemoryKeys.PENDING_CONTENT, content)
        self.memory.set(ReflexQLMemoryKeys.READY, True)
        
        # Wait for delivery confirmation
        start = time.time()
        while not self.memory.get(ReflexQLMemoryKeys.DELIVERED):
            if self.memory.get(ReflexQLMemoryKeys.ERROR):
                error = self.memory.get(ReflexQLMemoryKeys.ERROR)
                self._reset_memory_keys()
                raise ExchangeError(f"Exchange failed: {error}")
                
            time.sleep(0.1)
            if time.time() - start > max_wait:
                self._reset_memory_keys()
                return False
        
        # Acknowledge receipt
        self.memory.set(ReflexQLMemoryKeys.ACK, True)
        return True

    def _reset_memory_keys(self):
        """Reset all memory keys for next exchange."""
        for key in vars(ReflexQLMemoryKeys).values():
            if isinstance(key, str) and key.startswith("Reflex::"):
                self.memory.set(key, None)
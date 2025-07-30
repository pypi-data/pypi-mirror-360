"""
📋 Block Registry
Simple registry for LEGO blocks auto-discovery
"""

from typing import Dict, Any, List, Type
from ..core.lego_factory import get_lego_factory

class BlockRegistry:
    """
    📋 Registry for LinkTune LEGO blocks
    
    Provides auto-discovery and registration of blocks.
    """
    
    def __init__(self):
        self._blocks: Dict[str, Any] = {}
    
    def register(self, name: str, block_class: Type) -> None:
        """Register a block class"""
        self._blocks[name] = block_class
    
    def get_block(self, name: str) -> Any:
        """Get a registered block"""
        return self._blocks.get(name)
    
    def list_blocks(self) -> List[str]:
        """List all registered blocks"""
        return list(self._blocks.keys())
    
    def get_available_blocks(self) -> Dict[str, Any]:
        """Get available blocks from LEGO factory"""
        try:
            factory = get_lego_factory()
            return factory.get_available_blocks()
        except Exception:
            return {}

# Global registry instance
registry = BlockRegistry()
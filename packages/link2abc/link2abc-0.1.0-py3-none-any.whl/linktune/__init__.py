"""
🎵 LinkTune - Transform any link into music with AI

Simple, modular, and progressively enhanced link-to-music conversion.
From basic rule-based generation to professional AI composition with ChatMusician.

Usage:
    pip install linktune
    linktune https://example.com

Enhanced usage:
    pip install linktune[ai]
    linktune https://example.com --ai chatmusician
    
Full neural synthesis:
    pip install linktune[neural]
    linktune https://example.com --neural
"""

__version__ = "0.1.0"
__author__ = "Jerry G.Music Assembly"
__email__ = "jerry@gmusic.dev"

# Core API
from .core.pipeline import Pipeline
from .core.extractor import ContentExtractor
from .core.analyzer import ContentAnalyzer
from .core.generator import MusicGenerator
from .core.converter import FormatConverter

# Block registry for auto-discovery
from .utils.registry import BlockRegistry

# Simple API for quick usage
def link_to_music(url: str, **kwargs) -> dict:
    """
    🎵 Convert any link to music - dead simple API
    
    Args:
        url: URL to convert to music
        **kwargs: Optional configuration (ai='chatmusician', format='abc,midi', etc.)
        
    Returns:
        dict: Generated music files and metadata
        
    Example:
        result = link_to_music("https://example.com", ai="chatmusician")
        print(f"Generated: {result['abc_file']}")
    """
    from .core.pipeline import Pipeline
    
    # Build pipeline based on options
    pipeline = Pipeline.from_config(kwargs)
    
    # Execute conversion
    return pipeline.run(url)

# Version info
def get_version() -> str:
    """Get LinkTune version"""
    return __version__

def get_installed_tiers() -> list[str]:
    """
    🔍 Check which enhancement tiers are available
    
    Returns:
        list: Available tiers ['core', 'ai', 'neural', 'cloud']
    """
    tiers = ['core']  # Always available
    
    try:
        import openai
        tiers.append('ai')
    except ImportError:
        pass
    
    try:
        import torch
        tiers.append('neural')
    except ImportError:
        pass
        
    try:
        import boto3
        tiers.append('cloud')
    except ImportError:
        pass
    
    return tiers

# Public API exports
__all__ = [
    # Core API
    'link_to_music',
    'Pipeline',
    'ContentExtractor',
    'ContentAnalyzer', 
    'MusicGenerator',
    'FormatConverter',
    'BlockRegistry',
    
    # Utility functions
    'get_version',
    'get_installed_tiers',
]

# Package metadata
__package_info__ = {
    'name': 'linktune',
    'version': __version__,
    'description': 'Transform any link into music with AI - simple as that!',
    'author': __author__,
    'email': __email__,
    'url': 'https://github.com/jgwill/linktune',
    'license': 'MIT',
}
#!/usr/bin/env python3
"""
🧱 LEGO Factory - Pipeline Builder for LinkTune
Modular LEGO block architecture adapted from G.Music Assembly system

Provides dynamic pipeline construction with LEGO-style modularity.
"""

import importlib
from typing import Dict, Any, List, Optional, Type, Union
from dataclasses import dataclass
from pathlib import Path

@dataclass
class LEGOBlock:
    """Represents a single LEGO block in the pipeline"""
    name: str
    type: str  # 'extractor', 'analyzer', 'generator', 'converter', 'ai', 'neural'
    module_path: str
    class_name: str
    capabilities: List[str]
    tier_required: str = 'core'  # 'core', 'ai', 'neural', 'cloud'
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class LEGOFactory:
    """
    🧱 LEGO Factory for LinkTune
    
    Dynamically constructs pipelines from modular LEGO blocks.
    Supports progressive enhancement and tier-based loading.
    """
    
    def __init__(self):
        self.available_blocks: Dict[str, LEGOBlock] = {}
        self.loaded_instances: Dict[str, Any] = {}
        self.available_tiers = self._detect_available_tiers()
        
        # Register core blocks
        self._register_core_blocks()
        
        # Register enhancement blocks based on available tiers
        if 'ai' in self.available_tiers:
            self._register_ai_blocks()
        
        if 'neural' in self.available_tiers:
            self._register_neural_blocks()
        
        if 'cloud' in self.available_tiers:
            self._register_cloud_blocks()
    
    def _detect_available_tiers(self) -> List[str]:
        """Detect which enhancement tiers are available"""
        from .. import get_installed_tiers
        return get_installed_tiers()
    
    def _register_core_blocks(self):
        """Register core LEGO blocks (always available)"""
        
        # Content extractors
        self.available_blocks['url_extractor'] = LEGOBlock(
            name='URL Content Extractor',
            type='extractor',
            module_path='linktune.core.extractor',
            class_name='ContentExtractor',
            capabilities=['web_scraping', 'content_extraction', 'platform_detection'],
            tier_required='core'
        )
        
        # Content analyzers
        self.available_blocks['content_analyzer'] = LEGOBlock(
            name='Content Analyzer',
            type='analyzer',
            module_path='linktune.core.analyzer',
            class_name='ContentAnalyzer',
            capabilities=['emotional_analysis', 'theme_extraction', 'structure_analysis'],
            tier_required='core'
        )
        
        # Music generators
        self.available_blocks['abc_generator'] = LEGOBlock(
            name='ABC Music Generator',
            type='generator',
            module_path='linktune.core.generator',
            class_name='MusicGenerator',
            capabilities=['abc_notation', 'rule_based_generation', 'emotional_mapping'],
            tier_required='core'
        )
        
        # Format converters
        self.available_blocks['format_converter'] = LEGOBlock(
            name='Multi-Format Converter',
            type='converter',
            module_path='linktune.core.converter',
            class_name='FormatConverter',
            capabilities=['abc_to_midi', 'multi_format_export', 'tool_integration'],
            tier_required='core'
        )
    
    def _register_ai_blocks(self):
        """Register AI enhancement blocks"""
        
        # ChatMusician AI composer
        self.available_blocks['chatmusician'] = LEGOBlock(
            name='ChatMusician AI Composer',
            type='ai',
            module_path='linktune.blocks.ai.chatmusician',
            class_name='ChatMusicianBlock',
            capabilities=['professional_composition', 'advanced_harmonies', 'style_transfer'],
            tier_required='ai'
        )
        
        # Claude content analyzer
        self.available_blocks['claude'] = LEGOBlock(
            name='Claude AI Analyzer',
            type='ai',
            module_path='linktune.blocks.ai.claude',
            class_name='ClaudeBlock',
            capabilities=['sophisticated_analysis', 'emotional_intelligence', 'cultural_context'],
            tier_required='ai'
        )
        
        # ChatGPT creative analyzer
        self.available_blocks['chatgpt'] = LEGOBlock(
            name='ChatGPT Creative Analyzer',
            type='ai',
            module_path='linktune.blocks.ai.chatgpt',
            class_name='ChatGPTBlock',
            capabilities=['creative_analysis', 'narrative_understanding', 'musical_creativity'],
            tier_required='ai'
        )
        
        # Langfuse prompt injection
        self.available_blocks['langfuse'] = LEGOBlock(
            name='Langfuse Prompt Integration',
            type='prompt_injection',
            module_path='linktune.blocks.langfuse_integration',
            class_name='LangfuseIntegration',
            capabilities=['dynamic_prompts', 'versioning', 'a_b_testing'],
            tier_required='ai'
        )
    
    def _register_neural_blocks(self):
        """Register neural enhancement blocks"""
        
        # Orpheus neural synthesis
        self.available_blocks['orpheus'] = LEGOBlock(
            name='Orpheus Neural Synthesis',
            type='neural',
            module_path='linktune.blocks.neural.orpheus_bridge',
            class_name='create_orpheus_block',  # Use factory function
            capabilities=['neural_synthesis', 'voice_bridge', 'semantic_analysis'],
            tier_required='neural',
            dependencies=['ai']
        )
        
        # Advanced neural processors
        self.available_blocks['neural_harmony'] = LEGOBlock(
            name='Neural Harmony Generator',
            type='neural',
            module_path='linktune.blocks.neural.harmony',
            class_name='NeuralHarmonyBlock',
            capabilities=['advanced_harmonization', 'chord_progression_ai', 'voice_leading'],
            tier_required='neural',
            dependencies=['ai']
        )
    
    def _register_cloud_blocks(self):
        """Register cloud execution blocks"""
        
        # Cloud executor
        self.available_blocks['cloud_executor'] = LEGOBlock(
            name='Cloud Execution Engine',
            type='cloud',
            module_path='linktune.blocks.cloud.executor',
            class_name='CloudExecutor',
            capabilities=['cloud_execution', 'auto_terminate', 'cost_optimization'],
            tier_required='cloud',
            dependencies=['ai']
        )
    
    def build_pipeline(self, config: Dict[str, Any]) -> List[str]:
        """
        🔗 Build pipeline from configuration
        
        Args:
            config: Pipeline configuration
            
        Returns:
            List[str]: Ordered list of block names for the pipeline
        """
        pipeline_blocks = []
        
        # Always start with content extraction
        pipeline_blocks.append('url_extractor')
        
        # Add AI-enhanced analysis if available
        ai_type = config.get('ai')
        if ai_type and ai_type in self.available_blocks:
            # Add AI analyzer first
            pipeline_blocks.append(ai_type)
            
            # Add Langfuse integration if available
            if 'langfuse' in self.available_blocks:
                pipeline_blocks.append('langfuse')
        
        # Add content analysis (always needed)
        pipeline_blocks.append('content_analyzer')
        
        # Add generation based on configuration
        if ai_type == 'chatmusician' and 'chatmusician' in self.available_blocks:
            # Use ChatMusician for generation
            pipeline_blocks.append('chatmusician')
        elif config.get('neural') and 'orpheus' in self.available_blocks:
            # Use neural synthesis
            pipeline_blocks.append('orpheus')
            if 'neural_harmony' in self.available_blocks:
                pipeline_blocks.append('neural_harmony')
        else:
            # Use core generation
            pipeline_blocks.append('abc_generator')
        
        # Add format conversion (always last)
        pipeline_blocks.append('format_converter')
        
        # Add cloud execution if requested
        if config.get('cloud') and 'cloud_executor' in self.available_blocks:
            pipeline_blocks.insert(0, 'cloud_executor')  # Cloud wraps the entire pipeline
        
        return pipeline_blocks
    
    def create_block(self, block_name: str, config: Optional[Dict[str, Any]] = None) -> Any:
        """
        🧱 Create a LEGO block instance
        
        Args:
            block_name: Name of the block to create
            config: Configuration for the block
            
        Returns:
            Any: Block instance
        """
        if block_name in self.loaded_instances:
            return self.loaded_instances[block_name]
        
        if block_name not in self.available_blocks:
            raise ValueError(f"Block '{block_name}' not available")
        
        block_def = self.available_blocks[block_name]
        
        # Check tier availability
        if block_def.tier_required not in self.available_tiers:
            raise ImportError(f"Block '{block_name}' requires '{block_def.tier_required}' tier")
        
        # Check dependencies
        for dep in block_def.dependencies:
            if dep not in self.available_tiers:
                raise ImportError(f"Block '{block_name}' requires dependency '{dep}'")
        
        try:
            # Import and create the block
            module = importlib.import_module(block_def.module_path)
            block_class_or_function = getattr(module, block_def.class_name)
            
            # Check if it's a factory function or class
            if callable(block_class_or_function) and block_def.class_name.startswith('create_'):
                # It's a factory function
                instance = block_class_or_function(config)
            else:
                # It's a class - check if it accepts config parameter
                import inspect
                sig = inspect.signature(block_class_or_function.__init__)
                params = list(sig.parameters.keys())
                
                if len(params) > 1 and ('config' in params or 'timeout' in params or 'kwargs' in params):
                    # Class accepts configuration
                    if 'timeout' in params and block_def.type == 'extractor':
                        # Special handling for ContentExtractor
                        timeout = config.get('extraction_timeout', 10) if config else 10
                        instance = block_class_or_function(timeout=timeout)
                    else:
                        instance = block_class_or_function(config)
                else:
                    # Class doesn't accept configuration
                    instance = block_class_or_function()
            
            # Cache the instance
            self.loaded_instances[block_name] = instance
            
            return instance
            
        except ImportError as e:
            raise ImportError(f"Failed to import block '{block_name}': {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to create block '{block_name}': {e}")
    
    def get_pipeline_info(self, pipeline_blocks: List[str]) -> Dict[str, Any]:
        """
        📊 Get information about a pipeline
        
        Args:
            pipeline_blocks: List of block names in the pipeline
            
        Returns:
            Dict: Pipeline information
        """
        steps = []
        total_capabilities = set()
        required_tiers = set()
        
        for block_name in pipeline_blocks:
            if block_name in self.available_blocks:
                block_def = self.available_blocks[block_name]
                steps.append({
                    'name': block_def.name,
                    'type': block_def.type,
                    'capabilities': block_def.capabilities,
                    'tier': block_def.tier_required
                })
                total_capabilities.update(block_def.capabilities)
                required_tiers.add(block_def.tier_required)
        
        return {
            'steps': steps,
            'total_capabilities': list(total_capabilities),
            'required_tiers': list(required_tiers),
            'available_tiers': self.available_tiers,
            'is_complete': all(tier in self.available_tiers for tier in required_tiers)
        }
    
    def get_available_blocks(self) -> Dict[str, Dict[str, Any]]:
        """
        📋 Get all available blocks grouped by type
        
        Returns:
            Dict: Available blocks grouped by type
        """
        grouped_blocks = {}
        
        for block_name, block_def in self.available_blocks.items():
            block_type = block_def.type
            if block_type not in grouped_blocks:
                grouped_blocks[block_type] = {}
            
            grouped_blocks[block_type][block_name] = {
                'name': block_def.name,
                'capabilities': block_def.capabilities,
                'tier_required': block_def.tier_required,
                'available': block_def.tier_required in self.available_tiers
            }
        
        return grouped_blocks
    
    def create_custom_pipeline(self, block_sequence: List[str], config: Dict[str, Any]) -> List[Any]:
        """
        🎯 Create custom pipeline with specific block sequence
        
        Args:
            block_sequence: Custom sequence of block names
            config: Configuration for all blocks
            
        Returns:
            List[Any]: List of block instances in order
        """
        pipeline_instances = []
        
        for block_name in block_sequence:
            try:
                instance = self.create_block(block_name, config)
                pipeline_instances.append(instance)
            except Exception as e:
                raise RuntimeError(f"Failed to create custom pipeline at block '{block_name}': {e}")
        
        return pipeline_instances
    
    def suggest_pipeline(self, requirements: Dict[str, Any]) -> List[str]:
        """
        💡 Suggest optimal pipeline based on requirements
        
        Args:
            requirements: Requirements and preferences
            
        Returns:
            List[str]: Suggested pipeline block sequence
        """
        pipeline_blocks = []
        
        # Always start with extraction
        pipeline_blocks.append('url_extractor')
        
        # AI enhancement based on requirements
        if requirements.get('quality', 'medium') == 'high':
            # Use best available AI
            if 'chatmusician' in self.available_blocks:
                pipeline_blocks.extend(['langfuse', 'chatmusician'])
            elif 'claude' in self.available_blocks:
                pipeline_blocks.extend(['langfuse', 'claude'])
        
        # Content analysis
        pipeline_blocks.append('content_analyzer')
        
        # Generation
        if requirements.get('style') == 'neural' and 'orpheus' in self.available_blocks:
            pipeline_blocks.append('orpheus')
        elif requirements.get('ai') and requirements.get('ai') in self.available_blocks:
            pipeline_blocks.append(requirements['ai'])
        else:
            pipeline_blocks.append('abc_generator')
        
        # Conversion
        pipeline_blocks.append('format_converter')
        
        # Cloud if requested
        if requirements.get('cloud') and 'cloud_executor' in self.available_blocks:
            pipeline_blocks.insert(0, 'cloud_executor')
        
        return pipeline_blocks
    
    def validate_pipeline(self, pipeline_blocks: List[str]) -> Dict[str, Any]:
        """
        ✅ Validate pipeline configuration
        
        Args:
            pipeline_blocks: Pipeline block sequence
            
        Returns:
            Dict: Validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_blocks': [],
            'tier_issues': []
        }
        
        for block_name in pipeline_blocks:
            if block_name not in self.available_blocks:
                validation['valid'] = False
                validation['missing_blocks'].append(block_name)
                validation['errors'].append(f"Block '{block_name}' not found")
                continue
            
            block_def = self.available_blocks[block_name]
            
            # Check tier availability
            if block_def.tier_required not in self.available_tiers:
                validation['valid'] = False
                validation['tier_issues'].append({
                    'block': block_name,
                    'required': block_def.tier_required,
                    'available': self.available_tiers
                })
                validation['errors'].append(f"Block '{block_name}' requires '{block_def.tier_required}' tier")
            
            # Check dependencies
            for dep in block_def.dependencies:
                if dep not in self.available_tiers:
                    validation['warnings'].append(f"Block '{block_name}' dependency '{dep}' not available")
        
        return validation

# Global factory instance
_factory_instance = None

def get_lego_factory() -> LEGOFactory:
    """Get global LEGO factory instance"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = LEGOFactory()
    return _factory_instance

def build_pipeline_from_config(config: Dict[str, Any]) -> List[str]:
    """
    🔗 Build pipeline from configuration (convenience function)
    
    Args:
        config: Pipeline configuration
        
    Returns:
        List[str]: Pipeline block sequence
    """
    factory = get_lego_factory()
    return factory.build_pipeline(config)
#!/usr/bin/env python3
"""
🔗 LinkTune Pipeline System
Orchestrates the complete link-to-music conversion process

Simple pipeline system inspired by the G.Music Assembly LEGO architecture.
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
import time
from pathlib import Path

from .extractor import ContentExtractor
from .analyzer import ContentAnalyzer
from .generator import MusicGenerator
from .converter import FormatConverter
from .lego_factory import get_lego_factory, build_pipeline_from_config

@dataclass
class PipelineResult:
    """Result of pipeline execution"""
    success: bool
    url: str
    files: Dict[str, str]
    metadata: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None

class Pipeline:
    """
    🔗 LinkTune processing pipeline
    
    Orchestrates the complete link-to-music conversion:
    URL → Extract → Analyze → Generate → Convert → Files
    """
    
    def __init__(self, steps: Optional[List[Any]] = None, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.steps = steps or self._create_default_steps()
        self.results = {}
        
    def _create_default_steps(self) -> List[Any]:
        """Create default processing pipeline"""
        return [
            ContentExtractor(timeout=self.config.get('extraction_timeout', 10)),
            ContentAnalyzer(),
            MusicGenerator(),
            FormatConverter()
        ]
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'Pipeline':
        """
        🏗️ Create pipeline from configuration using LEGO factory
        
        Args:
            config: Configuration with ai, format, and other options
            
        Returns:
            Pipeline: Configured pipeline instance
        """
        # Use LEGO factory to build pipeline
        factory = get_lego_factory()
        
        # Handle Langfuse prompt injection if available
        if 'langfuse' in factory.available_blocks and config.get('prompts'):
            try:
                from ..blocks.langfuse_integration import setup_pipeline_with_langfuse
                config = setup_pipeline_with_langfuse(config)
            except ImportError:
                pass  # Langfuse not available
        
        # Build pipeline blocks using factory
        try:
            pipeline_blocks = factory.build_pipeline(config)
            steps = []
            
            for block_name in pipeline_blocks:
                try:
                    step_instance = factory.create_block(block_name, config)
                    steps.append(step_instance)
                except Exception as e:
                    print(f"Warning: Could not create block '{block_name}': {e}")
                    # Continue with available blocks
            
            # If no steps were created, fallback to default
            if not steps:
                return cls._create_fallback_pipeline(config)
            
            return cls(steps=steps, config=config)
            
        except Exception as e:
            print(f"LEGO factory pipeline creation failed: {e}")
            # Fallback to legacy pipeline creation
            return cls._create_legacy_pipeline(config)
    
    @classmethod
    def _create_legacy_pipeline(cls, config: Dict[str, Any]) -> 'Pipeline':
        """Create pipeline using legacy method (fallback)"""
        steps = []
        
        # Always start with extraction and analysis
        steps.append(ContentExtractor(timeout=config.get('extraction_timeout', 10)))
        steps.append(ContentAnalyzer())
        
        # Add AI enhancement if requested
        ai_type = config.get('ai')
        if ai_type:
            # Try to load AI blocks
            try:
                if ai_type == 'chatmusician':
                    from ..blocks.ai.chatmusician import ChatMusicianBlock
                    steps.append(ChatMusicianBlock(config))
                elif ai_type == 'claude':
                    from ..blocks.ai.claude import ClaudeBlock
                    steps.append(ClaudeBlock(config))
                elif ai_type == 'chatgpt':
                    from ..blocks.ai.chatgpt import ChatGPTBlock
                    steps.append(ChatGPTBlock(config))
                else:
                    # Fallback to basic generator
                    steps.append(MusicGenerator())
            except ImportError:
                # AI blocks not available, use basic generator
                steps.append(MusicGenerator())
        else:
            # Use basic generator
            steps.append(MusicGenerator())
        
        # Always end with format conversion
        steps.append(FormatConverter())
        
        return cls(steps=steps, config=config)
    
    @classmethod
    def _create_fallback_pipeline(cls, config: Dict[str, Any]) -> 'Pipeline':
        """Create minimal fallback pipeline"""
        steps = [
            ContentExtractor(timeout=config.get('extraction_timeout', 10)),
            ContentAnalyzer(),
            MusicGenerator(),
            FormatConverter()
        ]
        return cls(steps=steps, config=config)
    
    def run(self, url: str, output_path: Optional[str] = None) -> PipelineResult:
        """
        🚀 Execute the complete pipeline
        
        Args:
            url: URL to process
            output_path: Optional output path (default: generated)
            
        Returns:
            PipelineResult: Complete processing results
        """
        start_time = time.time()
        
        try:
            # Generate output path if not provided
            if output_path is None:
                output_path = self._generate_output_path(url)
            
            # Execute pipeline steps
            current_data = {'url': url, 'output_path': output_path}
            
            for i, step in enumerate(self.steps):
                step_name = step.__class__.__name__
                
                try:
                    if isinstance(step, ContentExtractor):
                        result = step.extract(url)
                        if not result.success:
                            raise RuntimeError(f"Content extraction failed: {result.error_message}")
                        current_data['extracted_content'] = result
                        
                    elif isinstance(step, ContentAnalyzer):
                        extracted = current_data['extracted_content']
                        analysis = step.analyze_content(extracted.content)
                        current_data['content_analysis'] = analysis
                        
                    elif isinstance(step, MusicGenerator):
                        analysis = current_data['content_analysis']
                        abc_notation = step.generate_abc(analysis, self.config)
                        current_data['abc_notation'] = abc_notation
                        
                    elif isinstance(step, FormatConverter):
                        abc_notation = current_data['abc_notation']
                        formats = self.config.get('format', ['abc', 'midi'])
                        if isinstance(formats, str):
                            formats = formats.split(',')
                        
                        conversion_result = step.convert(abc_notation, output_path, formats)
                        current_data['conversion_result'] = conversion_result
                        
                    else:
                        # Handle AI blocks or custom steps
                        if hasattr(step, 'process'):
                            result = step.process(current_data)
                            current_data.update(result)
                        elif hasattr(step, 'generate_abc'):
                            # AI music generator
                            analysis = current_data['content_analysis']
                            abc_notation = step.generate_abc(analysis, self.config)
                            current_data['abc_notation'] = abc_notation
                    
                    self.results[step_name] = current_data.copy()
                    
                except Exception as e:
                    raise RuntimeError(f"Step {step_name} failed: {str(e)}")
            
            # Build final result
            execution_time = time.time() - start_time
            conversion_result = current_data.get('conversion_result', {})
            
            return PipelineResult(
                success=True,
                url=url,
                files=conversion_result.get('files', {}),
                metadata={
                    'extraction': {
                        'platform': current_data['extracted_content'].platform,
                        'title': current_data['extracted_content'].title,
                    },
                    'analysis': current_data['content_analysis'].to_dict(),
                    'conversion': {
                        'formats_generated': conversion_result.get('formats_generated', []),
                        'formats_failed': conversion_result.get('formats_failed', []),
                    },
                    'pipeline_config': self.config,
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return PipelineResult(
                success=False,
                url=url,
                files={},
                metadata={'pipeline_config': self.config},
                execution_time=execution_time,
                error=str(e)
            )
    
    def _generate_output_path(self, url: str) -> str:
        """Generate output path from URL"""
        from urllib.parse import urlparse
        import hashlib
        
        # Create a safe filename from URL
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '').replace('.', '_')
        
        # Add hash for uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Generate timestamp
        timestamp = int(time.time())
        
        # Create output directory
        output_dir = Path(self.config.get('output_dir', 'output'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"linktune_{domain}_{timestamp}_{url_hash}"
        
        return str(output_dir / filename)
    
    def inject_prompt(self, stage: str, prompt: str) -> None:
        """
        💉 Inject custom prompt at pipeline stage
        
        Args:
            stage: Stage name to inject prompt
            prompt: Prompt text to inject
        """
        if 'prompts' not in self.config:
            self.config['prompts'] = {}
        
        self.config['prompts'][stage] = prompt
    
    def get_step_results(self) -> Dict[str, Any]:
        """Get results from each pipeline step"""
        return self.results.copy()
    
    def add_step(self, step: Any, position: Optional[int] = None) -> None:
        """
        ➕ Add a step to the pipeline
        
        Args:
            step: Step instance to add
            position: Optional position to insert (default: append)
        """
        if position is None:
            self.steps.append(step)
        else:
            self.steps.insert(position, step)
    
    def remove_step(self, step_type: type) -> bool:
        """
        ➖ Remove step by type
        
        Args:
            step_type: Type of step to remove
            
        Returns:
            bool: True if step was removed
        """
        for i, step in enumerate(self.steps):
            if isinstance(step, step_type):
                del self.steps[i]
                return True
        return False
    
    def get_pipeline_info(self) -> Dict[str, Any]:
        """Get information about the pipeline"""
        step_info = []
        for step in self.steps:
            info = {
                'name': step.__class__.__name__,
                'module': step.__class__.__module__,
            }
            
            # Add additional info if available
            if hasattr(step, 'get_info'):
                info.update(step.get_info())
            elif hasattr(step, 'get_supported_formats'):
                info['supported_formats'] = step.get_supported_formats()
            
            step_info.append(info)
        
        # Get LEGO factory info if available
        lego_info = {}
        try:
            factory = get_lego_factory()
            lego_info = {
                'available_tiers': factory.available_tiers,
                'available_blocks': list(factory.available_blocks.keys()),
                'lego_enabled': True
            }
        except Exception:
            lego_info = {'lego_enabled': False}
        
        return {
            'steps': step_info,
            'config': self.config,
            'step_count': len(self.steps),
            'lego_factory': lego_info
        }
    
    @classmethod
    def get_available_blocks(cls) -> Dict[str, Any]:
        """Get all available LEGO blocks"""
        try:
            factory = get_lego_factory()
            return factory.get_available_blocks()
        except Exception as e:
            return {'error': str(e), 'available': False}
    
    @classmethod
    def suggest_pipeline(cls, requirements: Dict[str, Any]) -> List[str]:
        """Suggest optimal pipeline based on requirements"""
        try:
            factory = get_lego_factory()
            return factory.suggest_pipeline(requirements)
        except Exception as e:
            print(f"Pipeline suggestion failed: {e}")
            return ['url_extractor', 'content_analyzer', 'abc_generator', 'format_converter']
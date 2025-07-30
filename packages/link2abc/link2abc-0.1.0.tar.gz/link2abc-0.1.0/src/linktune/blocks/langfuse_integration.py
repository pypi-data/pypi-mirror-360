#!/usr/bin/env python3
"""
🧵 Langfuse Integration - Prompt Injection System
Modular prompt management and injection for LinkTune LEGO blocks

Allows dynamic prompt injection from Langfuse "wherever we want" in the pipeline.
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False

@dataclass
class PromptConfig:
    """Configuration for Langfuse prompt injection"""
    name: str
    version: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    fallback: Optional[str] = None

class LangfuseIntegration:
    """
    🧵 Langfuse prompt injection system for LinkTune
    
    Provides dynamic prompt management and injection across all LEGO blocks.
    Enables prompt versioning, A/B testing, and real-time updates.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        if not LANGFUSE_AVAILABLE:
            raise ImportError("Langfuse library not installed. Install with: pip install langfuse")
        
        # Initialize Langfuse client
        self.langfuse = Langfuse(
            secret_key=os.getenv('LANGFUSE_SECRET_KEY'),
            public_key=os.getenv('LANGFUSE_PUBLIC_KEY'),
            host=os.getenv('LANGFUSE_HOST', 'https://cloud.langfuse.com')
        )
        
        # Cache for prompts to avoid repeated API calls
        self.prompt_cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 300)  # 5 minutes default
        self.last_cache_update = {}
        
        self.capabilities = [
            'dynamic_prompts',
            'versioning',
            'a_b_testing',
            'real_time_updates',
            'prompt_analytics',
            'fallback_management'
        ]
    
    def inject_prompt(self, prompt_name: str, variables: Optional[Dict[str, Any]] = None, 
                     fallback: Optional[str] = None, version: Optional[str] = None) -> str:
        """
        🎯 Inject prompt from Langfuse with variables
        
        Args:
            prompt_name: Name of the prompt in Langfuse
            variables: Variables to substitute in the prompt
            fallback: Fallback prompt if Langfuse fails
            version: Specific version to use (optional)
            
        Returns:
            str: Rendered prompt with variables substituted
        """
        try:
            # Get prompt from cache or Langfuse
            prompt_template = self._get_prompt(prompt_name, version)
            
            if not prompt_template:
                # Use fallback if provided
                if fallback:
                    return self._render_template(fallback, variables or {})
                else:
                    raise ValueError(f"Prompt '{prompt_name}' not found and no fallback provided")
            
            # Render prompt with variables
            rendered_prompt = self._render_template(prompt_template, variables or {})
            
            # Track usage in Langfuse
            self._track_prompt_usage(prompt_name, version, variables)
            
            return rendered_prompt
            
        except Exception as e:
            print(f"Langfuse prompt injection failed: {e}")
            
            # Fallback handling
            if fallback:
                return self._render_template(fallback, variables or {})
            else:
                # Return a generic error prompt
                return f"# Prompt injection failed for '{prompt_name}'\n# Error: {e}"
    
    def inject_prompts_batch(self, prompt_configs: List[PromptConfig]) -> Dict[str, str]:
        """
        🎯 Inject multiple prompts in batch
        
        Args:
            prompt_configs: List of prompt configurations
            
        Returns:
            Dict: Mapping of prompt names to rendered prompts
        """
        results = {}
        
        for config in prompt_configs:
            try:
                rendered = self.inject_prompt(
                    prompt_name=config.name,
                    variables=config.variables,
                    fallback=config.fallback,
                    version=config.version
                )
                results[config.name] = rendered
            except Exception as e:
                print(f"Failed to inject prompt '{config.name}': {e}")
                results[config.name] = config.fallback or f"# Prompt '{config.name}' failed"
        
        return results
    
    def setup_ai_block_prompts(self, block_type: str, content_analysis: Any) -> Dict[str, str]:
        """
        🤖 Setup prompts for AI blocks with content-aware injection
        
        Args:
            block_type: Type of AI block ('chatmusician', 'claude', 'chatgpt')
            content_analysis: Content analysis object for variable extraction
            
        Returns:
            Dict: Mapping of prompt types to rendered prompts
        """
        # Extract variables from content analysis
        variables = self._extract_analysis_variables(content_analysis)
        
        # Define prompt configurations for each block type
        prompt_configs = {
            'chatmusician': [
                PromptConfig(
                    name=f'chatmusician_composition_v2',
                    variables=variables,
                    fallback=self._get_default_chatmusician_prompt()
                ),
                PromptConfig(
                    name=f'chatmusician_style_guidance',
                    variables=variables,
                    fallback="Generate music in {style} style with {emotion} emotion."
                )
            ],
            'claude': [
                PromptConfig(
                    name=f'claude_content_analysis_v2',
                    variables=variables,
                    fallback=self._get_default_claude_prompt()
                ),
                PromptConfig(
                    name=f'claude_emotional_mapping',
                    variables=variables,
                    fallback="Analyze emotional content for musical interpretation."
                )
            ],
            'chatgpt': [
                PromptConfig(
                    name=f'chatgpt_creative_analysis_v2',
                    variables=variables,
                    fallback=self._get_default_chatgpt_prompt()
                ),
                PromptConfig(
                    name=f'chatgpt_narrative_structure',
                    variables=variables,
                    fallback="Analyze narrative structure for musical composition."
                )
            ]
        }
        
        # Get prompts for the specific block type
        configs = prompt_configs.get(block_type, [])
        return self.inject_prompts_batch(configs)
    
    def create_pipeline_prompts(self, pipeline_config: Dict[str, Any]) -> Dict[str, str]:
        """
        🔗 Create prompts for entire pipeline with context awareness
        
        Args:
            pipeline_config: Pipeline configuration
            
        Returns:
            Dict: Mapping of pipeline step names to prompts
        """
        pipeline_prompts = {}
        
        # Extract pipeline context
        context_variables = {
            'pipeline_type': pipeline_config.get('type', 'standard'),
            'ai_enabled': pipeline_config.get('ai') is not None,
            'neural_enabled': pipeline_config.get('neural', False),
            'cloud_enabled': pipeline_config.get('cloud', False),
            'output_formats': pipeline_config.get('format', ['abc'])
        }
        
        # Define pipeline prompt configurations
        pipeline_prompt_configs = [
            PromptConfig(
                name='extraction_guidance',
                variables=context_variables,
                fallback="Extract content from the provided URL."
            ),
            PromptConfig(
                name='analysis_enhancement',
                variables=context_variables,
                fallback="Analyze content for emotional and thematic elements."
            ),
            PromptConfig(
                name='generation_optimization',
                variables=context_variables,
                fallback="Generate music optimized for the target format."
            )
        ]
        
        return self.inject_prompts_batch(pipeline_prompt_configs)
    
    def _get_prompt(self, prompt_name: str, version: Optional[str] = None) -> Optional[str]:
        """Get prompt from cache or Langfuse API"""
        
        # Check cache first
        cache_key = f"{prompt_name}:{version or 'latest'}"
        
        if self._is_cache_valid(cache_key):
            return self.prompt_cache.get(cache_key)
        
        try:
            # Fetch from Langfuse
            if version:
                prompt = self.langfuse.get_prompt(prompt_name, version=version)
            else:
                prompt = self.langfuse.get_prompt(prompt_name)
            
            if prompt:
                prompt_content = prompt.prompt
                # Cache the prompt
                self.prompt_cache[cache_key] = prompt_content
                self.last_cache_update[cache_key] = time.time()
                return prompt_content
            
        except Exception as e:
            print(f"Failed to fetch prompt '{prompt_name}' from Langfuse: {e}")
        
        return None
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached prompt is still valid"""
        if cache_key not in self.prompt_cache:
            return False
        
        import time
        last_update = self.last_cache_update.get(cache_key, 0)
        return (time.time() - last_update) < self.cache_ttl
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render prompt template with variables"""
        try:
            # Simple variable substitution using string formatting
            return template.format(**variables)
        except KeyError as e:
            print(f"Missing variable in prompt template: {e}")
            return template
        except Exception as e:
            print(f"Error rendering prompt template: {e}")
            return template
    
    def _extract_analysis_variables(self, content_analysis: Any) -> Dict[str, Any]:
        """Extract variables from content analysis for prompt injection"""
        if not content_analysis:
            return {}
        
        variables = {}
        
        # Extract emotional profile variables
        if hasattr(content_analysis, 'emotional_profile') and content_analysis.emotional_profile:
            ep = content_analysis.emotional_profile
            variables.update({
                'emotion': ep.primary_emotion.value if hasattr(ep.primary_emotion, 'value') else str(ep.primary_emotion),
                'intensity': ep.intensity,
                'emotional_confidence': ep.confidence
            })
        
        # Extract themes
        if hasattr(content_analysis, 'themes') and content_analysis.themes:
            theme_names = [t.name for t in content_analysis.themes[:3]]
            variables.update({
                'themes': ', '.join(theme_names),
                'primary_theme': theme_names[0] if theme_names else 'general',
                'theme_count': len(theme_names)
            })
        
        # Extract musical suggestions
        if hasattr(content_analysis, 'musical_suggestions') and content_analysis.musical_suggestions:
            ms = content_analysis.musical_suggestions
            variables.update({
                'suggested_key': ms.get('key', 'C major'),
                'suggested_tempo': ms.get('tempo', 'moderato'),
                'suggested_style': ms.get('style', 'classical'),
                'complexity_level': ms.get('complexity_level', 'medium')
            })
        
        # Extract structure information
        if hasattr(content_analysis, 'structure') and content_analysis.structure:
            struct = content_analysis.structure
            variables.update({
                'content_length': struct.get('length', 100),
                'content_type': struct.get('content_type', 'unknown'),
                'complexity': struct.get('complexity', 'medium')
            })
        
        return variables
    
    def _track_prompt_usage(self, prompt_name: str, version: Optional[str], variables: Optional[Dict[str, Any]]):
        """Track prompt usage in Langfuse for analytics"""
        try:
            # Create a generation record in Langfuse
            self.langfuse.generation(
                name=f"prompt_injection_{prompt_name}",
                prompt={
                    "name": prompt_name,
                    "version": version or "latest",
                    "variables": variables or {}
                },
                metadata={
                    "tool": "LinkTune",
                    "injection_type": "dynamic_prompt"
                }
            )
        except Exception as e:
            # Don't fail on tracking errors
            print(f"Failed to track prompt usage: {e}")
    
    def _get_default_chatmusician_prompt(self) -> str:
        """Default ChatMusician prompt fallback"""
        return """Generate professional ABC notation for a musical composition with the following characteristics:

Primary Emotion: {emotion}
Emotional Intensity: {intensity:.2f}
Themes: {themes}

Musical Requirements:
- Professional quality composition with sophisticated harmonies
- Emotionally resonant melody that reflects the {emotion} feeling
- Appropriate chord progressions for the emotional content
- Clear musical structure with logical phrasing
- Standard ABC notation format with proper headers
- Include ornamental expressions where appropriate
- Maintain musical coherence throughout

Style: {suggested_style}
Key: {suggested_key}
Tempo: {suggested_tempo}"""
    
    def _get_default_claude_prompt(self) -> str:
        """Default Claude prompt fallback"""
        return """Analyze the following content for musical composition. Provide detailed analysis covering:

1. EMOTIONAL ANALYSIS:
   - Primary emotion and intensity
   - Secondary emotions present
   - Emotional arc through the content

2. THEMATIC ANALYSIS:
   - Main themes and concepts
   - Cultural context and references
   - Narrative elements

3. MUSICAL SUGGESTIONS:
   - Appropriate key and mode
   - Tempo suggestions
   - Style recommendations
   - Structural suggestions

Current context: {content_type} with {theme_count} themes
Primary theme: {primary_theme}
Content length: {content_length} words"""
    
    def _get_default_chatgpt_prompt(self) -> str:
        """Default ChatGPT prompt fallback"""
        return """Analyze the following content for musical composition, focusing on creative elements:

1. EMOTIONAL JOURNEY:
   - Primary emotion: {emotion}
   - Emotional intensity and evolution

2. CREATIVE THEMES:
   - Main themes: {themes}
   - Symbolic elements and metaphors
   - Narrative structure

3. MUSICAL INSPIRATION:
   - Suggested style: {suggested_style}
   - Key and harmonic approach: {suggested_key}
   - Tempo: {suggested_tempo}

4. CREATIVE DIRECTION:
   - Overall musical character
   - Structural suggestions
   - Innovative interpretations

Complexity level: {complexity_level}"""
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this integration"""
        return {
            'name': 'Langfuse Prompt Integration',
            'type': 'prompt_injection',
            'capabilities': self.capabilities,
            'available': LANGFUSE_AVAILABLE,
            'cached_prompts': len(self.prompt_cache),
            'cache_ttl': self.cache_ttl
        }

# Helper functions for easy integration

def inject_prompt_into_config(config: Dict[str, Any], prompt_name: str, 
                             variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    🎯 Helper function to inject Langfuse prompt into any config
    
    Args:
        config: Existing configuration
        prompt_name: Name of prompt to inject
        variables: Variables for prompt rendering
        
    Returns:
        Dict: Updated configuration with injected prompt
    """
    try:
        langfuse_integration = LangfuseIntegration()
        injected_prompt = langfuse_integration.inject_prompt(prompt_name, variables)
        
        # Add to prompts section of config
        if 'prompts' not in config:
            config['prompts'] = {}
        
        config['prompts'][prompt_name] = injected_prompt
        
    except Exception as e:
        print(f"Prompt injection failed: {e}")
    
    return config

def setup_pipeline_with_langfuse(pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔗 Setup entire pipeline with Langfuse prompt injection
    
    Args:
        pipeline_config: Base pipeline configuration
        
    Returns:
        Dict: Enhanced configuration with Langfuse prompts
    """
    try:
        langfuse_integration = LangfuseIntegration()
        
        # Get AI block type if specified
        ai_type = pipeline_config.get('ai')
        if ai_type:
            # Inject AI-specific prompts
            ai_prompts = langfuse_integration.setup_ai_block_prompts(ai_type, None)
            
            if 'prompts' not in pipeline_config:
                pipeline_config['prompts'] = {}
            
            pipeline_config['prompts'].update(ai_prompts)
        
        # Inject general pipeline prompts
        pipeline_prompts = langfuse_integration.create_pipeline_prompts(pipeline_config)
        
        if 'prompts' not in pipeline_config:
            pipeline_config['prompts'] = {}
        
        pipeline_config['prompts'].update(pipeline_prompts)
        
    except Exception as e:
        print(f"Pipeline Langfuse setup failed: {e}")
    
    return pipeline_config
#!/usr/bin/env python3
"""
🤖 ChatMusician Block - The Star AI Composer
Professional AI-powered music generation for LinkTune

Based on the G.Music Assembly ChatMusician integration but simplified for packaging.
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ...core.analyzer import ContentAnalysis

@dataclass
class ChatMusicianConfig:
    """Configuration for ChatMusician API"""
    api_endpoint: str = "http://localhost:8000"
    api_key: str = "demo_key"
    model_version: str = "latest"
    timeout: int = 30
    max_retries: int = 3
    
    @classmethod
    def from_env(cls) -> 'ChatMusicianConfig':
        """Create config from environment variables"""
        return cls(
            api_endpoint=os.getenv('CHATMUSICIAN_ENDPOINT', cls.api_endpoint),
            api_key=os.getenv('CHATMUSICIAN_API_KEY', cls.api_key),
            model_version=os.getenv('CHATMUSICIAN_MODEL', cls.model_version),
            timeout=int(os.getenv('CHATMUSICIAN_TIMEOUT', str(cls.timeout))),
            max_retries=int(os.getenv('CHATMUSICIAN_RETRIES', str(cls.max_retries)))
        )

class ChatMusicianBlock:
    """
    🤖 ChatMusician AI Music Generation Block
    
    Professional AI composer that generates sophisticated ABC notation
    with advanced harmonies, style awareness, and ornamental expressions.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize ChatMusician configuration
        self.chatmusician_config = ChatMusicianConfig.from_env()
        
        # Override with provided config
        if 'chatmusician' in self.config:
            cm_config = self.config['chatmusician']
            for key, value in cm_config.items():
                if hasattr(self.chatmusician_config, key):
                    setattr(self.chatmusician_config, key, value)
        
        # Session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.chatmusician_config.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'LinkTune-ChatMusician-Client/1.0'
        })
        
        self.capabilities = [
            'professional_composition',
            'advanced_harmonies', 
            'style_transfer',
            'ornamental_expressions',
            'genre_awareness',
            'emotional_intelligence'
        ]
    
    def generate_abc(self, analysis: ContentAnalysis, config: Dict[str, Any]) -> str:
        """
        🎵 Generate professional ABC notation using ChatMusician AI
        
        Args:
            analysis: Content analysis with emotional and thematic data
            config: Generation configuration
            
        Returns:
            str: Professional ABC notation
        """
        try:
            # Check if we can connect to ChatMusician
            if not self._test_connection():
                # Fallback to rule-based generation
                return self._fallback_generation(analysis, config)
            
            # Build musical prompt from analysis
            prompt = self._build_musical_prompt(analysis)
            
            # Get style preferences
            style = self._determine_style(analysis, config)
            
            # Calculate emotional parameters
            emotional_weight = analysis.emotional_profile.intensity
            complexity = self._determine_complexity(analysis)
            
            # Generate with ChatMusician
            abc_result = self._call_chatmusician_api(
                prompt=prompt,
                style=style,
                emotional_weight=emotional_weight,
                complexity=complexity,
                config=config
            )
            
            # Enhance and validate result
            enhanced_abc = self._enhance_abc_notation(abc_result, analysis)
            
            return enhanced_abc
            
        except Exception as e:
            # Fallback to rule-based generation
            print(f"ChatMusician generation failed: {e}")
            return self._fallback_generation(analysis, config)
    
    def _test_connection(self) -> bool:
        """Test connection to ChatMusician API"""
        try:
            response = self.session.get(
                f"{self.chatmusician_config.api_endpoint}/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def _build_musical_prompt(self, analysis: ContentAnalysis) -> str:
        """Build musical generation prompt from content analysis"""
        emotion = analysis.emotional_profile.primary_emotion.value
        intensity = analysis.emotional_profile.intensity
        themes = [t.name for t in analysis.themes[:3]]
        
        # Check for custom prompts
        custom_prompts = self.config.get('prompts', {})
        if 'chatmusician_composition' in custom_prompts:
            # Use custom prompt template
            prompt_template = custom_prompts['chatmusician_composition']
            return prompt_template.format(
                emotion=emotion,
                intensity=intensity,
                themes=', '.join(themes)
            )
        
        # Default prompt
        prompt = f"""Generate professional ABC notation for a musical composition with the following characteristics:

Primary Emotion: {emotion.title()}
Emotional Intensity: {intensity:.2f} (0.0 = subtle, 1.0 = intense)
Themes: {', '.join(themes) if themes else 'general content'}

Musical Requirements:
- Professional quality composition with sophisticated harmonies
- Emotionally resonant melody that reflects the {emotion} feeling
- Appropriate chord progressions for the emotional content
- Clear musical structure with logical phrasing
- Standard ABC notation format with proper headers
- Include ornamental expressions where appropriate
- Maintain musical coherence throughout

Style Guidelines:
- Use the emotional intensity to guide tempo and dynamics
- Incorporate thematic elements into the melodic development
- Create a complete, performance-ready composition
- Ensure the music tells the emotional story of the content"""

        return prompt
    
    def _determine_style(self, analysis: ContentAnalysis, config: Dict[str, Any]) -> str:
        """Determine musical style from analysis and config"""
        # Check explicit style in config
        if 'style' in config:
            return config['style']
        
        # Infer style from content themes
        for theme in analysis.themes:
            if theme.name in ['technology', 'science']:
                return 'contemporary'
            elif theme.name in ['nature', 'environment']:
                return 'celtic'
            elif theme.name in ['relationships', 'love']:
                return 'romantic'
            elif theme.name in ['adventure', 'action']:
                return 'cinematic'
        
        # Default based on emotion
        emotion = analysis.emotional_profile.primary_emotion.value
        style_map = {
            'joy': 'classical',
            'sadness': 'blues', 
            'contemplation': 'ambient',
            'excitement': 'jazz',
            'peace': 'folk',
            'love': 'romantic'
        }
        
        return style_map.get(emotion, 'classical')
    
    def _determine_complexity(self, analysis: ContentAnalysis) -> str:
        """Determine musical complexity from content analysis"""
        content_complexity = analysis.structure.get('complexity', 'medium')
        content_length = analysis.structure.get('length', 100)
        
        if content_complexity == 'simple' or content_length < 50:
            return 'simple'
        elif content_complexity == 'complex' or content_length > 500:
            return 'complex'
        else:
            return 'medium'
    
    def _call_chatmusician_api(self, prompt: str, style: str, emotional_weight: float,
                              complexity: str, config: Dict[str, Any]) -> str:
        """Call ChatMusician API for music generation"""
        
        payload = {
            'prompt': prompt,
            'style': style,
            'emotional_weight': emotional_weight,
            'complexity': complexity,
            'output_format': 'abc_notation',
            'features': {
                'advanced_harmonies': True,
                'ornamental_expressions': True,
                'style_transfer': True,
                'professional_quality': True
            },
            'model_version': self.chatmusician_config.model_version
        }
        
        # Add any additional config
        if 'chatmusician_params' in config:
            payload.update(config['chatmusician_params'])
        
        for attempt in range(self.chatmusician_config.max_retries):
            try:
                response = self.session.post(
                    f"{self.chatmusician_config.api_endpoint}/api/generate",
                    json=payload,
                    timeout=self.chatmusician_config.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    abc_notation = result.get('abc_notation', '')
                    
                    if abc_notation:
                        return abc_notation
                    else:
                        raise ValueError("Empty ABC notation returned")
                        
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise ValueError(f"API error: {response.status_code} - {response.text}")
                    
            except requests.RequestException as e:
                if attempt == self.chatmusician_config.max_retries - 1:
                    raise
                time.sleep(1)
        
        raise RuntimeError("ChatMusician API call failed after all retries")
    
    def _enhance_abc_notation(self, abc_result: str, analysis: ContentAnalysis) -> str:
        """Enhance generated ABC with metadata and validation"""
        emotion = analysis.emotional_profile.primary_emotion.value
        themes = ', '.join([t.name for t in analysis.themes])
        
        # Add LinkTune metadata header
        enhanced_header = f"""% Generated by LinkTune ChatMusician AI
% Professional AI Composition Engine
% Emotion: {emotion.title()} (intensity: {analysis.emotional_profile.intensity:.2f})
% Themes: {themes}
% Features: Advanced harmonies, ornamental expressions, style transfer
% Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        # Ensure the ABC has proper structure
        if not abc_result.startswith('X:'):
            # Add minimal headers if missing
            abc_result = f"""X:1
T:AI Generated Composition
C:ChatMusician via LinkTune
M:4/4
L:1/8
Q:1/4=120
K:C major
{abc_result}"""
        
        return enhanced_header + abc_result
    
    def _fallback_generation(self, analysis: ContentAnalysis, config: Dict[str, Any]) -> str:
        """Fallback to rule-based generation if ChatMusician fails"""
        from ...core.generator import MusicGenerator
        
        generator = MusicGenerator()
        abc_result = generator.generate_abc(analysis, config)
        
        # Add fallback notice
        fallback_header = """% Generated by LinkTune Core Engine (ChatMusician fallback)
% Note: ChatMusician AI was not available, using rule-based generation
% For professional AI composition, ensure ChatMusician API is accessible

"""
        
        return fallback_header + abc_result
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this block"""
        return {
            'name': 'ChatMusician AI Composer',
            'type': 'ai_generator',
            'capabilities': self.capabilities,
            'api_endpoint': self.chatmusician_config.api_endpoint,
            'connected': self._test_connection(),
            'model_version': self.chatmusician_config.model_version
        }
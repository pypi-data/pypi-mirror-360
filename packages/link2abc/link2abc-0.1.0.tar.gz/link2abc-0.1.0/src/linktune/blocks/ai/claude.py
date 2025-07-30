#!/usr/bin/env python3
"""
🌿 Claude Block - Sophisticated Content Analysis
Enhanced content understanding to feed better data to music generation

Provides sophisticated content analysis using Claude AI.
"""

import os
from typing import Dict, Any, Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from ...core.analyzer import ContentAnalysis, EmotionalProfile, Theme, Emotion

class ClaudeBlock:
    """
    🌿 Claude AI content analysis block
    
    Provides sophisticated content understanding and emotional analysis
    to enhance music generation quality.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
        
        # Initialize Claude client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = self.config.get('claude_model', 'claude-3-sonnet-20240229')
        
        self.capabilities = [
            'sophisticated_analysis',
            'emotional_intelligence',
            'thematic_extraction',
            'cultural_context',
            'narrative_understanding'
        ]
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🧠 Enhanced content analysis using Claude
        
        Args:
            data: Pipeline data containing extracted content
            
        Returns:
            Dict: Enhanced analysis data
        """
        extracted_content = data.get('extracted_content')
        if not extracted_content:
            return data
        
        try:
            # Get enhanced analysis from Claude
            enhanced_analysis = self._analyze_with_claude(extracted_content.content)
            
            # Merge with existing analysis or replace
            if 'content_analysis' in data:
                # Enhance existing analysis
                existing = data['content_analysis']
                enhanced_analysis = self._merge_analyses(existing, enhanced_analysis)
            
            data['content_analysis'] = enhanced_analysis
            data['claude_enhanced'] = True
            
            return data
            
        except Exception as e:
            # Fallback: return original data
            print(f"Claude analysis failed: {e}")
            return data
    
    def _analyze_with_claude(self, content: str) -> ContentAnalysis:
        """Analyze content using Claude AI"""
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(content)
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{
                "role": "user", 
                "content": prompt
            }]
        )
        
        # Parse Claude's response
        analysis_text = response.content[0].text
        
        # Convert to ContentAnalysis object
        return self._parse_claude_response(analysis_text, content)
    
    def _build_analysis_prompt(self, content: str) -> str:
        """Build analysis prompt for Claude"""
        
        # Check for custom prompts
        custom_prompts = self.config.get('prompts', {})
        if 'claude_analysis' in custom_prompts:
            return custom_prompts['claude_analysis'].format(content=content)
        
        # Default analysis prompt
        return f"""Analyze the following content for musical composition. Provide a detailed analysis covering:

1. EMOTIONAL ANALYSIS:
   - Primary emotion (joy, sadness, contemplation, excitement, peace, anger, fear, love, curiosity, melancholy)
   - Emotional intensity (0.0 to 1.0)
   - Secondary emotions present
   - Emotional arc/journey through the content

2. THEMATIC ANALYSIS:
   - Main themes and concepts
   - Cultural context and references
   - Narrative elements
   - Symbolic content

3. MUSICAL SUGGESTIONS:
   - Appropriate musical key and mode
   - Tempo suggestions
   - Style recommendations
   - Structural suggestions

4. CONTENT CHARACTERISTICS:
   - Complexity level
   - Tone and mood
   - Energy level
   - Overall character

Please format your response as structured analysis that can guide music generation.

CONTENT TO ANALYZE:
{content}

ANALYSIS:"""
    
    def _parse_claude_response(self, analysis_text: str, original_content: str) -> ContentAnalysis:
        """Parse Claude's analysis into ContentAnalysis object"""
        
        # This is a simplified parser - in production you'd want more robust parsing
        
        # Extract emotion (simple keyword matching)
        emotion_map = {
            'joy': Emotion.JOY,
            'happiness': Emotion.JOY,
            'sadness': Emotion.SADNESS,
            'sad': Emotion.SADNESS,
            'contemplation': Emotion.CONTEMPLATION,
            'thoughtful': Emotion.CONTEMPLATION,
            'excitement': Emotion.EXCITEMENT,
            'excited': Emotion.EXCITEMENT,
            'peace': Emotion.PEACE,
            'peaceful': Emotion.PEACE,
            'calm': Emotion.PEACE,
            'anger': Emotion.ANGER,
            'angry': Emotion.ANGER,
            'fear': Emotion.FEAR,
            'fearful': Emotion.FEAR,
            'love': Emotion.LOVE,
            'loving': Emotion.LOVE,
            'curiosity': Emotion.CURIOSITY,
            'curious': Emotion.CURIOSITY,
            'melancholy': Emotion.MELANCHOLY,
            'melancholic': Emotion.MELANCHOLY
        }
        
        # Find primary emotion
        primary_emotion = Emotion.CONTEMPLATION  # default
        analysis_lower = analysis_text.lower()
        
        for word, emotion in emotion_map.items():
            if word in analysis_lower:
                primary_emotion = emotion
                break
        
        # Extract intensity (look for numerical values)
        intensity = 0.5  # default
        import re
        intensity_matches = re.findall(r'intensity[:\s]*([0-9.]+)', analysis_lower)
        if intensity_matches:
            try:
                intensity = float(intensity_matches[0])
                intensity = max(0.0, min(1.0, intensity))  # clamp to 0-1
            except ValueError:
                pass
        
        # Extract themes (simple keyword extraction)
        themes = []
        theme_keywords = {
            'technology': ['technology', 'digital', 'computer', 'ai', 'tech'],
            'nature': ['nature', 'environment', 'natural', 'earth', 'green'],
            'relationships': ['relationship', 'family', 'friend', 'love', 'social'],
            'creativity': ['creative', 'art', 'artistic', 'imagination', 'inspire'],
            'learning': ['learn', 'education', 'knowledge', 'study', 'research'],
            'adventure': ['adventure', 'journey', 'travel', 'explore', 'quest']
        }
        
        for theme_name, keywords in theme_keywords.items():
            for keyword in keywords:
                if keyword in analysis_lower:
                    themes.append(Theme(
                        name=theme_name,
                        confidence=0.7,  # Claude analysis gets higher confidence
                        keywords=[keyword],
                        category='claude_extracted'
                    ))
                    break  # Only add each theme once
        
        # Create emotional profile
        emotional_profile = EmotionalProfile(
            primary_emotion=primary_emotion,
            secondary_emotions=[],  # Could extract these too
            intensity=intensity,
            confidence=0.9  # High confidence for Claude analysis
        )
        
        # Extract musical suggestions
        musical_suggestions = {
            'key': 'C major',  # Could extract from Claude's analysis
            'tempo': 'moderato',
            'style': 'classical',
            'complexity_level': 'medium'
        }
        
        # Look for key suggestions in Claude's response
        if 'minor' in analysis_lower:
            musical_suggestions['key'] = 'A minor'
        
        if any(word in analysis_lower for word in ['fast', 'quick', 'energetic']):
            musical_suggestions['tempo'] = 'allegro'
        elif any(word in analysis_lower for word in ['slow', 'calm', 'peaceful']):
            musical_suggestions['tempo'] = 'adagio'
        
        # Structure analysis
        structure = {
            'content_type': 'claude_analyzed',
            'length': len(original_content.split()),
            'complexity': 'medium',
            'claude_enhanced': True
        }
        
        return ContentAnalysis(
            content=original_content,
            emotional_profile=emotional_profile,
            themes=themes,
            structure=structure,
            musical_suggestions=musical_suggestions
        )
    
    def _merge_analyses(self, existing: ContentAnalysis, claude_analysis: ContentAnalysis) -> ContentAnalysis:
        """Merge existing analysis with Claude's enhanced analysis"""
        
        # Use Claude's emotional analysis if it has higher confidence
        if claude_analysis.emotional_profile.confidence > existing.emotional_profile.confidence:
            emotional_profile = claude_analysis.emotional_profile
        else:
            emotional_profile = existing.emotional_profile
        
        # Combine themes
        all_themes = existing.themes + claude_analysis.themes
        # Remove duplicates and keep highest confidence
        unique_themes = {}
        for theme in all_themes:
            if theme.name not in unique_themes or theme.confidence > unique_themes[theme.name].confidence:
                unique_themes[theme.name] = theme
        
        themes = list(unique_themes.values())
        
        # Merge musical suggestions
        musical_suggestions = existing.musical_suggestions.copy()
        musical_suggestions.update(claude_analysis.musical_suggestions)
        musical_suggestions['claude_enhanced'] = True
        
        # Merge structure
        structure = existing.structure.copy()
        structure.update(claude_analysis.structure)
        
        return ContentAnalysis(
            content=existing.content,
            emotional_profile=emotional_profile,
            themes=themes,
            structure=structure,
            musical_suggestions=musical_suggestions
        )
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this block"""
        return {
            'name': 'Claude AI Content Analyzer',
            'type': 'ai_analyzer',
            'capabilities': self.capabilities,
            'model': self.model,
            'available': ANTHROPIC_AVAILABLE
        }
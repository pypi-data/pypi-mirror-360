#!/usr/bin/env python3
"""
🧠 ChatGPT Block - Content Analysis and Creative Enhancement
Sophisticated content understanding and creative music generation guidance

Provides intelligent content analysis using OpenAI's ChatGPT API.
"""

import os
import json
from typing import Dict, Any, Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ...core.analyzer import ContentAnalysis, EmotionalProfile, Theme, Emotion

class ChatGPTBlock:
    """
    🧠 ChatGPT AI content analysis and creative guidance block
    
    Provides sophisticated content understanding and creative suggestions
    for music generation enhancement.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = self.config.get('chatgpt_model', 'gpt-4')
        
        self.capabilities = [
            'creative_analysis',
            'narrative_understanding',
            'cultural_context',
            'emotional_intelligence',
            'musical_creativity',
            'style_suggestions'
        ]
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🎨 Enhanced content analysis using ChatGPT
        
        Args:
            data: Pipeline data containing extracted content
            
        Returns:
            Dict: Enhanced analysis data with creative insights
        """
        extracted_content = data.get('extracted_content')
        if not extracted_content:
            return data
        
        try:
            # Get creative analysis from ChatGPT
            enhanced_analysis = self._analyze_with_chatgpt(extracted_content.content)
            
            # Merge with existing analysis or replace
            if 'content_analysis' in data:
                # Enhance existing analysis
                existing = data['content_analysis']
                enhanced_analysis = self._merge_analyses(existing, enhanced_analysis)
            
            data['content_analysis'] = enhanced_analysis
            data['chatgpt_enhanced'] = True
            
            return data
            
        except Exception as e:
            # Fallback: return original data
            print(f"ChatGPT analysis failed: {e}")
            return data
    
    def _analyze_with_chatgpt(self, content: str) -> ContentAnalysis:
        """Analyze content using ChatGPT API"""
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(content)
        
        # Call ChatGPT API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative AI assistant specializing in analyzing content for musical composition. Provide detailed, structured analysis that helps create emotionally resonant music."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        # Parse ChatGPT's response
        analysis_text = response.choices[0].message.content
        
        # Convert to ContentAnalysis object
        return self._parse_chatgpt_response(analysis_text, content)
    
    def _build_analysis_prompt(self, content: str) -> str:
        """Build analysis prompt for ChatGPT"""
        
        # Check for custom prompts
        custom_prompts = self.config.get('prompts', {})
        if 'chatgpt_analysis' in custom_prompts:
            return custom_prompts['chatgpt_analysis'].format(content=content)
        
        # Default creative analysis prompt
        return f"""Analyze the following content for musical composition, focusing on creative and emotional elements. Provide a comprehensive analysis covering:

1. EMOTIONAL JOURNEY:
   - Primary emotion and emotional arc throughout the content
   - Emotional intensity (0.0 to 1.0) and how it evolves
   - Secondary emotions and their interplay
   - Emotional transitions and peaks

2. CREATIVE THEMES:
   - Main themes, concepts, and ideas
   - Symbolic elements and metaphors
   - Cultural references and context
   - Narrative structure and storytelling elements

3. MUSICAL INSPIRATION:
   - Suggested musical genre and style
   - Appropriate key, mode, and harmonic approach
   - Tempo and rhythm suggestions
   - Instrumentation recommendations
   - Dynamic and expressive markings

4. CREATIVE DIRECTION:
   - Overall musical character and personality
   - Structural suggestions (verse/chorus, movements, etc.)
   - Special techniques or effects to consider
   - How to translate the content's essence into music

5. ARTISTIC INTERPRETATION:
   - Multiple creative approaches possible
   - Innovative musical interpretations
   - Ways to surprise and engage listeners
   - Connection between content meaning and musical expression

Please provide specific, actionable insights that will guide the creation of meaningful, emotionally connected music.

CONTENT TO ANALYZE:
{content}

ANALYSIS:"""
    
    def _parse_chatgpt_response(self, analysis_text: str, original_content: str) -> ContentAnalysis:
        """Parse ChatGPT's analysis into ContentAnalysis object"""
        
        # Enhanced parsing with creative insights
        
        # Extract emotion with creative understanding
        emotion_map = {
            'joy': Emotion.JOY, 'happiness': Emotion.JOY, 'delight': Emotion.JOY,
            'elation': Emotion.JOY, 'bliss': Emotion.JOY, 'euphoria': Emotion.JOY,
            'sadness': Emotion.SADNESS, 'sorrow': Emotion.SADNESS, 'grief': Emotion.SADNESS,
            'melancholy': Emotion.MELANCHOLY, 'melancholic': Emotion.MELANCHOLY,
            'wistful': Emotion.MELANCHOLY, 'nostalgic': Emotion.MELANCHOLY,
            'contemplation': Emotion.CONTEMPLATION, 'thoughtful': Emotion.CONTEMPLATION,
            'reflective': Emotion.CONTEMPLATION, 'meditative': Emotion.CONTEMPLATION,
            'excitement': Emotion.EXCITEMENT, 'thrilling': Emotion.EXCITEMENT,
            'exhilarating': Emotion.EXCITEMENT, 'energetic': Emotion.EXCITEMENT,
            'peace': Emotion.PEACE, 'peaceful': Emotion.PEACE, 'serene': Emotion.PEACE,
            'tranquil': Emotion.PEACE, 'calm': Emotion.PEACE, 'restful': Emotion.PEACE,
            'anger': Emotion.ANGER, 'rage': Emotion.ANGER, 'fury': Emotion.ANGER,
            'fear': Emotion.FEAR, 'anxiety': Emotion.FEAR, 'terror': Emotion.FEAR,
            'love': Emotion.LOVE, 'affection': Emotion.LOVE, 'tenderness': Emotion.LOVE,
            'curiosity': Emotion.CURIOSITY, 'wonder': Emotion.CURIOSITY, 'intrigue': Emotion.CURIOSITY
        }
        
        # Find primary emotion with creative context
        primary_emotion = Emotion.CONTEMPLATION  # default
        analysis_lower = analysis_text.lower()
        
        emotion_scores = {}
        for word, emotion in emotion_map.items():
            if word in analysis_lower:
                # Count occurrences for better emotion detection
                count = analysis_lower.count(word)
                if emotion in emotion_scores:
                    emotion_scores[emotion] += count
                else:
                    emotion_scores[emotion] = count
        
        if emotion_scores:
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
        
        # Extract intensity with creative nuance
        intensity = 0.6  # default for creative content
        import re
        
        # Look for intensity indicators
        intensity_words = {
            'subtle': 0.3, 'gentle': 0.4, 'moderate': 0.5,
            'strong': 0.7, 'intense': 0.8, 'overwhelming': 0.9,
            'powerful': 0.8, 'dramatic': 0.9, 'explosive': 1.0
        }
        
        for word, value in intensity_words.items():
            if word in analysis_lower:
                intensity = max(intensity, value)
        
        # Look for numerical intensity values
        intensity_matches = re.findall(r'intensity[:\s]*([0-9.]+)', analysis_lower)
        if intensity_matches:
            try:
                extracted_intensity = float(intensity_matches[0])
                if 0.0 <= extracted_intensity <= 1.0:
                    intensity = extracted_intensity
                elif extracted_intensity <= 10.0:  # Scale 1-10 to 0-1
                    intensity = extracted_intensity / 10.0
            except ValueError:
                pass
        
        # Extract themes with creative categorization
        themes = []
        creative_themes = {
            'storytelling': ['story', 'narrative', 'tale', 'plot', 'character'],
            'technology': ['technology', 'digital', 'ai', 'computer', 'innovation'],
            'nature': ['nature', 'environment', 'earth', 'organic', 'natural'],
            'relationships': ['relationship', 'connection', 'bond', 'family', 'friendship'],
            'creativity': ['creative', 'artistic', 'imagination', 'inspiration', 'expression'],
            'adventure': ['adventure', 'journey', 'quest', 'exploration', 'discovery'],
            'mystery': ['mystery', 'unknown', 'enigma', 'secrets', 'hidden'],
            'transformation': ['change', 'growth', 'evolution', 'metamorphosis', 'development'],
            'conflict': ['conflict', 'struggle', 'tension', 'challenge', 'opposition'],
            'harmony': ['harmony', 'balance', 'unity', 'cooperation', 'peace'],
            'time': ['time', 'memory', 'past', 'future', 'temporal', 'eternal'],
            'spirituality': ['spiritual', 'divine', 'sacred', 'transcendent', 'mystical']
        }
        
        for theme_name, keywords in creative_themes.items():
            theme_confidence = 0
            found_keywords = []
            
            for keyword in keywords:
                if keyword in analysis_lower:
                    theme_confidence += 0.2
                    found_keywords.append(keyword)
            
            if theme_confidence > 0:
                # Cap confidence at 0.9 for ChatGPT analysis
                theme_confidence = min(0.9, theme_confidence)
                themes.append(Theme(
                    name=theme_name,
                    confidence=theme_confidence,
                    keywords=found_keywords,
                    category='chatgpt_creative'
                ))
        
        # Create emotional profile
        emotional_profile = EmotionalProfile(
            primary_emotion=primary_emotion,
            secondary_emotions=[],  # Could extract these with more sophisticated parsing
            intensity=intensity,
            confidence=0.85  # High confidence for ChatGPT creative analysis
        )
        
        # Extract musical suggestions with creative interpretation
        musical_suggestions = {
            'genre': 'classical',
            'key': 'C major',
            'tempo': 'moderato',
            'style': 'expressive',
            'complexity_level': 'medium',
            'creative_approach': 'narrative'
        }
        
        # Parse genre suggestions
        genre_indicators = {
            'classical': ['classical', 'orchestral', 'symphony'],
            'jazz': ['jazz', 'improvisation', 'syncopated'],
            'folk': ['folk', 'traditional', 'acoustic', 'simple'],
            'contemporary': ['modern', 'contemporary', 'innovative'],
            'cinematic': ['cinematic', 'dramatic', 'film', 'epic'],
            'ambient': ['ambient', 'atmospheric', 'ethereal'],
            'electronic': ['electronic', 'digital', 'synthetic']
        }
        
        for genre, indicators in genre_indicators.items():
            if any(word in analysis_lower for word in indicators):
                musical_suggestions['genre'] = genre
                break
        
        # Parse key suggestions
        if any(word in analysis_lower for word in ['dark', 'minor', 'sad', 'melancholy']):
            musical_suggestions['key'] = 'A minor'
        elif any(word in analysis_lower for word in ['bright', 'major', 'happy', 'joyful']):
            musical_suggestions['key'] = 'C major'
        
        # Parse tempo suggestions
        tempo_indicators = {
            'adagio': ['slow', 'peaceful', 'meditative', 'calm'],
            'andante': ['walking', 'steady', 'moderate'],
            'allegro': ['fast', 'energetic', 'lively', 'exciting'],
            'presto': ['very fast', 'frantic', 'urgent', 'explosive']
        }
        
        for tempo, indicators in tempo_indicators.items():
            if any(word in analysis_lower for word in indicators):
                musical_suggestions['tempo'] = tempo
                break
        
        # Creative approach suggestions
        if any(word in analysis_lower for word in ['story', 'narrative', 'journey']):
            musical_suggestions['creative_approach'] = 'narrative'
        elif any(word in analysis_lower for word in ['abstract', 'impressionist', 'atmospheric']):
            musical_suggestions['creative_approach'] = 'impressionistic'
        elif any(word in analysis_lower for word in ['dramatic', 'theatrical', 'cinematic']):
            musical_suggestions['creative_approach'] = 'dramatic'
        
        # Structure analysis with creative insights
        structure = {
            'content_type': 'chatgpt_creative',
            'length': len(original_content.split()),
            'complexity': 'medium',
            'creative_elements': themes,
            'chatgpt_enhanced': True,
            'narrative_structure': 'detected' if 'story' in analysis_lower else 'abstract'
        }
        
        return ContentAnalysis(
            content=original_content,
            emotional_profile=emotional_profile,
            themes=themes,
            structure=structure,
            musical_suggestions=musical_suggestions
        )
    
    def _merge_analyses(self, existing: ContentAnalysis, chatgpt_analysis: ContentAnalysis) -> ContentAnalysis:
        """Merge existing analysis with ChatGPT's creative analysis"""
        
        # Use ChatGPT's emotional analysis if it has higher confidence
        if chatgpt_analysis.emotional_profile.confidence > existing.emotional_profile.confidence:
            emotional_profile = chatgpt_analysis.emotional_profile
        else:
            emotional_profile = existing.emotional_profile
        
        # Combine themes, prioritizing creative insights
        all_themes = existing.themes + chatgpt_analysis.themes
        # Remove duplicates and keep highest confidence
        unique_themes = {}
        for theme in all_themes:
            if theme.name not in unique_themes or theme.confidence > unique_themes[theme.name].confidence:
                unique_themes[theme.name] = theme
        
        themes = list(unique_themes.values())
        
        # Merge musical suggestions with creative enhancement
        musical_suggestions = existing.musical_suggestions.copy()
        musical_suggestions.update(chatgpt_analysis.musical_suggestions)
        musical_suggestions['chatgpt_enhanced'] = True
        
        # Merge structure with creative elements
        structure = existing.structure.copy()
        structure.update(chatgpt_analysis.structure)
        
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
            'name': 'ChatGPT Creative Analyzer',
            'type': 'ai_analyzer',
            'capabilities': self.capabilities,
            'model': self.model,
            'available': OPENAI_AVAILABLE
        }
#!/usr/bin/env python3
"""
🧠 LinkTune Content Analyzer
Emotional and thematic analysis for music generation

Simplified version of the G.Music Assembly content analyzer.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class Emotion(Enum):
    """Core emotions mapped to musical elements"""
    JOY = "joy"
    SADNESS = "sadness" 
    CONTEMPLATION = "contemplation"
    EXCITEMENT = "excitement"
    PEACE = "peace"
    ANGER = "anger"
    FEAR = "fear"
    LOVE = "love"
    CURIOSITY = "curiosity"
    MELANCHOLY = "melancholy"

@dataclass
class EmotionalProfile:
    """Emotional analysis of content"""
    primary_emotion: Emotion
    secondary_emotions: List[Emotion]
    intensity: float  # 0.0 to 1.0
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'primary_emotion': self.primary_emotion.value,
            'secondary_emotions': [e.value for e in self.secondary_emotions],
            'intensity': self.intensity,
            'confidence': self.confidence
        }

@dataclass
class Theme:
    """Thematic content analysis"""
    name: str
    confidence: float
    keywords: List[str]
    category: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'confidence': self.confidence, 
            'keywords': self.keywords,
            'category': self.category
        }

@dataclass
class ContentAnalysis:
    """Complete content analysis for music generation"""
    content: str
    emotional_profile: EmotionalProfile
    themes: List[Theme]
    structure: Dict[str, Any]
    musical_suggestions: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'content': self.content,
            'emotional_profile': self.emotional_profile.to_dict(),
            'themes': [theme.to_dict() for theme in self.themes],
            'structure': self.structure,
            'musical_suggestions': self.musical_suggestions
        }

class ContentAnalyzer:
    """
    🧠 Analyze content for emotional and thematic elements
    
    Maps text content to musical parameters for generation.
    """
    
    def __init__(self):
        # Emotion keyword mappings
        self.emotion_keywords = {
            Emotion.JOY: [
                'happy', 'joy', 'excited', 'celebration', 'wonderful', 'amazing', 
                'fantastic', 'delighted', 'cheerful', 'upbeat', 'positive', 'smile',
                'laugh', 'fun', 'great', 'excellent', 'brilliant', 'awesome'
            ],
            Emotion.SADNESS: [
                'sad', 'cry', 'tears', 'lonely', 'depressed', 'sorrow', 'grief',
                'mourning', 'loss', 'heartbreak', 'disappointed', 'upset', 'down'
            ],
            Emotion.CONTEMPLATION: [
                'think', 'reflect', 'consider', 'ponder', 'meditate', 'wonder',
                'philosophy', 'deep', 'meaning', 'purpose', 'understand', 'analyze'
            ],
            Emotion.EXCITEMENT: [
                'exciting', 'thrilling', 'amazing', 'incredible', 'adventure',
                'action', 'energy', 'dynamic', 'powerful', 'intense', 'rush'
            ],
            Emotion.PEACE: [
                'calm', 'peaceful', 'serene', 'quiet', 'gentle', 'soft', 'tranquil',
                'relaxed', 'still', 'harmony', 'balance', 'zen', 'meditation'
            ],
            Emotion.LOVE: [
                'love', 'heart', 'romance', 'passion', 'devotion', 'care', 'affection',
                'relationship', 'family', 'friend', 'connection', 'bond'
            ],
            Emotion.CURIOSITY: [
                'curious', 'question', 'explore', 'discover', 'learn', 'research',
                'investigate', 'mystery', 'unknown', 'wonder', 'search'
            ],
            Emotion.MELANCHOLY: [
                'melancholy', 'nostalgic', 'bittersweet', 'wistful', 'longing',
                'memory', 'past', 'regret', 'missing', 'distant', 'fading'
            ]
        }
        
        # Musical style mappings
        self.style_keywords = {
            'classical': ['elegant', 'sophisticated', 'formal', 'structured', 'traditional'],
            'jazz': ['smooth', 'improvisation', 'swing', 'blues', 'syncopated'],
            'folk': ['simple', 'story', 'tradition', 'acoustic', 'rural', 'natural'],
            'electronic': ['modern', 'digital', 'synthetic', 'futuristic', 'tech'],
            'ambient': ['atmospheric', 'space', 'floating', 'ethereal', 'background'],
            'rock': ['energy', 'power', 'drive', 'loud', 'aggressive', 'strong'],
            'celtic': ['mystical', 'ancient', 'nature', 'spiritual', 'flowing']
        }
        
        # Tempo mappings based on content characteristics
        self.tempo_indicators = {
            'fast': ['quick', 'rapid', 'rush', 'speed', 'urgent', 'active', 'busy'],
            'slow': ['slow', 'calm', 'gentle', 'peaceful', 'relaxed', 'still'],
            'moderate': ['steady', 'walking', 'moderate', 'balanced', 'regular']
        }
    
    def analyze_content(self, content: str) -> ContentAnalysis:
        """
        🎯 Analyze content for musical generation
        
        Args:
            content: Text content to analyze
            
        Returns:
            ContentAnalysis: Complete analysis with emotional and thematic data
        """
        # Clean and prepare content
        cleaned_content = self._clean_content(content)
        
        # Analyze emotions
        emotional_profile = self._analyze_emotions(cleaned_content)
        
        # Extract themes
        themes = self._extract_themes(cleaned_content)
        
        # Analyze structure
        structure = self._analyze_structure(cleaned_content)
        
        # Generate musical suggestions
        musical_suggestions = self._generate_musical_suggestions(
            emotional_profile, themes, structure
        )
        
        return ContentAnalysis(
            content=content,
            emotional_profile=emotional_profile,
            themes=themes,
            structure=structure,
            musical_suggestions=musical_suggestions
        )
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content for analysis"""
        # Remove extra whitespace and normalize
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Convert to lowercase for analysis
        return content.lower()
    
    def _analyze_emotions(self, content: str) -> EmotionalProfile:
        """Analyze emotional content using keyword matching"""
        emotion_scores = {}
        
        # Score each emotion based on keyword presence
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                # Count occurrences with word boundaries
                matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content))
                if matches > 0:
                    score += matches
                    found_keywords.append(keyword)
            
            if score > 0:
                emotion_scores[emotion] = {
                    'score': score,
                    'keywords': found_keywords
                }
        
        # Determine primary and secondary emotions
        if emotion_scores:
            sorted_emotions = sorted(
                emotion_scores.items(), 
                key=lambda x: x[1]['score'], 
                reverse=True
            )
            
            primary_emotion = sorted_emotions[0][0]
            secondary_emotions = [e[0] for e in sorted_emotions[1:3]]
            
            # Calculate intensity based on keyword density
            total_words = len(content.split())
            total_emotion_score = sum(e['score'] for e in emotion_scores.values())
            intensity = min(total_emotion_score / max(total_words, 1) * 10, 1.0)
            
            # Simple confidence based on number of emotion keywords found
            confidence = min(len(emotion_scores) / 5.0, 1.0)
        else:
            # Default to neutral emotions
            primary_emotion = Emotion.CONTEMPLATION
            secondary_emotions = []
            intensity = 0.5
            confidence = 0.3
        
        return EmotionalProfile(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            intensity=intensity,
            confidence=confidence
        )
    
    def _extract_themes(self, content: str) -> List[Theme]:
        """Extract thematic content"""
        themes = []
        
        # Simple theme detection based on content patterns
        theme_patterns = {
            'technology': [
                'computer', 'software', 'ai', 'artificial intelligence', 'tech',
                'digital', 'internet', 'code', 'programming', 'algorithm'
            ],
            'nature': [
                'nature', 'forest', 'tree', 'flower', 'animal', 'bird', 'ocean',
                'mountain', 'sky', 'earth', 'natural', 'environment'
            ],
            'relationships': [
                'relationship', 'family', 'friend', 'love', 'partner', 'parent',
                'child', 'community', 'social', 'connection', 'bond'
            ],
            'creativity': [
                'creative', 'art', 'music', 'write', 'paint', 'design', 'imagine',
                'inspiration', 'expression', 'artistic', 'craft'
            ],
            'learning': [
                'learn', 'study', 'education', 'knowledge', 'understand', 'teach',
                'school', 'research', 'discover', 'explore', 'science'
            ],
            'adventure': [
                'adventure', 'journey', 'travel', 'explore', 'discover', 'quest',
                'expedition', 'voyage', 'path', 'destination', 'experience'
            ]
        }
        
        for theme_name, keywords in theme_patterns.items():
            score = 0
            found_keywords = []
            
            for keyword in keywords:
                matches = len(re.findall(r'\b' + re.escape(keyword) + r'\b', content))
                if matches > 0:
                    score += matches
                    found_keywords.append(keyword)
            
            if score > 0:
                total_words = len(content.split())
                confidence = min(score / max(total_words, 1) * 20, 1.0)
                
                themes.append(Theme(
                    name=theme_name,
                    confidence=confidence,
                    keywords=found_keywords,
                    category='content_theme'
                ))
        
        # Sort by confidence
        themes.sort(key=lambda t: t.confidence, reverse=True)
        
        return themes[:5]  # Return top 5 themes
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        # Simple complexity assessment
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        if avg_sentence_length < 10:
            complexity = 'simple'
        elif avg_sentence_length < 20:
            complexity = 'medium'
        else:
            complexity = 'complex'
        
        # Content type detection
        content_type = 'general'
        if '?' in content:
            content_type = 'conversation' if content.count('?') > 2 else 'inquiry'
        elif content.count('\n') > 5:
            content_type = 'structured'
        elif any(word in content for word in ['once', 'story', 'narrative']):
            content_type = 'story'
        
        return {
            'content_type': content_type,
            'length': len(words),
            'complexity': complexity,
            'sentence_count': len(sentences),
            'avg_sentence_length': avg_sentence_length
        }
    
    def _generate_musical_suggestions(self, emotional_profile: EmotionalProfile, 
                                    themes: List[Theme], structure: Dict[str, Any]) -> Dict[str, Any]:
        """Generate musical suggestions based on analysis"""
        
        # Map emotion to musical parameters
        emotion_mappings = {
            Emotion.JOY: {'key': 'C major', 'tempo': 'allegro', 'mode': 'major'},
            Emotion.SADNESS: {'key': 'D minor', 'tempo': 'adagio', 'mode': 'minor'},
            Emotion.CONTEMPLATION: {'key': 'F major', 'tempo': 'andante', 'mode': 'major'},
            Emotion.EXCITEMENT: {'key': 'E major', 'tempo': 'presto', 'mode': 'major'},
            Emotion.PEACE: {'key': 'G major', 'tempo': 'largo', 'mode': 'major'},
            Emotion.LOVE: {'key': 'A major', 'tempo': 'moderato', 'mode': 'major'},
            Emotion.MELANCHOLY: {'key': 'B minor', 'tempo': 'andante', 'mode': 'minor'},
        }
        
        primary_emotion = emotional_profile.primary_emotion
        base_params = emotion_mappings.get(primary_emotion, {
            'key': 'C major', 'tempo': 'moderato', 'mode': 'major'
        })
        
        # Suggest musical style based on themes
        suggested_style = 'classical'  # default
        for theme in themes:
            if theme.name in ['technology', 'digital']:
                suggested_style = 'electronic'
                break
            elif theme.name in ['nature', 'environment']:
                suggested_style = 'celtic'
                break
            elif theme.name in ['relationships', 'love']:
                suggested_style = 'folk'
                break
        
        # Adjust tempo based on intensity
        tempo_modifier = emotional_profile.intensity
        if tempo_modifier > 0.7:
            tempo_adjustment = 'faster'
        elif tempo_modifier < 0.3:
            tempo_adjustment = 'slower'
        else:
            tempo_adjustment = 'standard'
        
        return {
            'key': base_params.get('key', 'C major'),
            'tempo': base_params.get('tempo', 'moderato'),
            'mode': base_params.get('mode', 'major'),
            'style': suggested_style,
            'tempo_adjustment': tempo_adjustment,
            'intensity': emotional_profile.intensity,
            'recommended_length': min(32, max(8, structure['length'] // 10)),  # measures
            'complexity_level': structure['complexity']
        }
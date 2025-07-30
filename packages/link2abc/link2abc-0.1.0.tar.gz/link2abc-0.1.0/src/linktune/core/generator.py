#!/usr/bin/env python3
"""
🎵 LinkTune Music Generator
Rule-based ABC notation generation for core functionality

Simplified version of the G.Music Assembly generator system.
"""

import random
from typing import Dict, List, Any, Optional
from .analyzer import ContentAnalysis, Emotion

class MusicGenerator:
    """
    🎵 Generate ABC notation from content analysis
    
    Rule-based music generation for reliable core functionality.
    Can be enhanced with AI blocks for professional composition.
    """
    
    def __init__(self):
        # Musical building blocks
        self.scales = {
            'C major': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
            'G major': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
            'D major': ['D', 'E', 'F#', 'G', 'A', 'B', 'C#'],
            'A major': ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#'],
            'E major': ['E', 'F#', 'G#', 'A', 'B', 'C#', 'D#'],
            'F major': ['F', 'G', 'A', 'Bb', 'C', 'D', 'E'],
            'Bb major': ['Bb', 'C', 'D', 'Eb', 'F', 'G', 'A'],
            'A minor': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
            'E minor': ['E', 'F#', 'G', 'A', 'B', 'C', 'D'],
            'B minor': ['B', 'C#', 'D', 'E', 'F#', 'G', 'A'],
            'F# minor': ['F#', 'G#', 'A', 'B', 'C#', 'D', 'E'],
            'D minor': ['D', 'E', 'F', 'G', 'A', 'Bb', 'C'],
            'G minor': ['G', 'A', 'Bb', 'C', 'D', 'Eb', 'F'],
        }
        
        # Emotional pattern templates
        self.emotional_patterns = {
            Emotion.JOY: {
                'intervals': [1, 3, 5, 1, 5, 3, 1],  # Upward, bright
                'rhythm': ['2', '1', '1', '2', '1', '1', '2'],
                'dynamics': 'forte'
            },
            Emotion.SADNESS: {
                'intervals': [1, 3, 2, 1, 6, 5, 1],  # Downward, minor
                'rhythm': ['4', '2', '2', '4', '2', '2', '4'],
                'dynamics': 'piano'
            },
            Emotion.CONTEMPLATION: {
                'intervals': [1, 5, 4, 3, 2, 3, 1],  # Thoughtful, flowing
                'rhythm': ['2', '2', '2', '2', '2', '2', '4'],
                'dynamics': 'mezzo-piano'
            },
            Emotion.EXCITEMENT: {
                'intervals': [1, 3, 5, 7, 8, 5, 1],  # Energetic, ascending
                'rhythm': ['1', '1', '1', '1', '1', '1', '2'],
                'dynamics': 'fortissimo'
            },
            Emotion.PEACE: {
                'intervals': [1, 3, 5, 3, 1, 5, 1],  # Gentle, stable
                'rhythm': ['4', '4', '4', '4', '4', '4', '8'],
                'dynamics': 'pianissimo'
            },
            Emotion.LOVE: {
                'intervals': [1, 3, 5, 6, 5, 3, 1],  # Warm, embracing
                'rhythm': ['2', '2', '4', '2', '2', '2', '4'],
                'dynamics': 'dolce'
            }
        }
        
        # Tempo mappings
        self.tempo_bpm = {
            'largo': 40,
            'adagio': 60,
            'andante': 80,
            'moderato': 100,
            'allegro': 120,
            'presto': 160
        }
        
        # Time signatures for different styles
        self.time_signatures = {
            'simple': '4/4',
            'flowing': '3/4',
            'complex': '7/8',
            'dance': '2/4'
        }
    
    def generate_abc(self, analysis: ContentAnalysis, config: Optional[Dict[str, Any]] = None) -> str:
        """
        🎵 Generate ABC notation from content analysis
        
        Args:
            analysis: Content analysis with emotional and thematic data
            config: Optional configuration overrides
            
        Returns:
            str: ABC notation for the generated melody
        """
        config = config or {}
        
        # Get musical parameters
        suggestions = analysis.musical_suggestions
        key = config.get('key', suggestions.get('key', 'C major'))
        tempo = config.get('tempo', suggestions.get('tempo', 'moderato'))
        length = config.get('length', suggestions.get('recommended_length', 16))
        
        # Generate title
        title = self._generate_title(analysis)
        
        # Get scale for the key
        scale = self.scales.get(key, self.scales['C major'])
        
        # Get emotional pattern
        emotion_pattern = self.emotional_patterns.get(
            analysis.emotional_profile.primary_emotion,
            self.emotional_patterns[Emotion.CONTEMPLATION]
        )
        
        # Generate melody
        melody = self._generate_melody(
            scale, emotion_pattern, length, analysis.emotional_profile.intensity
        )
        
        # Build ABC notation
        abc_notation = self._build_abc_notation(
            title, key, tempo, melody, analysis
        )
        
        return abc_notation
    
    def _generate_title(self, analysis: ContentAnalysis) -> str:
        """Generate a title for the composition"""
        emotion = analysis.emotional_profile.primary_emotion.value.title()
        
        if analysis.themes:
            main_theme = analysis.themes[0].name.replace('_', ' ').title()
            return f"{emotion} {main_theme}"
        else:
            return f"{emotion} Melody"
    
    def _generate_melody(self, scale: List[str], pattern: Dict[str, Any], 
                        length: int, intensity: float) -> List[Dict[str, Any]]:
        """Generate melody notes based on emotional pattern"""
        melody = []
        base_intervals = pattern['intervals']
        base_rhythms = pattern['rhythm']
        
        # Adjust intensity
        octave_modifier = int(intensity * 2)  # 0-2 octave range
        
        for i in range(length):
            # Select interval and rhythm cyclically
            interval_idx = base_intervals[i % len(base_intervals)] - 1  # Convert to 0-based
            rhythm = base_rhythms[i % len(base_rhythms)]
            
            # Get note from scale
            note_idx = interval_idx % len(scale)
            note = scale[note_idx]
            
            # Add octave if needed
            if octave_modifier > 0 and interval_idx >= len(scale):
                note = note.lower()  # Lower case indicates higher octave
            
            # Add some variation
            if random.random() < 0.1:  # 10% chance of variation
                # Neighbor tone
                if note_idx > 0 and random.random() < 0.5:
                    note = scale[note_idx - 1]
                elif note_idx < len(scale) - 1:
                    note = scale[note_idx + 1]
            
            melody.append({
                'note': note,
                'rhythm': rhythm
            })
        
        return melody
    
    def _build_abc_notation(self, title: str, key: str, tempo: str, 
                          melody: List[Dict[str, Any]], analysis: ContentAnalysis) -> str:
        """Build complete ABC notation"""
        
        # Get tempo BPM
        tempo_bpm = self.tempo_bpm.get(tempo, 100)
        
        # Get time signature
        complexity = analysis.structure.get('complexity', 'simple')
        time_sig = self.time_signatures.get(complexity, '4/4')
        
        # Build header
        abc_lines = [
            "X:1",
            f"T:{title}",
            f"C:LinkTune Generated - {analysis.emotional_profile.primary_emotion.value.title()}",
            f"M:{time_sig}",
            "L:1/8",
            f"Q:1/4={tempo_bpm}",
            f"K:{key}",
            f"% Generated from content analysis",
            f"% Primary emotion: {analysis.emotional_profile.primary_emotion.value}",
            f"% Intensity: {analysis.emotional_profile.intensity:.2f}",
            f"% Themes: {', '.join([t.name for t in analysis.themes[:3]])}",
            ""
        ]
        
        # Build melody line
        melody_line = "|: "
        measure_count = 0
        beat_count = 0
        
        for note_data in melody:
            note = note_data['note']
            rhythm = note_data['rhythm']
            
            melody_line += note + rhythm + " "
            
            # Track beats (assuming 4/4 time)
            beat_count += int(rhythm)
            if beat_count >= 8:  # 8 eighth notes = 1 measure in 4/4
                beat_count = 0
                measure_count += 1
                
                # Add bar lines every 4 measures for readability
                if measure_count % 4 == 0:
                    melody_line += "|\n"
                    if measure_count < len(melody) // 8:  # Not the last line
                        melody_line += ""
        
        # Close the repeat and add final bar
        melody_line += " :|"
        
        abc_lines.append(melody_line)
        
        # Add musical structure for longer pieces
        if len(melody) > 16:
            abc_lines.append("")
            abc_lines.append("% Variation")
            variation = self._generate_variation(melody, key)
            abc_lines.append(variation)
        
        # Add metadata footer
        abc_lines.extend([
            "",
            f"% Content Analysis Summary:",
            f"% - Emotional intensity: {analysis.emotional_profile.intensity:.2f}",
            f"% - Content length: {analysis.structure.get('length', 0)} words",
            f"% - Complexity: {analysis.structure.get('complexity', 'unknown')}",
            f"% - Generated by LinkTune Core Engine"
        ])
        
        return "\n".join(abc_lines)
    
    def _generate_variation(self, original_melody: List[Dict[str, Any]], key: str) -> str:
        """Generate a variation of the melody"""
        scale = self.scales.get(key, self.scales['C major'])
        variation_line = "|: "
        
        # Create variation by inverting intervals and changing rhythm
        for i, note_data in enumerate(original_melody[:8]):  # Take first 8 notes
            original_note = note_data['note']
            
            # Find original note in scale
            try:
                note_idx = scale.index(original_note)
                # Invert around the tonic (simple inversion)
                inverted_idx = len(scale) - 1 - note_idx
                if inverted_idx < 0:
                    inverted_idx = 0
                elif inverted_idx >= len(scale):
                    inverted_idx = len(scale) - 1
                
                new_note = scale[inverted_idx]
            except ValueError:
                # If note not found, use original
                new_note = original_note
            
            # Vary rhythm slightly
            original_rhythm = note_data['rhythm']
            if original_rhythm == '2':
                new_rhythm = '1' if random.random() < 0.3 else '2'
            elif original_rhythm == '1':
                new_rhythm = '2' if random.random() < 0.3 else '1'
            else:
                new_rhythm = original_rhythm
            
            variation_line += new_note + new_rhythm + " "
        
        variation_line += " :|"
        return variation_line
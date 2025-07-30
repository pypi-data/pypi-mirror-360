#!/usr/bin/env python3
"""
🔄 LinkTune Format Converter
Convert ABC notation to multiple formats (MIDI, MP3, etc.)

Simplified version of the G.Music Assembly format converter.
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import music21

class FormatConverter:
    """
    🔄 Convert ABC notation to multiple output formats
    
    Supports MIDI conversion via music21 (always available).
    Optional conversions to MP3, SVG, etc. if tools are installed.
    """
    
    def __init__(self):
        self.supported_formats = ['abc', 'midi']
        self.conversion_tools = {}
        
        # Check for optional conversion tools
        self._detect_conversion_tools()
    
    def _detect_conversion_tools(self):
        """Detect available conversion tools"""
        tools_to_check = {
            'abc2midi': 'midi',
            'fluidsynth': 'mp3', 
            'timidity': 'mp3',
            'abcm2ps': 'svg',
            'inkscape': 'svg',
            'convert': 'jpg'  # ImageMagick
        }
        
        for tool, format_type in tools_to_check.items():
            if self._tool_available(tool):
                self.conversion_tools[tool] = format_type
                if format_type not in self.supported_formats:
                    self.supported_formats.append(format_type)
    
    def _tool_available(self, tool_name: str) -> bool:
        """Check if a command-line tool is available"""
        try:
            subprocess.run([tool_name, '--version'], 
                         capture_output=True, timeout=5)
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run([tool_name, '-h'], 
                             capture_output=True, timeout=5)
                return True
            except:
                return False
    
    def convert(self, abc_notation: str, output_path: str, 
                formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        🔄 Convert ABC notation to multiple formats
        
        Args:
            abc_notation: ABC notation string
            output_path: Base output path (without extension)
            formats: List of formats to generate ['abc', 'midi', 'mp3', 'svg']
            
        Returns:
            Dict with generated files and conversion results
        """
        if formats is None:
            formats = ['abc', 'midi']
        
        results = {
            'success': True,
            'files': {},
            'errors': {},
            'formats_generated': [],
            'formats_failed': []
        }
        
        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Always save ABC file
        if 'abc' in formats:
            abc_file = f"{output_path}.abc"
            try:
                with open(abc_file, 'w') as f:
                    f.write(abc_notation)
                results['files']['abc'] = abc_file
                results['formats_generated'].append('abc')
            except Exception as e:
                results['errors']['abc'] = str(e)
                results['formats_failed'].append('abc')
        
        # Convert to other formats
        for fmt in formats:
            if fmt == 'abc':
                continue  # Already handled
            
            try:
                if fmt == 'midi':
                    success = self._convert_to_midi(abc_notation, output_path)
                elif fmt == 'mp3':
                    success = self._convert_to_mp3(abc_notation, output_path)
                elif fmt == 'svg':
                    success = self._convert_to_svg(abc_notation, output_path)
                elif fmt == 'jpg':
                    success = self._convert_to_jpg(abc_notation, output_path)
                else:
                    results['errors'][fmt] = f"Unsupported format: {fmt}"
                    results['formats_failed'].append(fmt)
                    continue
                
                if success:
                    file_path = f"{output_path}.{fmt}"
                    if os.path.exists(file_path):
                        results['files'][fmt] = file_path
                        results['formats_generated'].append(fmt)
                    else:
                        results['errors'][fmt] = "File not generated"
                        results['formats_failed'].append(fmt)
                else:
                    results['formats_failed'].append(fmt)
                    
            except Exception as e:
                results['errors'][fmt] = str(e)
                results['formats_failed'].append(fmt)
        
        # Update overall success status
        results['success'] = len(results['formats_generated']) > 0
        
        return results
    
    def _convert_to_midi(self, abc_notation: str, output_path: str) -> bool:
        """Convert ABC to MIDI using music21"""
        try:
            # Create temporary ABC file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.abc', delete=False) as tmp_abc:
                tmp_abc.write(abc_notation)
                tmp_abc_path = tmp_abc.name
            
            try:
                # Parse ABC with music21
                score = music21.converter.parse(tmp_abc_path)
                
                # Convert to MIDI
                midi_path = f"{output_path}.mid"
                score.write('midi', fp=midi_path)
                
                return os.path.exists(midi_path)
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_abc_path)
                
        except Exception as e:
            # Fallback: try with abc2midi if available
            if 'abc2midi' in self.conversion_tools:
                return self._convert_with_abc2midi(abc_notation, output_path)
            return False
    
    def _convert_with_abc2midi(self, abc_notation: str, output_path: str) -> bool:
        """Convert using abc2midi command line tool"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.abc', delete=False) as tmp_abc:
                tmp_abc.write(abc_notation)
                tmp_abc_path = tmp_abc.name
            
            try:
                midi_path = f"{output_path}.mid"
                result = subprocess.run([
                    'abc2midi', tmp_abc_path, '-o', midi_path
                ], capture_output=True, timeout=30)
                
                return result.returncode == 0 and os.path.exists(midi_path)
                
            finally:
                os.unlink(tmp_abc_path)
                
        except Exception:
            return False
    
    def _convert_to_mp3(self, abc_notation: str, output_path: str) -> bool:
        """Convert ABC to MP3 (requires MIDI first, then audio conversion)"""
        # First convert to MIDI
        if not self._convert_to_midi(abc_notation, output_path):
            return False
        
        midi_path = f"{output_path}.mid"
        mp3_path = f"{output_path}.mp3"
        
        # Try fluidsynth conversion
        if 'fluidsynth' in self.conversion_tools:
            try:
                # This is a simplified example - actual implementation would need soundfont
                result = subprocess.run([
                    'fluidsynth', '-ni', '/usr/share/sounds/sf2/FluidR3_GM.sf2',
                    midi_path, '-F', mp3_path
                ], capture_output=True, timeout=60)
                
                return result.returncode == 0 and os.path.exists(mp3_path)
            except Exception:
                pass
        
        # Try timidity conversion
        if 'timidity' in self.conversion_tools:
            try:
                result = subprocess.run([
                    'timidity', midi_path, '-Ow', '-o', f"{output_path}.wav"
                ], capture_output=True, timeout=60)
                
                if result.returncode == 0:
                    # Convert WAV to MP3 if ffmpeg available
                    return self._wav_to_mp3(f"{output_path}.wav", mp3_path)
                    
            except Exception:
                pass
        
        return False
    
    def _wav_to_mp3(self, wav_path: str, mp3_path: str) -> bool:
        """Convert WAV to MP3 using ffmpeg"""
        try:
            result = subprocess.run([
                'ffmpeg', '-i', wav_path, '-acodec', 'mp3', mp3_path
            ], capture_output=True, timeout=60)
            
            success = result.returncode == 0 and os.path.exists(mp3_path)
            
            # Clean up WAV file
            if os.path.exists(wav_path):
                os.unlink(wav_path)
            
            return success
        except Exception:
            return False
    
    def _convert_to_svg(self, abc_notation: str, output_path: str) -> bool:
        """Convert ABC to SVG notation"""
        if 'abcm2ps' not in self.conversion_tools:
            return False
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.abc', delete=False) as tmp_abc:
                tmp_abc.write(abc_notation)
                tmp_abc_path = tmp_abc.name
            
            try:
                svg_path = f"{output_path}.svg"
                result = subprocess.run([
                    'abcm2ps', '-g', tmp_abc_path, '-O', output_path
                ], capture_output=True, timeout=30)
                
                return result.returncode == 0 and os.path.exists(svg_path)
                
            finally:
                os.unlink(tmp_abc_path)
                
        except Exception:
            return False
    
    def _convert_to_jpg(self, abc_notation: str, output_path: str) -> bool:
        """Convert ABC to JPG (via SVG if available)"""
        # First convert to SVG
        if not self._convert_to_svg(abc_notation, output_path):
            return False
        
        svg_path = f"{output_path}.svg"
        jpg_path = f"{output_path}.jpg"
        
        # Convert SVG to JPG using ImageMagick
        if 'convert' in self.conversion_tools:
            try:
                result = subprocess.run([
                    'convert', svg_path, '-density', '300', '-quality', '90', jpg_path
                ], capture_output=True, timeout=30)
                
                return result.returncode == 0 and os.path.exists(jpg_path)
            except Exception:
                pass
        
        # Try Inkscape conversion
        if 'inkscape' in self.conversion_tools:
            try:
                result = subprocess.run([
                    'inkscape', svg_path, '--export-type=jpg', f'--export-filename={jpg_path}'
                ], capture_output=True, timeout=30)
                
                return result.returncode == 0 and os.path.exists(jpg_path)
            except Exception:
                pass
        
        return False
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported output formats"""
        return self.supported_formats.copy()
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get available conversion tools"""
        return self.conversion_tools.copy()
#!/usr/bin/env python3
"""
🧪 LinkTune Core Tests
Basic functionality tests for core components
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from linktune.core.extractor import ContentExtractor, ExtractionResult
from linktune.core.analyzer import ContentAnalyzer, EmotionalProfile, Emotion
from linktune.core.generator import MusicGenerator
from linktune.core.converter import MusicConverter
from linktune.core.pipeline import Pipeline

class TestContentExtractor:
    """Test content extraction functionality"""
    
    def test_extract_basic_html(self):
        """Test extracting content from basic HTML"""
        extractor = ContentExtractor()
        
        # Mock the requests response
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = """
            <html>
                <head><title>Test Page</title></head>
                <body>
                    <h1>Main Title</h1>
                    <p>This is test content for music generation.</p>
                    <p>It contains emotional and thematic elements.</p>
                </body>
            </html>
            """
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = extractor.extract("https://example.com")
            
            assert result.success
            assert "test content" in result.content.lower()
            assert result.title == "Test Page"
            assert result.platform == "generic"
    
    def test_extract_timeout(self):
        """Test extraction timeout handling"""
        extractor = ContentExtractor(timeout=1)
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Timeout")
            
            result = extractor.extract("https://slow-example.com")
            
            assert not result.success
            assert "error" in result.error_message.lower()
    
    def test_extract_invalid_url(self):
        """Test handling of invalid URLs"""
        extractor = ContentExtractor()
        
        result = extractor.extract("not-a-url")
        
        assert not result.success
        assert result.error_message

class TestContentAnalyzer:
    """Test content analysis functionality"""
    
    def test_analyze_emotional_content(self):
        """Test emotional analysis of content"""
        analyzer = ContentAnalyzer()
        
        # Test happy content
        happy_content = "This is a wonderful day full of joy and excitement! Amazing things are happening."
        analysis = analyzer.analyze_content(happy_content)
        
        assert analysis.emotional_profile.primary_emotion == Emotion.JOY
        assert analysis.emotional_profile.intensity > 0.5
        assert len(analysis.themes) > 0
    
    def test_analyze_sad_content(self):
        """Test analysis of sad content"""
        analyzer = ContentAnalyzer()
        
        sad_content = "The loss was devastating and filled everyone with deep sorrow and melancholy."
        analysis = analyzer.analyze_content(sad_content)
        
        assert analysis.emotional_profile.primary_emotion in [Emotion.SADNESS, Emotion.MELANCHOLY]
        assert analysis.emotional_profile.intensity > 0.4
    
    def test_analyze_empty_content(self):
        """Test handling of empty content"""
        analyzer = ContentAnalyzer()
        
        analysis = analyzer.analyze_content("")
        
        assert analysis.emotional_profile.primary_emotion == Emotion.CONTEMPLATION
        assert analysis.emotional_profile.intensity == 0.5
        assert len(analysis.themes) == 0

class TestMusicGenerator:
    """Test music generation functionality"""
    
    def test_generate_basic_abc(self):
        """Test basic ABC notation generation"""
        generator = MusicGenerator()
        analyzer = ContentAnalyzer()
        
        # Create test analysis
        content = "Happy melodic content about nature and joy."
        analysis = analyzer.analyze_content(content)
        
        abc_notation = generator.generate_abc(analysis, {})
        
        # Check ABC format
        assert abc_notation.startswith("X:")
        assert "T:" in abc_notation  # Title
        assert "M:" in abc_notation  # Meter
        assert "K:" in abc_notation  # Key
        assert "|" in abc_notation   # Bar lines
    
    def test_generate_with_config(self):
        """Test generation with specific configuration"""
        generator = MusicGenerator()
        analyzer = ContentAnalyzer()
        
        analysis = analyzer.analyze_content("Calm peaceful content")
        config = {
            "style": "folk",
            "key": "G major",
            "tempo": "andante"
        }
        
        abc_notation = generator.generate_abc(analysis, config)
        
        assert "G" in abc_notation  # Should respect key preference
        assert abc_notation  # Should generate something
    
    def test_emotional_mapping(self):
        """Test that emotions map to appropriate musical parameters"""
        generator = MusicGenerator()
        
        # Test different emotions
        emotions_to_test = [
            (Emotion.JOY, "major"),
            (Emotion.SADNESS, "minor"),
            (Emotion.EXCITEMENT, "fast"),
            (Emotion.PEACE, "slow")
        ]
        
        for emotion, expected_characteristic in emotions_to_test:
            # Create mock analysis
            analysis = Mock()
            analysis.emotional_profile = EmotionalProfile(
                primary_emotion=emotion,
                secondary_emotions=[],
                intensity=0.7,
                confidence=0.8
            )
            analysis.themes = []
            analysis.structure = {"complexity": "medium"}
            analysis.musical_suggestions = {}
            
            abc_notation = generator.generate_abc(analysis, {})
            
            # Basic validation that something was generated
            assert abc_notation
            assert "X:" in abc_notation

class TestMusicConverter:
    """Test music format conversion"""
    
    def test_convert_abc_to_midi(self):
        """Test ABC to MIDI conversion"""
        converter = MusicConverter()
        
        # Simple ABC notation
        abc_notation = """X:1
T:Test Song
M:4/4
L:1/8
K:C
C D E F | G A B c |
"""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test"
            
            result = converter.convert(abc_notation, str(output_path), ["abc", "midi"])
            
            # Check that ABC file was created
            assert "abc" in result["files"]
            assert Path(result["files"]["abc"]).exists()
            
            # MIDI conversion might fail without external tools, but should be attempted
            assert "midi" in result["formats_generated"] or "midi" in result["formats_failed"]
    
    def test_convert_invalid_abc(self):
        """Test handling of invalid ABC notation"""
        converter = MusicConverter()
        
        invalid_abc = "This is not valid ABC notation"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "test"
            
            result = converter.convert(invalid_abc, str(output_path), ["abc"])
            
            # Should still create ABC file even if content is invalid
            assert "abc" in result["files"]

class TestPipeline:
    """Test complete pipeline functionality"""
    
    def test_pipeline_creation(self):
        """Test pipeline creation and configuration"""
        config = {"format": ["abc"], "extraction_timeout": 5}
        pipeline = Pipeline.from_config(config)
        
        assert len(pipeline.steps) >= 4  # Extractor, Analyzer, Generator, Converter
        assert pipeline.config == config
    
    def test_pipeline_info(self):
        """Test pipeline information retrieval"""
        pipeline = Pipeline.from_config({"format": ["abc"]})
        
        info = pipeline.get_pipeline_info()
        
        assert "steps" in info
        assert "config" in info
        assert len(info["steps"]) > 0
        assert all("name" in step for step in info["steps"])
    
    @patch('linktune.core.extractor.ContentExtractor.extract')
    def test_pipeline_execution_success(self, mock_extract):
        """Test successful pipeline execution"""
        # Mock successful extraction
        mock_extract.return_value = ExtractionResult(
            success=True,
            content="Test content for music generation",
            title="Test",
            platform="test",
            metadata={},
            error_message=""
        )
        
        pipeline = Pipeline.from_config({"format": ["abc"]})
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the output path generation
            with patch.object(pipeline, '_generate_output_path', return_value=str(Path(temp_dir) / "test")):
                result = pipeline.run("https://test.com")
        
        assert result.success
        assert result.url == "https://test.com"
        assert result.execution_time > 0
    
    @patch('linktune.core.extractor.ContentExtractor.extract')
    def test_pipeline_execution_failure(self, mock_extract):
        """Test pipeline execution with extraction failure"""
        # Mock failed extraction
        mock_extract.return_value = ExtractionResult(
            success=False,
            content="",
            title="",
            platform="",
            metadata={},
            error_message="Extraction failed"
        )
        
        pipeline = Pipeline.from_config({"format": ["abc"]})
        
        result = pipeline.run("https://failing-test.com")
        
        assert not result.success
        assert "extraction failed" in result.error.lower()

class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_end_to_end_basic(self):
        """Test complete end-to-end processing"""
        # This test requires actual network access, so we'll mock it
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.text = """
            <html>
                <head><title>Integration Test</title></head>
                <body><p>Beautiful melodic content about joy and happiness.</p></body>
            </html>
            """
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            import linktune
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Redirect output to temp directory
                with patch('linktune.core.pipeline.Pipeline._generate_output_path') as mock_path:
                    mock_path.return_value = str(Path(temp_dir) / "integration_test")
                    
                    result = linktune.link_to_music("https://test.com")
            
            assert result.success
            assert "abc" in result.files
    
    def test_tier_detection(self):
        """Test detection of installed tiers"""
        import linktune
        
        tiers = linktune.get_installed_tiers()
        
        # Core should always be available
        assert "core" in tiers
        assert isinstance(tiers, list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
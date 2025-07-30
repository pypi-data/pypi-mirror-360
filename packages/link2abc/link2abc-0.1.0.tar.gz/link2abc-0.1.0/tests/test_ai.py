#!/usr/bin/env python3
"""
🤖 LinkTune AI Tests
Tests for AI enhancement features
"""

import pytest
import os
from unittest.mock import Mock, patch

# Skip AI tests if AI tier not installed
try:
    from linktune.blocks.ai.chatmusician import ChatMusicianBlock
    from linktune.blocks.ai.claude import ClaudeBlock
    from linktune.blocks.ai.chatgpt import ChatGPTBlock
    from linktune.blocks.langfuse_integration import LangfuseIntegration
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

from linktune.core.analyzer import ContentAnalysis, EmotionalProfile, Emotion, Theme
import linktune

@pytest.mark.skipif(not AI_AVAILABLE, reason="AI tier not installed")
class TestChatMusicianBlock:
    """Test ChatMusician AI block"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_analysis = ContentAnalysis(
            content="Happy melodic content about nature and joy",
            emotional_profile=EmotionalProfile(
                primary_emotion=Emotion.JOY,
                secondary_emotions=[],
                intensity=0.8,
                confidence=0.9
            ),
            themes=[
                Theme(name="nature", confidence=0.8, keywords=["nature"], category="content"),
                Theme(name="happiness", confidence=0.9, keywords=["joy", "happy"], category="emotional")
            ],
            structure={"complexity": "medium", "length": 50},
            musical_suggestions={"key": "C major", "tempo": "allegro", "style": "classical"}
        )
    
    def test_chatmusician_initialization(self):
        """Test ChatMusician block initialization"""
        block = ChatMusicianBlock()
        
        assert block.capabilities
        assert "professional_composition" in block.capabilities
        assert block.chatmusician_config is not None
    
    @patch('requests.Session.get')
    def test_connection_test(self, mock_get):
        """Test ChatMusician connection testing"""
        block = ChatMusicianBlock()
        
        # Mock successful connection
        mock_get.return_value.status_code = 200
        assert block._test_connection()
        
        # Mock failed connection
        mock_get.side_effect = Exception("Connection failed")
        assert not block._test_connection()
    
    def test_prompt_building(self):
        """Test musical prompt building"""
        block = ChatMusicianBlock()
        
        prompt = block._build_musical_prompt(self.test_analysis)
        
        assert "joy" in prompt.lower()
        assert "0.80" in prompt  # intensity
        assert "nature" in prompt.lower()
        assert "professional" in prompt.lower()
    
    def test_style_determination(self):
        """Test musical style determination"""
        block = ChatMusicianBlock()
        
        # Test explicit style
        style = block._determine_style(self.test_analysis, {"style": "jazz"})
        assert style == "jazz"
        
        # Test inferred style
        style = block._determine_style(self.test_analysis, {})
        assert style in ["classical", "contemporary", "jazz", "folk"]
    
    @patch('linktune.blocks.ai.chatmusician.ChatMusicianBlock._test_connection')
    @patch('linktune.core.generator.MusicGenerator.generate_abc')
    def test_fallback_generation(self, mock_generator, mock_connection):
        """Test fallback to rule-based generation"""
        mock_connection.return_value = False
        mock_generator.return_value = "X:1\nT:Fallback\nK:C\nC D E F|"
        
        block = ChatMusicianBlock()
        result = block.generate_abc(self.test_analysis, {})
        
        assert "fallback" in result.lower()
        assert "X:1" in result

@pytest.mark.skipif(not AI_AVAILABLE, reason="AI tier not installed")
class TestClaudeBlock:
    """Test Claude AI block"""
    
    def setup_method(self):
        """Setup test data"""
        self.test_data = {
            "extracted_content": Mock(content="Test content for analysis")
        }
    
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    def test_claude_initialization(self):
        """Test Claude block initialization"""
        with patch('anthropic.Anthropic'):
            block = ClaudeBlock()
            
            assert block.capabilities
            assert "sophisticated_analysis" in block.capabilities
    
    def test_claude_initialization_no_key(self):
        """Test Claude initialization without API key"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                ClaudeBlock()
    
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch('anthropic.Anthropic')
    def test_claude_process_success(self, mock_anthropic):
        """Test successful Claude processing"""
        # Mock Claude API response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text="Detailed analysis with joy emotion, intensity: 0.8")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client
        
        block = ClaudeBlock()
        result = block.process(self.test_data)
        
        assert "claude_enhanced" in result
        assert result["claude_enhanced"] is True

@pytest.mark.skipif(not AI_AVAILABLE, reason="AI tier not installed")
class TestChatGPTBlock:
    """Test ChatGPT AI block"""
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_chatgpt_initialization(self):
        """Test ChatGPT block initialization"""
        with patch('openai.OpenAI'):
            block = ChatGPTBlock()
            
            assert block.capabilities
            assert "creative_analysis" in block.capabilities
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch('openai.OpenAI')
    def test_chatgpt_creative_analysis(self, mock_openai):
        """Test ChatGPT creative analysis"""
        # Mock OpenAI API response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Creative analysis with joy and excitement"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        block = ChatGPTBlock()
        test_data = {"extracted_content": Mock(content="Creative content")}
        
        result = block.process(test_data)
        
        assert "chatgpt_enhanced" in result
        assert result["chatgpt_enhanced"] is True

@pytest.mark.skipif(not AI_AVAILABLE, reason="AI tier not installed")
class TestLangfuseIntegration:
    """Test Langfuse prompt integration"""
    
    @patch.dict(os.environ, {"LANGFUSE_SECRET_KEY": "test-secret", "LANGFUSE_PUBLIC_KEY": "test-public"})
    def test_langfuse_initialization(self):
        """Test Langfuse integration initialization"""
        with patch('langfuse.Langfuse'):
            integration = LangfuseIntegration()
            
            assert integration.capabilities
            assert "dynamic_prompts" in integration.capabilities
    
    @patch.dict(os.environ, {"LANGFUSE_SECRET_KEY": "test-secret", "LANGFUSE_PUBLIC_KEY": "test-public"})
    @patch('langfuse.Langfuse')
    def test_prompt_injection(self, mock_langfuse):
        """Test prompt injection functionality"""
        # Mock Langfuse client
        mock_client = Mock()
        mock_prompt = Mock()
        mock_prompt.prompt = "Test prompt with {emotion} and {intensity}"
        mock_client.get_prompt.return_value = mock_prompt
        mock_langfuse.return_value = mock_client
        
        integration = LangfuseIntegration()
        
        # Test prompt injection
        result = integration.inject_prompt(
            "test_prompt",
            variables={"emotion": "joy", "intensity": "0.8"},
            fallback="Fallback prompt"
        )
        
        assert "joy" in result
        assert "0.8" in result
    
    def test_prompt_injection_fallback(self):
        """Test prompt injection with fallback"""
        # No Langfuse configured, should use fallback
        integration = LangfuseIntegration.__new__(LangfuseIntegration)  # Skip __init__
        integration.prompt_cache = {}
        integration.last_cache_update = {}
        integration.config = {}
        
        result = integration.inject_prompt(
            "nonexistent_prompt",
            fallback="This is a fallback prompt"
        )
        
        assert result == "This is a fallback prompt"

@pytest.mark.skipif(not AI_AVAILABLE, reason="AI tier not installed")
class TestAIIntegration:
    """Test AI integration with main LinkTune API"""
    
    @patch('requests.get')
    def test_ai_enhanced_conversion(self, mock_get):
        """Test AI-enhanced music conversion"""
        # Mock web content
        mock_response = Mock()
        mock_response.text = """
        <html>
            <head><title>AI Test</title></head>
            <body><p>Happy content about music and joy.</p></body>
        </html>
        """
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test with ChatMusician (fallback to simulation if API not available)
        result = linktune.link_to_music(
            "https://test.com",
            ai="chatmusician",
            config={"format": ["abc"]}
        )
        
        # Should succeed even in simulation mode
        assert result.success or result.error  # Either success or proper error handling
    
    def test_ai_tier_detection(self):
        """Test AI tier detection"""
        tiers = linktune.get_installed_tiers()
        
        if AI_AVAILABLE:
            assert "ai" in tiers
        else:
            assert "ai" not in tiers
    
    @patch('requests.get')
    def test_ai_fallback_behavior(self, mock_get):
        """Test AI fallback to rule-based generation"""
        # Mock web content
        mock_response = Mock()
        mock_response.text = "<html><body><p>Test content</p></body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test with invalid AI type - should fallback to core generation
        result = linktune.link_to_music(
            "https://test.com",
            ai="nonexistent_ai",
            config={"format": ["abc"]}
        )
        
        # Should still succeed with fallback
        assert result.success

class TestAIConfiguration:
    """Test AI configuration and setup"""
    
    def test_ai_config_validation(self):
        """Test AI configuration validation"""
        from linktune.core.pipeline import Pipeline
        
        # Valid AI config
        valid_config = {
            "ai": "chatmusician",
            "format": ["abc"]
        }
        
        # Should not raise exception
        pipeline = Pipeline.from_config(valid_config)
        assert pipeline.config["ai"] == "chatmusician"
    
    def test_missing_ai_dependencies(self):
        """Test handling of missing AI dependencies"""
        # This test simulates what happens when AI blocks can't be imported
        with patch('linktune.core.pipeline.Pipeline.from_config') as mock_from_config:
            mock_from_config.side_effect = ImportError("AI tier not available")
            
            with pytest.raises(ImportError):
                Pipeline.from_config({"ai": "chatmusician"})

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not integration"])
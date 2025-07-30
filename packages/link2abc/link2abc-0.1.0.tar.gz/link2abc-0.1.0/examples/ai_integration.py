#!/usr/bin/env python3
"""
🤖 LinkTune AI Integration Examples
Advanced examples showing AI features with ChatMusician, Claude, and ChatGPT
"""

import os
import linktune
from linktune.blocks.langfuse_integration import LangfuseIntegration, inject_prompt_into_config

def chatmusician_example():
    """ChatMusician professional composition example"""
    print("🎼 ChatMusician Professional Composition")
    print("=" * 50)
    
    # Check if ChatMusician is available
    if 'CHATMUSICIAN_API_KEY' not in os.environ:
        print("⚠️  Set CHATMUSICIAN_API_KEY environment variable for full functionality")
        print("   Using simulation mode for demo")
    
    # Professional composition with ChatMusician
    result = linktune.link_to_music(
        "https://app.simplenote.com/p/bBs4zY",
        ai="chatmusician",
        config={
            "style": "jazz",
            "complexity": "high",
            "chatmusician_params": {
                "features": {
                    "advanced_harmonies": True,
                    "ornamental_expressions": True,
                    "style_transfer": True
                }
            }
        }
    )
    
    print(f"✅ Success: {result.success}")
    if result.success:
        print(f"🎵 Generated: {result.files}")
        
        # Show metadata if available
        if result.metadata and 'analysis' in result.metadata:
            analysis = result.metadata['analysis']
            print(f"🎭 Emotion: {analysis.get('emotional_profile', {}).get('primary_emotion')}")
            print(f"🎨 Style: {analysis.get('musical_suggestions', {}).get('style')}")

def claude_analysis_example():
    """Claude sophisticated content analysis"""
    print("\n🧠 Claude Content Analysis")
    print("=" * 50)
    
    if 'ANTHROPIC_API_KEY' not in os.environ:
        print("⚠️  Set ANTHROPIC_API_KEY environment variable for full functionality")
        return
    
    # Use Claude for sophisticated analysis
    result = linktune.link_to_music(
        "https://app.simplenote.com/p/bBs4zY",
        ai="claude",
        config={
            "claude_model": "claude-3-sonnet-20240229",
            "prompts": {
                "claude_analysis": """
                Analyze this content for musical composition with deep cultural understanding:
                
                {content}
                
                Provide insights on:
                1. Cultural context and musical traditions
                2. Emotional layers and complexity
                3. Narrative structure for musical adaptation
                4. Symbolic elements that could inspire musical motifs
                """
            }
        }
    )
    
    print(f"✅ Success: {result.success}")
    if result.metadata:
        print("🔍 Claude enhanced analysis available")

def chatgpt_creative_example():
    """ChatGPT creative interpretation"""
    print("\n🎨 ChatGPT Creative Interpretation")
    print("=" * 50)
    
    if 'OPENAI_API_KEY' not in os.environ:
        print("⚠️  Set OPENAI_API_KEY environment variable for full functionality")
        return
    
    # Creative interpretation with ChatGPT
    result = linktune.link_to_music(
        "https://app.simplenote.com/p/bBs4zY",
        ai="chatgpt",
        config={
            "chatgpt_model": "gpt-4",
            "prompts": {
                "chatgpt_analysis": """
                Provide a creative musical interpretation of this content:
                
                {content}
                
                Think creatively about:
                1. How to translate abstract concepts into musical elements
                2. Innovative approaches to represent the content's essence
                3. Multiple creative perspectives for musical adaptation
                4. Experimental techniques that could capture the content's spirit
                """
            }
        }
    )
    
    print(f"✅ Success: {result.success}")
    if result.metadata:
        print("🎨 ChatGPT creative enhancement available")

def langfuse_prompt_example():
    """Langfuse dynamic prompt injection"""
    print("\n🧵 Langfuse Dynamic Prompts")
    print("=" * 50)
    
    # Check if Langfuse is configured
    if not all(key in os.environ for key in ['LANGFUSE_SECRET_KEY', 'LANGFUSE_PUBLIC_KEY']):
        print("⚠️  Set LANGFUSE_SECRET_KEY and LANGFUSE_PUBLIC_KEY for dynamic prompts")
        print("   Using static prompts for demo")
        
        # Static prompt example
        config = {
            "ai": "chatmusician",
            "prompts": {
                "chatmusician_composition": """
                Generate a {style} composition with {emotion} emotion.
                
                Requirements:
                - Advanced harmonic progressions
                - Emotional depth matching intensity {intensity}
                - Themes: {themes}
                - Professional orchestration
                """
            }
        }
        
        result = linktune.link_to_music("https://app.simplenote.com/p/bBs4zY", config=config)
        print(f"📝 Static prompt example: {result.success}")
        return
    
    try:
        # Dynamic prompt injection with Langfuse
        langfuse = LangfuseIntegration()
        
        # Inject prompt for ChatMusician composition
        config = {"ai": "chatmusician"}
        config = inject_prompt_into_config(
            config, 
            "chatmusician_composition_v2",
            variables={
                "emotion": "contemplative",
                "intensity": 0.7,
                "themes": "technology, future, innovation"
            }
        )
        
        result = linktune.link_to_music("https://app.simplenote.com/p/bBs4zY", config=config)
        print(f"✅ Langfuse prompt injection: {result.success}")
        
    except Exception as e:
        print(f"⚠️  Langfuse integration error: {e}")

def ai_comparison_example():
    """Compare different AI models on the same content"""
    print("\n🔬 AI Model Comparison")
    print("=" * 50)
    
    url = "https://app.simplenote.com/p/bBs4zY"
    ai_models = ["chatmusician", "claude", "chatgpt"]
    results = {}
    
    for ai_model in ai_models:
        print(f"Testing {ai_model}...")
        
        try:
            result = linktune.link_to_music(
                url,
                ai=ai_model,
                config={"format": ["abc"]}  # Keep it simple for comparison
            )
            
            results[ai_model] = {
                "success": result.success,
                "execution_time": result.execution_time,
                "error": result.error
            }
            
            status = "✅" if result.success else "❌"
            print(f"   {status} {ai_model}: {result.execution_time:.2f}s")
            
        except Exception as e:
            results[ai_model] = {
                "success": False,
                "execution_time": 0,
                "error": str(e)
            }
            print(f"   ❌ {ai_model}: {e}")
    
    # Summary
    print(f"\n📊 AI Comparison Results:")
    for ai_model, result in results.items():
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {ai_model}: {result['execution_time']:.2f}s")

def custom_ai_pipeline_example():
    """Create custom pipeline with multiple AI stages"""
    print("\n🔗 Custom AI Pipeline")
    print("=" * 50)
    
    from linktune.core.pipeline import Pipeline
    from linktune.core.lego_factory import get_lego_factory
    
    # Get LEGO factory
    factory = get_lego_factory()
    
    # Create custom pipeline with multiple AI stages
    try:
        # Build pipeline with Claude for analysis + ChatMusician for generation
        pipeline_config = {
            "ai": "chatmusician",  # Primary AI
            "format": ["abc", "midi"],
            "prompts": {
                "multi_stage_analysis": True
            }
        }
        
        pipeline = Pipeline.from_config(pipeline_config)
        
        # Show pipeline info
        info = pipeline.get_pipeline_info()
        print(f"🔧 Pipeline components:")
        for step in info['steps']:
            print(f"   • {step['name']}")
        
        # Run pipeline
        result = pipeline.run("https://app.simplenote.com/p/bBs4zY")
        print(f"✅ Custom pipeline success: {result.success}")
        
    except Exception as e:
        print(f"❌ Custom pipeline error: {e}")

def ai_configuration_optimization():
    """Show AI configuration optimization techniques"""
    print("\n⚡ AI Configuration Optimization")
    print("=" * 50)
    
    # Performance-optimized config
    fast_config = {
        "ai": "chatmusician",
        "format": ["abc"],  # Minimal output
        "extraction_timeout": 5,
        "chatmusician_params": {
            "model_version": "fast",
            "complexity": "simple"
        }
    }
    
    # Quality-optimized config
    quality_config = {
        "ai": "chatmusician",
        "format": ["abc", "midi", "mp3"],
        "chatmusician_params": {
            "model_version": "latest",
            "complexity": "high",
            "features": {
                "advanced_harmonies": True,
                "ornamental_expressions": True,
                "style_transfer": True
            }
        },
        "prompts": {
            "quality_focus": True
        }
    }
    
    print("⚡ Fast config (0.5-2s):")
    print(f"   {fast_config}")
    
    print("\n🎨 Quality config (2-10s):")
    print(f"   {quality_config}")
    
    # Test both configurations
    for name, config in [("Fast", fast_config), ("Quality", quality_config)]:
        try:
            import time
            start = time.time()
            result = linktune.link_to_music("https://app.simplenote.com/p/bBs4zY", config=config)
            elapsed = time.time() - start
            
            status = "✅" if result.success else "❌"
            print(f"   {status} {name}: {elapsed:.2f}s")
            
        except Exception as e:
            print(f"   ❌ {name}: {e}")

def main():
    """Run all AI integration examples"""
    print("🤖 LinkTune AI Integration Examples")
    print("=" * 60)
    
    # Check available tiers
    tiers = linktune.get_installed_tiers()
    print(f"🧱 Available tiers: {', '.join(tiers)}")
    
    if 'ai' not in tiers:
        print("❌ AI tier not installed")
        print("   Install with: pip install linktune[ai]")
        return
    
    # Run AI examples
    chatmusician_example()
    claude_analysis_example()
    chatgpt_creative_example()
    langfuse_prompt_example()
    ai_comparison_example()
    custom_ai_pipeline_example()
    ai_configuration_optimization()
    
    print("\n🎉 AI Integration examples completed!")
    print("📚 For advanced AI features, see:")
    print("   https://linktune.readthedocs.io/en/latest/ai-integration/")

if __name__ == "__main__":
    main()
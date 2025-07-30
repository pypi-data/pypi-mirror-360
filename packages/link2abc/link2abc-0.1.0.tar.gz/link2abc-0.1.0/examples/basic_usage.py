#!/usr/bin/env python3
"""
🎵 LinkTune Basic Usage Examples
Simple examples showing how to use LinkTune programmatically
"""

import linktune
from linktune import Pipeline
from linktune.core.pipeline import PipelineResult

def basic_conversion():
    """Basic link-to-music conversion"""
    print("🎵 Basic Conversion Example")
    print("=" * 40)
    
    # Simple conversion
    result = linktune.link_to_music("https://app.simplenote.com/p/bBs4zY")
    
    print(f"✅ Success: {result.success}")
    print(f"📄 Generated files: {result.files}")
    print(f"⏱️  Execution time: {result.execution_time:.2f}s")
    
    return result

def ai_enhanced_conversion():
    """AI-enhanced music generation"""
    print("\n🤖 AI Enhanced Example")
    print("=" * 40)
    
    # Check if AI tier is available
    tiers = linktune.get_installed_tiers()
    if 'ai' not in tiers:
        print("❌ AI tier not installed")
        print("   Install with: pip install linktune[ai]")
        return None
    
    # AI-enhanced conversion
    result = linktune.link_to_music(
        "https://app.simplenote.com/p/bBs4zY",
        ai="chatmusician",
        format=["abc", "midi"],
        config={
            "style": "jazz",
            "complexity": "medium"
        }
    )
    
    print(f"✅ Success: {result.success}")
    print(f"🎼 Files: {result.files}")
    
    if result.metadata:
        analysis = result.metadata.get('analysis', {})
        if analysis:
            emotional = analysis.get('emotional_profile', {})
            print(f"🎭 Emotion: {emotional.get('primary_emotion', 'unknown')}")
            print(f"📊 Intensity: {emotional.get('intensity', 0):.2f}")
    
    return result

def custom_pipeline_example():
    """Custom pipeline with specific steps"""
    print("\n🔗 Custom Pipeline Example")
    print("=" * 40)
    
    # Create custom pipeline configuration
    config = {
        'ai': 'chatmusician',
        'format': ['abc', 'midi'],
        'style': 'classical',
        'extraction_timeout': 15
    }
    
    # Create pipeline from configuration
    pipeline = Pipeline.from_config(config)
    
    # Show pipeline info
    info = pipeline.get_pipeline_info()
    print(f"🔧 Pipeline steps: {len(info['steps'])}")
    for step in info['steps']:
        print(f"   • {step['name']}")
    
    # Run pipeline
    result = pipeline.run("https://app.simplenote.com/p/bBs4zY")
    
    print(f"✅ Success: {result.success}")
    print(f"📁 Output: {result.files}")
    
    return result

def batch_processing_example():
    """Process multiple URLs in batch"""
    print("\n📦 Batch Processing Example")
    print("=" * 40)
    
    urls = [
        "https://app.simplenote.com/p/bBs4zY",
        "https://httpbin.org/json",
        "https://jsonplaceholder.typicode.com/posts/1"
    ]
    
    results = []
    
    for i, url in enumerate(urls, 1):
        print(f"Processing {i}/{len(urls)}: {url}")
        
        try:
            result = linktune.link_to_music(
                url,
                format=["abc"],  # Keep it simple for batch
                config={"extraction_timeout": 5}
            )
            results.append(result)
            
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.execution_time:.1f}s")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    successful = sum(1 for r in results if r.success)
    print(f"\n📊 Batch Summary: {successful}/{len(urls)} successful")
    
    return results

def configuration_examples():
    """Show different configuration options"""
    print("\n⚙️ Configuration Examples")
    print("=" * 40)
    
    # Minimal config
    minimal_config = {
        'format': ['abc']
    }
    
    # Full config with all options
    full_config = {
        'ai': 'chatmusician',
        'format': ['abc', 'midi', 'mp3'],
        'style': 'jazz',
        'complexity': 'high',
        'extraction_timeout': 10,
        'output_dir': './output',
        'prompts': {
            'chatmusician_composition': 'Create a sophisticated jazz composition with {emotion} emotion'
        }
    }
    
    # Cloud config
    cloud_config = {
        'cloud': True,
        'cost_optimize': True,
        'ai': 'chatmusician',
        'format': ['abc', 'midi']
    }
    
    print("📝 Configuration options:")
    print(f"   Minimal: {minimal_config}")
    print(f"   Full: {full_config}")
    print(f"   Cloud: {cloud_config}")

def error_handling_example():
    """Show proper error handling"""
    print("\n🛡️ Error Handling Example")
    print("=" * 40)
    
    # Example with invalid URL
    try:
        result = linktune.link_to_music("not-a-valid-url")
        if not result.success:
            print(f"❌ Conversion failed: {result.error}")
    except Exception as e:
        print(f"❌ Exception caught: {e}")
    
    # Example with timeout
    try:
        result = linktune.link_to_music(
            "https://httpbin.org/delay/10",  # Simulates slow response
            config={'extraction_timeout': 2}
        )
        if not result.success:
            print(f"⏱️  Timeout error: {result.error}")
    except Exception as e:
        print(f"⏱️  Timeout exception: {e}")
    
    print("✅ Error handling complete")

def main():
    """Run all examples"""
    print("🎵 LinkTune Usage Examples")
    print("=" * 50)
    
    # Run examples
    basic_conversion()
    ai_enhanced_conversion()
    custom_pipeline_example()
    batch_processing_example()
    configuration_examples()
    error_handling_example()
    
    print("\n🎉 All examples completed!")
    print("📚 Check the documentation for more advanced usage:")
    print("   https://linktune.readthedocs.io")

if __name__ == "__main__":
    main()
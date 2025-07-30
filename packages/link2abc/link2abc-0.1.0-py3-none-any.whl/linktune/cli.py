#!/usr/bin/env python3
"""
🎵 LinkTune CLI
Dead-simple command-line interface for link-to-music conversion

Usage: linktune https://example.com
"""

import sys
import click
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

from .core.pipeline import Pipeline, PipelineResult
from . import __version__, get_installed_tiers

@click.command()
@click.argument('url', required=False)
@click.option('--ai', 
              type=click.Choice(['chatmusician', 'claude', 'chatgpt', 'auto'], case_sensitive=False),
              help='AI model for enhanced generation')
@click.option('--format', '-f', 
              default='abc,midi',
              help='Output formats (comma-separated): abc,midi,mp3,svg,jpg')
@click.option('--output', '-o',
              help='Output filename (without extension)')
@click.option('--prompt-file', '-p',
              type=click.Path(exists=True),
              help='YAML file with custom prompts')
@click.option('--config', '-c',
              type=click.Path(),
              help='Configuration file path')
@click.option('--neural', is_flag=True,
              help='Enable neural synthesis (requires neural tier)')
@click.option('--cloud', is_flag=True,
              help='Use cloud execution (requires cloud tier)')
@click.option('--cost-optimize', is_flag=True,
              help='Optimize for cost efficiency in cloud mode')
@click.option('--test', is_flag=True,
              help='Test functionality with example URL')
@click.option('--test-ai', is_flag=True,
              help='Test AI functionality (requires AI tier)')
@click.option('--version', is_flag=True,
              help='Show version information')
@click.option('--list-tiers', is_flag=True,
              help='List available enhancement tiers')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output')
def main(url: Optional[str], ai: Optional[str], format: str, output: Optional[str],
         prompt_file: Optional[str], config: Optional[str], neural: bool, cloud: bool,
         cost_optimize: bool, test: bool, test_ai: bool, version: bool, 
         list_tiers: bool, verbose: bool):
    """
    🎵 Link2ABC - Transform any link into ABC music notation with AI
    
    Convert web content to beautiful ABC notation using rule-based generation,
    AI enhancement, or full neural synthesis.
    
    Examples:
    
      link2abc https://app.simplenote.com/p/bBs4zY
      
      link2abc https://app.simplenote.com/p/bBs4zY --ai chatmusician
      
      link2abc https://app.simplenote.com/p/bBs4zY --format abc,midi,mp3 --ai claude
    """
    
    # Handle special commands
    if version:
        click.echo(f"Link2ABC v{__version__}")
        click.echo("Transform any link into ABC music notation with AI - simple as that!")
        return
    
    if list_tiers:
        tiers = get_installed_tiers()
        click.echo("🧱 Available Link2ABC Tiers:")
        for tier in tiers:
            if tier == 'core':
                click.echo("  ✅ core - Basic rule-based generation")
            elif tier == 'ai':
                click.echo("  ✅ ai - AI-enhanced composition (ChatMusician, Claude, ChatGPT)")
            elif tier == 'neural':
                click.echo("  ✅ neural - Neural synthesis (Orpheus integration)")
            elif tier == 'cloud':
                click.echo("  ✅ cloud - Cloud execution with auto-terminate")
        
        missing_tiers = set(['ai', 'neural', 'cloud']) - set(tiers)
        for tier in missing_tiers:
            click.echo(f"  ❌ {tier} - Install with: pip install link2abc[{tier}]")
        return
    
    if test:
        _run_test(verbose)
        return
    
    if test_ai:
        _run_ai_test(verbose)
        return
    
    # Require URL for actual processing
    if not url:
        click.echo("❌ Error: URL is required")
        click.echo("Usage: link2abc https://app.simplenote.com/p/bBs4zY")
        click.echo("Run 'link2abc --help' for more options")
        sys.exit(1)
    
    try:
        # Load configuration
        config_data = _load_config(config, prompt_file)
        
        # Build processing configuration
        processing_config = _build_processing_config(
            ai, format, neural, cloud, cost_optimize, config_data
        )
        
        if verbose:
            click.echo(f"🔧 Configuration: {processing_config}")
        
        # Create and run pipeline
        pipeline = Pipeline.from_config(processing_config)
        
        if verbose:
            pipeline_info = pipeline.get_pipeline_info()
            click.echo(f"🔗 Pipeline steps: {[step['name'] for step in pipeline_info['steps']]}")
        
        # Execute conversion
        click.echo(f"🎵 Converting: {url}")
        result = pipeline.run(url, output)
        
        # Display results
        _display_result(result, verbose)
        
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)
        
    except KeyboardInterrupt:
        click.echo("\n🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"💥 Unexpected error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def _load_config(config_path: Optional[str], prompt_file: Optional[str]) -> Dict[str, Any]:
    """Load configuration from files"""
    config = {}
    
    # Load main config
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    config = yaml.safe_load(f) or {}
                else:
                    import json
                    config = json.load(f)
        except Exception as e:
            click.echo(f"⚠️  Warning: Failed to load config file: {e}")
    
    # Load prompts
    if prompt_file and Path(prompt_file).exists():
        try:
            with open(prompt_file, 'r') as f:
                prompts = yaml.safe_load(f) or {}
                config['prompts'] = prompts
        except Exception as e:
            click.echo(f"⚠️  Warning: Failed to load prompt file: {e}")
    
    return config

def _build_processing_config(ai: Optional[str], format: str, neural: bool, 
                           cloud: bool, cost_optimize: bool, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build processing configuration"""
    processing_config = config_data.copy()
    
    # Set AI option
    if ai:
        processing_config['ai'] = ai
    
    # Set output formats
    processing_config['format'] = format.split(',')
    
    # Neural processing
    if neural:
        processing_config['neural'] = True
    
    # Cloud execution
    if cloud:
        processing_config['cloud'] = True
        if cost_optimize:
            processing_config['cost_optimize'] = True
    
    return processing_config

def _run_test(verbose: bool):
    """Run basic functionality test"""
    click.echo("🧪 Testing Link2ABC basic functionality...")
    
    test_url = "https://example.com"
    
    try:
        pipeline = Pipeline.from_config({'format': ['abc']})
        result = pipeline.run(test_url)
        
        if result.success:
            click.echo("✅ Basic test passed!")
            if verbose:
                click.echo(f"   Generated: {result.files}")
                click.echo(f"   Execution time: {result.execution_time:.2f}s")
        else:
            click.echo(f"❌ Basic test failed: {result.error}")
            
    except Exception as e:
        click.echo(f"❌ Test error: {e}")

def _run_ai_test(verbose: bool):
    """Run AI functionality test"""
    installed_tiers = get_installed_tiers()
    
    if 'ai' not in installed_tiers:
        click.echo("❌ AI tier not installed")
        click.echo("   Install with: pip install link2abc[ai]")
        return
    
    click.echo("🤖 Testing Link2ABC AI functionality...")
    
    test_url = "https://example.com"
    
    # Test each available AI
    ai_models = ['chatmusician', 'claude', 'chatgpt']
    
    for ai_model in ai_models:
        try:
            click.echo(f"   Testing {ai_model}...")
            pipeline = Pipeline.from_config({
                'ai': ai_model,
                'format': ['abc']
            })
            result = pipeline.run(test_url)
            
            if result.success:
                click.echo(f"   ✅ {ai_model} test passed!")
            else:
                click.echo(f"   ⚠️  {ai_model} test failed: {result.error}")
                
        except ImportError:
            click.echo(f"   ❌ {ai_model} not available")
        except Exception as e:
            click.echo(f"   ❌ {ai_model} error: {e}")

def _display_result(result: PipelineResult, verbose: bool):
    """Display processing results"""
    if result.success:
        click.echo("✅ Conversion completed successfully!")
        
        # Show generated files
        if result.files:
            click.echo("\n📄 Generated files:")
            for format_type, file_path in result.files.items():
                file_size = _get_file_size(file_path)
                click.echo(f"   🎵 {format_type.upper()}: {file_path} ({file_size})")
        
        # Show metadata
        if verbose and result.metadata:
            metadata = result.metadata
            
            if 'extraction' in metadata:
                ext = metadata['extraction']
                click.echo(f"\n📝 Content extracted from: {ext.get('platform', 'unknown')}")
                if ext.get('title'):
                    click.echo(f"   Title: {ext['title']}")
            
            if 'analysis' in metadata:
                analysis = metadata['analysis']
                emotional = analysis.get('emotional_profile', {})
                click.echo(f"\n🎭 Analysis:")
                click.echo(f"   Emotion: {emotional.get('primary_emotion', 'unknown')}")
                click.echo(f"   Intensity: {emotional.get('intensity', 0):.2f}")
                
                themes = analysis.get('themes', [])
                if themes:
                    theme_names = [t['name'] for t in themes[:3]]
                    click.echo(f"   Themes: {', '.join(theme_names)}")
        
        click.echo(f"\n⏱️  Execution time: {result.execution_time:.2f}s")
        
    else:
        click.echo(f"❌ Conversion failed: {result.error}")
        
        if verbose and result.metadata:
            config = result.metadata.get('pipeline_config', {})
            click.echo(f"   Configuration: {config}")

def _get_file_size(file_path: str) -> str:
    """Get human-readable file size"""
    try:
        size = Path(file_path).stat().st_size
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "unknown size"

if __name__ == '__main__':
    main()
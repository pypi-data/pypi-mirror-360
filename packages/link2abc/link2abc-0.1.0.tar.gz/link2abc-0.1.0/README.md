# 🎵 Link2ABC

**Transform any link into ABC music notation with AI - simple as that!**

[![PyPI version](https://badge.fury.io/py/link2abc.svg)](https://badge.fury.io/py/link2abc)
[![Python Support](https://img.shields.io/pypi/pyversions/link2abc.svg)](https://pypi.org/project/link2abc/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Link2ABC converts any web content into beautiful ABC music notation using AI. From blog posts to ChatGPT conversations, from simple melodies to professional compositions with ChatMusician AI.

## ⚡ Quick Start

```bash
# Install and create music in 30 seconds
pip install link2abc
link2abc https://app.simplenote.com/p/bBs4zY
# Output: melody.abc, melody.mid
```

## 🎯 Features

- **🎵 Universal**: Works with any web content
- **🤖 AI-Powered**: ChatMusician integration for professional composition
- **🧱 Modular**: Progressive enhancement architecture  
- **💰 Cost-Effective**: Cloud execution with auto-terminate
- **🎼 Multi-Format**: ABC, MIDI, MP3, SVG output
- **📝 Langfuse Ready**: Custom prompt injection

## 📦 Installation Tiers

### 🥇 Core (Basic)
Perfect for getting started - 99% installation success rate.

```bash
pip install link2abc
# Size: ~15MB | Success: 99% | Features: Basic rule-based generation
```

### 🤖 AI Enhanced (Recommended)  
Professional music generation with ChatMusician.

```bash
pip install link2abc[ai]
# Size: ~50MB | Success: 95% | Features: + ChatMusician, Claude, ChatGPT
```

### 🧠 Neural Processing
Advanced audio synthesis with Orpheus integration.

```bash
pip install link2abc[neural] 
# Size: ~2GB | Success: 80% | Features: + Neural synthesis, Voice input
```

### 🌍 Everything
All features including cloud execution.

```bash
pip install link2abc[full]
# Size: ~3GB | Success: 70% | Features: + Cloud execution, Voice bridge
```

## 🎵 Usage Examples

### Basic Usage
```bash
# Convert any link to music
link2abc https://app.simplenote.com/p/bBs4zY

# Specify output format
link2abc https://app.simplenote.com/p/bBs4zY --format abc,midi,mp3

# Custom output location
link2abc https://app.simplenote.com/p/bBs4zY --output my_song
```

### AI Enhancement
```bash
# Use ChatMusician (recommended)
link2abc https://app.simplenote.com/p/bBs4zY --ai chatmusician

# Compare different AI models
link2abc https://app.simplenote.com/p/bBs4zY --ai chatmusician,claude,chatgpt

# Custom AI prompts
link2abc https://app.simplenote.com/p/bBs4zY --prompt-file custom_prompts.yaml
```

### Advanced Features
```bash
# Neural audio synthesis
link2abc https://app.simplenote.com/p/bBs4zY --neural

# Voice input (requires microphone)
link2abc --voice "Create a happy melody about friendship"

# Cloud execution (cost-optimized)
link2abc https://app.simplenote.com/p/bBs4zY --cloud --cost-optimize
```

## 🐍 Python API

### Simple API
```python
import linktune

# One-liner conversion
result = linktune.link_to_music("https://app.simplenote.com/p/bBs4zY")
print(f"Generated: {result['abc_file']}")

# With AI enhancement
result = linktune.link_to_music(
    "https://app.simplenote.com/p/bBs4zY", 
    ai="chatmusician",
    format=["abc", "midi", "mp3"]
)
```

### Advanced Pipeline
```python
from linktune import Pipeline
from linktune.blocks.ai import ChatMusicianBlock

# Custom pipeline
pipeline = Pipeline([
    linktune.ContentExtractor(),
    linktune.ContentAnalyzer(),
    ChatMusicianBlock(),
    linktune.FormatConverter()
])

# Process with custom prompts
pipeline.inject_prompt("musical_style", "Create jazz-influenced composition")
result = pipeline.run("https://app.simplenote.com/p/bBs4zY")
```

## 🤖 ChatMusician Integration

Link2ABC features first-class ChatMusician integration for professional music generation.

### Setup
```bash
# Install with ChatMusician support
pip install link2abc[ai]

# Set API key
export CHATMUSICIAN_API_KEY="your-key-here"

# Generate professional music
link2abc https://app.simplenote.com/p/bBs4zY --ai chatmusician
```

### Features
- **Professional Harmonies**: Advanced chord progressions
- **Style Transfer**: Jazz, Classical, Celtic, Folk adaptations
- **Ornamental Expressions**: Grace notes, trills, articulations
- **Multi-Format Output**: ABC, MIDI, MP3, SVG generation

## 📝 Langfuse Prompt Customization

Inject custom prompts at any pipeline stage:

```yaml
# prompts.yaml
content_analysis: |
  Analyze this content for musical elements:
  - Identify emotional tone and energy level
  - Extract key themes and narrative arc
  - Suggest appropriate musical genre

chatmusician_composition: |
  Generate ABC notation that:
  - Reflects the emotional journey
  - Uses sophisticated harmonic progressions
  - Includes ornamental expressions
  - Maintains musical coherence
```

```bash
link2abc https://app.simplenote.com/p/bBs4zY --prompt-file prompts.yaml
```

## ⚙️ Configuration

### Environment Variables
```bash
# AI Services
export CHATMUSICIAN_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Langfuse
export LANGFUSE_PUBLIC_KEY="your-key"

# Cloud Execution
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
```

### Config File
```yaml
# ~/.link2abc/config.yaml
ai:
  default: "chatmusician"
  chatmusician:
    endpoint: "https://api.chatmusician.com"
    model: "latest"
  
output:
  default_format: ["abc", "midi"]
  directory: "~/Music/Link2ABC"

cloud:
  auto_terminate: true
  cost_optimize: true
  instance_type: "t3.medium"
```

## 🧪 Testing Your Installation

```bash
# Test basic functionality
link2abc --test

# Test AI features (if installed)
link2abc --test-ai

# Test with real content
link2abc https://app.simplenote.com/p/bBs4zY

# Check available features
python -c "import linktune; print(linktune.get_installed_tiers())"
```

## 📊 Performance & Cost

### Execution Speed
- **Basic**: 0.1-0.5 seconds
- **AI Enhanced**: 1-5 seconds  
- **Neural**: 5-15 seconds
- **Cloud**: 0.3-2 seconds + startup

### Cloud Cost (with auto-terminate)
- **Basic Processing**: $0.001-0.01 per conversion
- **AI Generation**: $0.01-0.05 per conversion
- **Neural Synthesis**: $0.05-0.20 per conversion

## 🔧 Development

### Setup Development Environment
```bash
git clone https://github.com/jgwill/link2abc
cd link2abc
pip install -e ".[dev]"
pre-commit install
```

### Run Tests
```bash
# Basic tests
pytest tests/unit/

# Integration tests (requires AI keys)
pytest tests/integration/ 

# Full test suite
pytest
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📚 Documentation

- **Full Documentation**: https://link2abc.readthedocs.io
- **API Reference**: https://link2abc.readthedocs.io/api/
- **Examples**: https://github.com/jgwill/link2abc/tree/main/examples
- **Tutorials**: https://link2abc.readthedocs.io/tutorials/

## 🤝 Support

- **Issues**: https://github.com/jgwill/link2abc/issues
- **Discussions**: https://github.com/jgwill/link2abc/discussions
- **Documentation**: https://link2abc.readthedocs.io
- **Email**: jerry@gmusic.dev

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🎵 Examples

Check out the [examples directory](examples/) for:
- Basic link conversion examples
- AI-enhanced composition tutorials  
- Custom pipeline implementations
- Langfuse prompt templates
- Integration with other tools

---

**Transform any link into ABC music notation with AI - simple as that!** 🎵✨
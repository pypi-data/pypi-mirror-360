# Copper Sun Brass

> 🧠 Development Intelligence for AI Agents

Copper Sun Brass is an AI advisory system that acts as a "General Staff" for AI agents (like Claude Code) working on software projects. It provides persistent memory, project analysis, and intelligence gathering.

## 🚀 Quick Start

### One-Command Installation (Recommended)
```bash
# Install and activate trial in one command
curl -fsSL https://brass.coppersun.dev/setup | bash

# Navigate to your project and initialize
cd your-project
brass init
```

### Standard Installation
```bash
# Install from PyPI (recommended: pipx for isolated environment)
pipx install coppersun-brass

# Generate and activate 15-day trial
brass generate-trial --activate

# Configure Claude API (required)
brass config set claude_api_key sk-your-api-key

# Initialize in your project
cd your-project
brass init
```

### Check Status
```bash
# Verify everything is working
brass status

# Get AI insights for your project
brass insights

# View legal documents
brass legal
```

## 🎯 Key Features

### Four Specialized Agents

1. **Watch Agent** 👁️ - Continuous project monitoring
2. **Scout Agent** 🔍 - Deep code analysis and pattern detection  
3. **Strategist Agent** 🎯 - High-level planning and recommendations
4. **Planner Agent** 📋 - Task generation and prioritization

### Core Capabilities

- **Persistent Memory** 💾 - Maintains context across AI sessions
- **Strategic Planning** 📊 - Project analysis and recommendations
- **Pattern Detection** 🔍 - Identifies code patterns and potential issues
- **File System Monitoring** 📡 - Tracks file changes in real-time
- **Code Intelligence** 🧠 - Security detection and architecture insights
- **Privacy-First** 🔒 - All data stays local on your machine

## 💡 How It Works

Copper Sun Brass creates a `.brass/` directory in your project containing:
- **Project context** that persists across AI sessions
- **Continuous analysis** by four specialized AI agents
- **Strategic insights** and recommendations
- **Development patterns** and best practices

When you work with Claude Code (or other AI assistants), they can access this context to provide much better, more informed assistance.

## 📖 Documentation

Complete documentation available at: **https://brass.coppersun.dev**

### Essential Commands
```bash
brass status        # Check system status
brass init          # Initialize project
brass insights      # Get AI recommendations  
brass refresh       # Update project analysis
brass scout scan    # Scan for code issues
brass legal         # View legal documents
brass --help        # See all commands
```

## 🔧 Requirements

- **Python**: 3.8 or later
- **Operating System**: macOS, Linux, Windows (WSL)
- **Claude API Key**: Required for AI functionality

## 🛡️ License & Pricing

- **Free Trial**: 15 days, full features
- **Pro**: $15/month after trial
- **Privacy**: All data stays local, no telemetry

Purchase and legal information: **https://brass.coppersun.dev/legal**

## 🌟 Why Copper Sun Brass?

Traditional development tools are stateless. AI agents forget context between sessions. Copper Sun Brass solves this by providing:

1. **Persistent Intelligence** - Never lose context between AI sessions
2. **Strategic Thinking** - Goes beyond syntax checking to architectural insights
3. **Adaptive Learning** - Improves understanding of your project over time
4. **AI-Native Design** - Built specifically for AI coding assistants

## 🆘 Getting Help

- **Documentation**: https://brass.coppersun.dev
- **Installation Issues**: Try the troubleshooting guide at https://brass.coppersun.dev/install
- **Support**: support@coppersuncreative.com

## 📊 Status

- **Version**: 2.1.19
- **Status**: Beta
- **Python**: 3.8+
- **License**: Proprietary (see https://brass.coppersun.dev/legal)

## 🙏 Acknowledgments

**Third-Party Services:**
- **Claude API** - AI analysis capabilities (Anthropic PBC)
- **HuggingFace Transformers** - Model infrastructure (Apache 2.0)

**Disclaimer:**
Claude and Claude Code are products of Anthropic PBC. Brass is an independent development intelligence tool that works with various AI coding assistants, including Claude Code, and is not affiliated with Anthropic.

---

**Ready to enhance your AI development workflow?** 🚀

```bash
curl -fsSL https://brass.coppersun.dev/setup | bash
```

*Built with ❤️ for AI agents and the developers who work with them.*
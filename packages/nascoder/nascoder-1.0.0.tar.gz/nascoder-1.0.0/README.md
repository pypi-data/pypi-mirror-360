# 🚀 NasCoder

**AI Assistant powered by AWS Bedrock with Claude models**

NasCoder is a powerful command-line AI assistant that brings the capabilities of Claude AI models directly to your terminal through AWS Bedrock.

```
███╗   ██╗ █████╗ ███████╗ ██████╗ ██████╗ ██████╗ ███████╗██████╗ 
████╗  ██║██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
██╔██╗ ██║███████║███████╗██║     ██║   ██║██║  ██║█████╗  ██████╔╝
██║╚██╗██║██╔══██║╚════██║██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗
██║ ╚████║██║  ██║███████║╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║
╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
```

## ✨ Features

- 🤖 **Multiple Claude Models**: Support for Claude-3 Opus, Sonnet, and Haiku
- 🔐 **Interactive Authentication**: Secure AWS credential management
- 🎨 **Beautiful CLI Interface**: Rich terminal experience with colors and formatting
- 🔄 **Model Switching**: Easy switching between different AI models
- 💬 **Conversation History**: Maintains context throughout your session
- 🚀 **Easy Installation**: One-command installation via pip

## 🚀 Quick Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install nascoder
```

### Option 2: Install from GitHub
```bash
pip install git+https://github.com/freelancernasim/nascoder.git
```

### Option 3: Development Installation
```bash
git clone https://github.com/freelancernasim/nascoder.git
cd nascoder
pip install -e .
```

## 🔧 Setup

1. **Install NasCoder** (see installation options above)

2. **Configure AWS Credentials** (one of these methods):
   ```bash
   # Method 1: AWS CLI
   aws configure
   
   # Method 2: Environment Variables
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   
   # Method 3: Use /auth command in NasCoder (interactive)
   ```

3. **Ensure Bedrock Access**: Make sure your AWS account has access to Amazon Bedrock and Claude models

## 🎯 Usage

### Start NasCoder
```bash
nascoder
```

### Interactive Commands
- `/auth` - Authenticate with AWS credentials interactively
- `/models` - List all available AI models
- `/switch claude-3-sonnet` - Switch to a different model
- `/status` - Check authentication and current model status
- `/clear` - Clear conversation history
- `/help` - Show all available commands
- `/quit` - Exit NasCoder

### Example Session
```
$ nascoder

███╗   ██╗ █████╗ ███████╗ ██████╗ ██████╗ ██████╗ ███████╗██████╗ 
████╗  ██║██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
██╔██╗ ██║███████║███████╗██║     ██║   ██║██║  ██║█████╗  ██████╔╝
██║╚██╗██║██╔══██║╚════██║██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗
██║ ╚████║██║  ██║███████║╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║
╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝

┌─ NasCoder v1.0 - AI Assistant powered by AWS Bedrock ─┐
│ Status: Authenticated                                  │
│ Current Model: claude-3-opus                          │
│ Type /help for commands or /quit to exit             │
└───────────────────────────────────────────────────────┘

You: Hello! Can you help me write a Python function?

NasCoder: I'd be happy to help you write a Python function! What specific functionality are you looking to implement?

You: /switch claude-3-sonnet
Switched to claude-3-sonnet

You: /quit
Goodbye!
```

## 🤖 Available Models

- **claude-3-opus** - Most capable model, best for complex tasks
- **claude-3-sonnet** - Balanced performance and speed
- **claude-3-haiku** - Fastest model, great for quick responses

## 📋 Requirements

- Python 3.8 or higher
- AWS account with Bedrock access
- AWS credentials configured
- Internet connection

## 🛠️ Development

### Local Development Setup
```bash
git clone https://github.com/freelancernasim/nascoder.git
cd nascoder
pip install -r requirements.txt
python -m nascoder.cli
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/freelancernasim/nascoder/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/freelancernasim/nascoder/issues)
- 📧 **Contact**: [contact@nascoder.dev](mailto:contact@nascoder.dev)

## 🌟 Star History

If you find NasCoder useful, please consider giving it a star on GitHub!

---

**Made with ❤️ by the NasCoder Team**

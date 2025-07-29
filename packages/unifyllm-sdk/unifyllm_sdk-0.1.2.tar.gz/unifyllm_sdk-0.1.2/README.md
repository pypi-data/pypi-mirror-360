# UniLLM - Unified API Gateway for Multiple LLM Providers

A unified API gateway that provides a single API key interface for multiple LLM providers (OpenAI, Anthropic, Google, etc.) with built-in usage tracking, billing, and a modern web dashboard.

## 🎯 What is UniLLM?

UniLLM solves the complexity of managing multiple LLM API keys by providing:
- **Single API Key**: Use one key to access all supported providers
- **Automatic Provider Selection**: Smart routing based on model names
- **Usage Tracking**: Built-in analytics and cost monitoring
- **Modern Dashboard**: React-based web interface for management
- **Credit System**: Pre-paid credits with automatic deduction

## 🚀 Quick Start

### 1. Install the Client Library
```bash
pip install unillm
```

### 2. Get Your API Key
1. Deploy the UniLLM API gateway (see [Deployment Guide](#deployment))
2. Register and get your API key from the dashboard
3. Set your API key: `export UNILLM_API_KEY="your-api-key-here"`

### 3. Basic Usage

#### Simple Chat
```python
from unillm import chat

response = chat(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.content)
```

#### Using the Client Class
```python
from unillm import UniLLM

client = UniLLM(api_key="your-api-key")

response = client.chat(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's 2+2?"}],
    temperature=0.7
)
print(response.content)
```

#### Conversation Example
```python
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "My name is Alice."},
    {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
    {"role": "user", "content": "What's my name?"}
]

response = client.chat(model="gpt-4", messages=conversation)
print(response.content)  # "Your name is Alice!"
```

## 📋 Supported Models

UniLLM automatically routes to the correct provider based on the model name:

- **OpenAI**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`, etc.
- **Anthropic**: `claude-3-sonnet`, `claude-3-haiku`, `claude-2.1`, etc.
- **Google**: `gemini-pro`, `gemini-pro-vision`, etc.
- **Mistral**: `mistral-large`, `mistral-medium`, etc.
- **Cohere**: `command`, `command-light`, etc.

## 🔧 Configuration

### Environment Variables
```bash
export UNILLM_API_KEY="your-api-key"
export UNILLM_BASE_URL="https://your-api-gateway.com"  # Optional, defaults to localhost:8000
```

### Client Configuration
```python
client = UniLLM(
    api_key="your-api-key",
    base_url="https://your-api-gateway.com"
)
```

## 📊 Usage Tracking

The client automatically tracks usage through your API gateway:
- Token usage (prompt, completion, total)
- Cost tracking per model
- Request history
- Analytics dashboard

## 🚀 Deployment

### Option 1: Deploy to Production (Recommended)

1. **Deploy the API Gateway**:
   ```bash
   # Clone and setup
   git clone https://github.com/yourusername/unillm
   cd unillm/api_gateway
   
   # Install dependencies
   pip install -r requirements_phase2.txt
   
   # Set environment variables
   export OPENAI_API_KEY="your-openai-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   # ... other provider keys
   
   # Run the server
   python main_phase2.py
   ```

2. **Deploy to Cloud**:
   - **Railway**: Easy deployment with automatic HTTPS
   - **Render**: Free tier available
   - **Heroku**: Simple deployment
   - **DigitalOcean**: More control

3. **Update Client Base URL**:
   ```python
   client = UniLLM(
       api_key="your-api-key",
       base_url="https://your-deployed-api.com"
   )
   ```

### Option 2: Local Development

1. **Start the API Gateway**:
   ```bash
   cd api_gateway
   python main_phase2.py
   ```

2. **Use the Client**:
   ```python
   client = UniLLM(api_key="your-api-key")  # Uses localhost:8000 by default
   ```

## 🎨 Dashboard

Access the modern React dashboard for:
- **User Management**: Register, login, manage API keys
- **Usage Analytics**: Real-time usage statistics
- **Billing**: Credit purchase and management
- **Chat Interface**: Test models directly
- **API Keys**: Manage your keys

### Launch Dashboard
```bash
cd api_gateway
python launch_dashboard.py
```

Then visit: http://localhost:8501

## 📚 Examples

See the `examples/` directory for more usage examples:

- `simple_client_example.py` - Basic usage examples
- `advanced_usage.py` - Advanced features and patterns

## 🧪 Testing

Test your setup:
```bash
# Test the client library
python test_client_library.py

# Test the API gateway
cd api_gateway
python test_phase2.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/unillm/issues)
- **Documentation**: [GitHub Wiki](https://github.com/yourusername/unillm/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/unillm/discussions)

## 🗺️ Roadmap

- [ ] Streaming support
- [ ] More provider integrations
- [ ] Advanced analytics
- [ ] Team management
- [ ] API rate limiting
- [ ] Webhook support

---

**UniLLM** - Simplify your LLM integration with a unified API gateway. 
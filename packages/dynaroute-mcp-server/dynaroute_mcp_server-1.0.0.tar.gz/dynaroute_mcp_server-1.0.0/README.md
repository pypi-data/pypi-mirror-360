# DynaRoute MCP Server

A Model Context Protocol (MCP) server that provides intelligent chat completions with automatic model routing and cost optimization through DynaRoute.

## Features

- 🧠 **Intelligent Model Routing**: Automatically routes queries to the most cost-effective model while maintaining quality
- 💰 **Cost Optimization**: Save up to 70% compared to premium models like GPT-4o
- 📊 **Detailed Analytics**: Get comprehensive metrics including token usage, costs, and performance data
- 🔍 **Routing Intelligence**: See exactly which model was selected and why
- ⚡ **Easy Integration**: Works seamlessly with Claude Desktop, Cursor, and other MCP-compatible clients

## Installation

Install via pip:

```bash
pip install dynaroute-mcp-server
```

## Quick Start

1. **Get your DynaRoute API key** from [DynaRoute](https://dynaroute.com)

2. **Set your API key**:
   ```bash
   export DYNAROUTE_API_KEY=your_api_key_here
   ```

3. **Configure Claude Desktop** by adding this to your `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "dynaroute": {
         "command": "dynaroute-mcp-server",
         "env": {
           "DYNAROUTE_API_KEY": "your_api_key_here"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** and start using DynaRoute!

## Usage

Once configured, you can use DynaRoute in Claude Desktop by:

- **Asking for AI responses**: "Use DynaRoute to explain quantum computing"
- **Requesting cost analysis**: "Get a cost-optimized response about machine learning"
- **Explicit tool usage**: "Use the DynaRoute tool to answer this question"

## Example Output

When you use the DynaRoute tool, you'll get:

```
🤖 DynaRoute Response:
[Your AI response content here]

📊 PERFORMANCE METRICS:
• Model Used: gcp-gemini-2.0-flash-thinking
• Response Time: 2.5 seconds
• Request ID: chatcmpl-xyz123

🔢 TOKEN USAGE:
• Input Tokens: 25
• Output Tokens: 150
• Total Tokens: 175

💰 COST BREAKDOWN:
• Input Cost: $0.000012
• Output Cost: $0.000045
• Total Cost: $0.000057

📈 COST SAVINGS vs GPT-4o:
• GPT-4o Equivalent Cost: $0.000175
• Your Actual Cost: $0.000057
• Money Saved: $0.000118
• Savings Percentage: 67.4%

✅ EFFICIENCY SUMMARY: DynaRoute saved you 67.4% compared to GPT-4o while maintaining quality!
```

## Configuration

### Environment Variables

- `DYNAROUTE_API_KEY`: Your DynaRoute API key (required)

### Tool Parameters

The `dynaroute_chat` tool accepts:

- `messages`: Array of conversation messages (required)
- `level_override`: Override complexity level 1-5 (optional)

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "dynaroute": {
      "command": "dynaroute-mcp-server",
      "env": {
        "DYNAROUTE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Other MCP Clients

### Cursor IDE
Add to your Cursor settings:
```json
{
  "mcp": {
    "servers": {
      "dynaroute": {
        "command": "dynaroute-mcp-server",
        "env": {
          "DYNAROUTE_API_KEY": "your_api_key_here"
        }
      }
    }
  }
}
```

### Custom Usage
You can also import and use the server programmatically:

```python
import asyncio
from dynaroute_mcp import DynaRouteMCPServer

async def main():
    server = DynaRouteMCPServer(api_key="your_api_key")
    await server.run()

asyncio.run(main())
```

## Requirements

- Python 3.8+
- DynaRoute API key
- MCP-compatible client (Claude Desktop, Cursor, etc.)

## Dependencies

- `mcp`: Model Context Protocol implementation
- `dynaroute`: Official DynaRoute Python client

## License

MIT License

## Support

- 📧 Email: abraar237@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/abraar237/dynaroute-mcp-server/issues)
- 📖 Documentation: [GitHub README](https://github.com/abraar237/dynaroute-mcp-server)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### 1.0.0
- Initial release
- DynaRoute integration with MCP
- Cost optimization and analytics
- Claude Desktop support
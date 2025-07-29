# A collection of ISEK examples
Here we show you how to use isek to quickly build an agent, and how to use isek to build your distributed agent system

---

## 📦 Installation

```bash
  pip install isek
```

## 🧪 Understanding how ISEK works

- [Fast Create Agent](create_agent) - Show you how to quickly build a single agent/distributed agent
- [Building Customized Agent](create_agent_by_config) - Show you more features of ISEK agent and customize your own agent
- [Custom Tool Agent](loading_tool) - Show you how to load and call custom tools on agent
- [Deep Thinking Agent](deep_think_agent) - Show you the deep thinking ability of ISEK agent and some creative apps

## 🔧 Tool Integration

### FastMCP Toolkit

Connect to MCP servers for external tool access.

#### Quick Start

```bash
pip install fastmcp
export GITHUB_TOKEN="your_github_token"
```

```python
from isek.tools.fastmcp_toolkit import fastmcp_tools

# Use in agent
agent = IsekAgent(
    tools=[fastmcp_tools],
    # ... other config
)
```

#### Examples
- [FastMCP Tool Agent](lv2_fastmcp_tool_agent.py) - Complete example

#### Available MCP Servers
- **GitHub Copilot MCP**: `
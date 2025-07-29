# 🤖 AA Kit

**The Universal AI Agent Framework for the MCP Era**

AA Kit is a Python framework designed to build AI agents that naturally compose into ecosystems. Every agent is simultaneously a standalone agent, an MCP server, and an MCP client - creating true interoperability across the entire AI landscape.

## 🎯 Core Philosophy

> **"Make simple things simple, complex things possible, and everything interoperable"**

AA Kit fills the gap left by existing frameworks by being:
- **Simple by default** - Create agents in 3 lines of code
- **MCP-native** - Universal compatibility with all AI tools and frameworks
- **Composition-first** - Agents naturally work together
- **Deploy-ready** - Production deployment in one line

## 🚀 Quick Start

```python
from aakit import Agent

# Create an agent
agent = Agent(
    name="support_agent",
    instruction="You are a helpful customer support agent",
    model="gpt-4"
)

# Use it
response = agent.chat("I need help with my order")

# Deploy it
agent.serve()  # REST API + WebSocket + MCP server on localhost:8000
```

## 📋 Table of Contents

- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Key Differentiators](#key-differentiators)
- [Developer Experience](#developer-experience)
- [Architecture](#architecture)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 📦 Installation

```bash
pip install aa-kit
```

**Requirements:**
- Python 3.9+
- At least one LLM API key (OpenAI, Anthropic, etc.)

## 🧠 Core Concepts

### Agents are Simple Constructors

```python
from aakit import Agent

agent = Agent(
    name="my_agent",                    # Unique identifier
    instruction="Your role description", # System prompt
    model="gpt-4",                      # LLM to use
    tools=[],                           # Optional tools
    memory=None,                        # Optional memory backend
    reasoning="simple"                  # Reasoning pattern
)
```

### Tools are Always MCP

```python
# Define tools as regular Python functions
def search_database(query: str) -> str:
    return f"Results for: {query}"

def create_ticket(issue: str) -> str:
    return f"Ticket #{random.randint(1000, 9999)} created"

# Agent automatically converts them to MCP
agent = Agent(
    name="support",
    instruction="You help customers",
    model="gpt-4",
    tools=[search_database, create_ticket]
)
```

### Every Agent IS an MCP Server

```python
# Your agent is automatically an MCP server
agent.serve_mcp(port=8080)

# Other agents can now use it as a tool
other_agent = Agent(
    name="manager", 
    instruction="You coordinate support",
    model="gpt-4",
    tools=["http://localhost:8080"]  # Use the support agent
)
```

## 🔥 Key Differentiators

### 1. **MCP-First Architecture**
- Every tool speaks MCP protocol
- Every agent IS an MCP server
- Universal compatibility with all AI frameworks

### 2. **Built-in Reasoning Patterns**
```python
# Choose how your agent thinks
simple_agent = Agent("You chat", model="gpt-4", reasoning="simple")
react_agent = Agent("You solve problems", model="gpt-4", reasoning="react")
cot_agent = Agent("You analyze", model="gpt-4", reasoning="chain_of_thought")
```

### 3. **Stateless + External Memory**
```python
# Memory is injected, not built-in
agent = Agent(
    name="assistant",
    instruction="You remember conversations",
    model="gpt-4",
    memory="redis://localhost"  # Any storage backend
)
```

### 4. **Zero-Config LLM Management**
```python
# Automatic model selection and fallbacks
agent = Agent("You help", model="auto")  # OpenAI → Anthropic → Local
agent = Agent("You help", model=["gpt-4", "claude-3"])  # Fallback chain
```

### 5. **True Interoperability**
```python
# AA Kit agents work in any framework
my_agent = Agent("Helper", model="gpt-4")

# Use in LangChain
langchain_tool = Tool.from_mcp(my_agent.mcp_endpoint)

# Use in CrewAI
crewai_tool = MCPTool(my_agent.mcp_endpoint)
```

## 👨‍💻 Developer Experience

### Simple Creation
```python
# Minimal agent
agent = Agent("You help with math", model="gpt-4")

# With tools
calculator = Agent(
    name="calculator",
    instruction="You solve math problems",
    model="gpt-4",
    tools=[add, multiply, divide]
)

# With memory
personal_assistant = Agent(
    name="assistant",
    instruction="You are my personal assistant",
    model="gpt-4", 
    memory="sqlite://assistant.db"
)
```

### Easy Composition
```python
# Agents use other agents naturally
researcher = Agent("You research topics", model="gpt-4", tools=[web_search])
writer = Agent("You write articles", model="claude-3")

def create_content(topic):
    research = researcher.chat(f"Research {topic}")
    article = writer.chat(f"Write an article about: {research}")
    return article
```

### One-Line Deployment
```python
# Local development
agent.serve()  # localhost:8000

# Production
agent.deploy(mode="serverless")  # Auto-scaling cloud deployment
```

## 🏗️ Architecture

### Core Components

```
┌─────────────────┐
│     Agent       │
├─────────────────┤
│ • Name          │
│ • Instruction   │
│ • Model         │
│ • Tools (MCP)   │
│ • Memory        │
│ • Reasoning     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  MCP Server     │
├─────────────────┤
│ • Auto-generated│
│ • Standard API  │
│ • Tool calls    │
│ • Responses     │
└─────────────────┘
```

### Reasoning Patterns

1. **Simple**: Direct LLM call, no tool use
2. **ReAct**: Reason → Act → Observe loop with tools
3. **Chain of Thought**: Think step-by-step before responding
4. **Custom**: Define your own reasoning pattern

### Memory Backends

- **None**: Stateless (default)
- **Local**: In-memory for development
- **Redis**: Fast external memory
- **SQLite**: File-based persistence  
- **PostgreSQL**: Production database
- **Custom**: Bring your own storage

## 📚 Examples

### Customer Support Agent
```python
from aakit import Agent

def search_orders(customer_id: str) -> str:
    return f"Orders for {customer_id}: [Order #1, Order #2]"

def create_ticket(issue: str) -> str:
    return f"Support ticket created: {issue}"

support_agent = Agent(
    name="support",
    instruction="""You are a helpful customer support agent. 
    Help customers with orders and issues. Be empathetic and solution-focused.""",
    model="gpt-4",
    tools=[search_orders, create_ticket],
    reasoning="react"
)

# Use the agent
response = support_agent.chat("I can't find my order #12345")
print(response)
```

### Multi-Agent Content Team
```python
from aakit import Agent

# Define specialized agents
researcher = Agent(
    name="researcher",
    instruction="You research topics thoroughly using web search",
    model="gpt-4",
    tools=[web_search]
)

writer = Agent(
    name="writer", 
    instruction="You write engaging, well-structured articles",
    model="claude-3"
)

editor = Agent(
    name="editor",
    instruction="You review and improve written content",
    model="gpt-4"
)

# Expose team as MCP services
from aakit import serve_mcp

serve_mcp({
    "researcher": researcher,
    "writer": writer, 
    "editor": editor
}, port=8080)

# Now other agents can use the entire team
coordinator = Agent(
    name="coordinator",
    instruction="You coordinate content creation using the research, writing, and editing team",
    model="gpt-4",
    tools=["http://localhost:8080/researcher", 
           "http://localhost:8080/writer",
           "http://localhost:8080/editor"]
)
```

### Code Analysis Agent
```python
def analyze_code(code: str) -> str:
    """Analyze code for potential issues"""
    return f"Analysis of {len(code)} characters of code..."

def suggest_improvements(analysis: str) -> str:
    """Suggest code improvements"""
    return f"Improvements based on: {analysis[:50]}..."

code_agent = Agent(
    name="code_reviewer",
    instruction="""You are a senior code reviewer. 
    Analyze code for bugs, security issues, and best practices.""",
    model="gpt-4",
    tools=[analyze_code, suggest_improvements],
    reasoning="chain_of_thought"
)

# Use with different models for cost optimization
quick_review = Agent(
    name="quick_reviewer",
    instruction="You do quick code reviews",
    model="gpt-3.5-turbo",
    tools=[analyze_code]
)
```

## 📖 API Reference

### Agent Class

```python
class Agent:
    def __init__(
        self,
        name: str,
        instruction: str,
        model: str | List[str] = "auto",
        tools: List[Callable | str] = None,
        memory: str | MemoryBackend = None,
        reasoning: str = "simple",
        temperature: float = 0.7,
        max_tokens: int = None,
        rate_limit: int = None
    )
    
    def chat(self, message: str) -> str:
        """Send a message to the agent"""
        
    def serve(self, port: int = 8000) -> None:
        """Start REST API + WebSocket server"""
        
    def serve_mcp(self, port: int = 8080) -> None:
        """Start MCP server"""
        
    def deploy(self, mode: str = "serverless") -> str:
        """Deploy to cloud"""
        
    @property
    def mcp_endpoint(self) -> str:
        """Get MCP endpoint URL"""
```

### Utility Functions

```python
from aakit import serve_mcp, discover_mcp_tools

# Serve multiple agents as MCP
serve_mcp({
    "agent1": agent1,
    "agent2": agent2
}, port=8080)

# Discover available MCP tools
tools = discover_mcp_tools("http://localhost:8080")
```

## 🚀 Deployment

### Local Development
```python
# Start agent with web UI
agent.serve()  # http://localhost:8000

# MCP endpoint available at
# http://localhost:8000/mcp
```

### Production Deployment
```python
# Serverless deployment (auto-scaling)
agent.deploy(mode="serverless")

# Container deployment
agent.deploy(mode="container")

# Kubernetes deployment  
agent.deploy(mode="kubernetes")
```

### Environment Variables
```bash
# LLM Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Memory Configuration
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost/db

# AA Kit Configuration
OMNIAGENT_DEFAULT_MODEL=gpt-4
OMNIAGENT_DEBUG=true
```

## 🛠️ Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/josharsh/aa-kit
cd aa-kit
pip install -e ".[dev]"
pytest
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- [Documentation](https://aa-kit.dev/docs)
- [Examples](https://github.com/josharsh/aa-kit-examples)
- [Discord Community](https://discord.gg/aa-kit)
- [Twitter](https://twitter.com/aa-kit_dev)

---

**AA Kit - Building the future of AI agent interoperability** 🚀
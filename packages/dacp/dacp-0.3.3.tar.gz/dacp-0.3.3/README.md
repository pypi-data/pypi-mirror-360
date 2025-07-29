# DACP - Declarative Agent Communication Protocol

A Python library for managing LLM/agent communications and tool function calls following the OAS Open Agent Specification.

## Installation

```bash
pip install -e .
```

## Quick Start

```python
import dacp

# Create an orchestrator to manage agents
orchestrator = dacp.Orchestrator()

# Create and register an agent
class MyAgent:
    def handle_message(self, message):
        return {"response": f"Hello {message.get('name', 'World')}!"}

agent = MyAgent()
orchestrator.register_agent("my-agent", agent)

# Send a message to the agent
response = orchestrator.send_message("my-agent", {"name": "Alice"})
print(response)  # {"response": "Hello Alice!"}

# Use built-in tools
result = dacp.file_writer("./output/greeting.txt", "Hello, World!")
print(result["message"])  # "Successfully wrote 13 characters to ./output/greeting.txt"

# Use intelligence providers (supports multiple LLM providers)
intelligence_config = {
    "engine": "anthropic",
    "model": "claude-3-haiku-20240307",
    "api_key": "your-api-key"  # or set ANTHROPIC_API_KEY env var
}
response = dacp.invoke_intelligence("What is the weather like today?", intelligence_config)

# Or use the legacy call_llm function for OpenAI
response = dacp.call_llm("What is the weather like today?")
```

## Features

- **Agent Orchestration**: Central management of multiple agents with message routing
- **Tool Registry**: Register and manage custom tools for LLM agents
- **Built-in Tools**: Includes a `file_writer` tool that automatically creates parent directories
- **LLM Integration**: Built-in support for OpenAI models (extensible)
- **Protocol Parsing**: Parse and validate agent responses
- **Tool Execution**: Safe execution of registered tools
- **Conversation History**: Track and query agent interactions
- **OAS Compliance**: Follows Open Agent Specification standards

## API Reference

### Orchestrator

- `Orchestrator()`: Create a new orchestrator instance
- `register_agent(agent_id: str, agent) -> None`: Register an agent
- `unregister_agent(agent_id: str) -> bool`: Remove an agent
- `send_message(agent_id: str, message: Dict) -> Dict`: Send message to specific agent
- `broadcast_message(message: Dict, exclude_agents: List[str] = None) -> Dict`: Send message to all agents
- `get_conversation_history(agent_id: str = None) -> List[Dict]`: Get conversation history
- `clear_history() -> None`: Clear conversation history
- `get_session_info() -> Dict`: Get current session information

### Tools

- `register_tool(tool_id: str, func)`: Register a new tool
- `run_tool(tool_id: str, args: Dict) -> dict`: Execute a registered tool
- `TOOL_REGISTRY`: Access the current tool registry
- `file_writer(path: str, content: str) -> dict`: Write content to file, creating directories automatically

### Intelligence (Multi-Provider LLM Support)

- `invoke_intelligence(prompt: str, config: dict) -> str`: Call any supported LLM provider
- `validate_config(config: dict) -> bool`: Validate intelligence configuration
- `get_supported_engines() -> list`: Get list of supported engines

### LLM (Legacy)

- `call_llm(prompt: str, model: str = "gpt-4") -> str`: Call OpenAI (legacy function)

### Logging

- `enable_info_logging(log_file: str = None) -> None`: Enable info-level logging with emoji format
- `enable_debug_logging(log_file: str = None) -> None`: Enable debug logging with detailed format  
- `enable_quiet_logging() -> None`: Enable only error and critical logging
- `setup_dacp_logging(level, format_style, include_timestamp, log_file) -> None`: Custom logging setup
- `set_dacp_log_level(level: str) -> None`: Change log level dynamically
- `disable_dacp_logging() -> None`: Disable all DACP logging
- `enable_dacp_logging() -> None`: Re-enable DACP logging

### Protocol

- `parse_agent_response(response: str | dict) -> dict`: Parse agent response
- `is_tool_request(msg: dict) -> bool`: Check if message is a tool request
- `get_tool_request(msg: dict) -> tuple[str, dict]`: Extract tool request details
- `wrap_tool_result(name: str, result: dict) -> dict`: Wrap tool result for agent
- `is_final_response(msg: dict) -> bool`: Check if message is a final response
- `get_final_response(msg: dict) -> dict`: Extract final response

## Agent Development

### Creating an Agent

Agents must implement a `handle_message` method:

```python
import dacp

class GreetingAgent:
    def handle_message(self, message):
        name = message.get("name", "World")
        task = message.get("task")
        
        if task == "greet":
            return {"response": f"Hello, {name}!"}
        elif task == "farewell":
            return {"response": f"Goodbye, {name}!"}
        else:
            return {"error": f"Unknown task: {task}"}

# Register the agent
orchestrator = dacp.Orchestrator()
agent = GreetingAgent()
orchestrator.register_agent("greeter", agent)

# Use the agent
response = orchestrator.send_message("greeter", {
    "task": "greet", 
    "name": "Alice"
})
print(response)  # {"response": "Hello, Alice!"}
```

### Agent Base Class

You can also inherit from the `Agent` base class:

```python
import dacp

class MyAgent(dacp.Agent):
    def handle_message(self, message):
        return {"processed": message}
```

### Tool Requests from Agents

Agents can request tool execution by returning properly formatted responses:

```python
class ToolUsingAgent:
    def handle_message(self, message):
        if message.get("task") == "write_file":
            return {
                "tool_request": {
                    "name": "file_writer",
                    "args": {
                        "path": "./output/agent_file.txt",
                        "content": "Hello from agent!"
                    }
                }
            }
        return {"response": "Task completed"}

# The orchestrator will automatically execute the tool and return results
orchestrator = dacp.Orchestrator()
agent = ToolUsingAgent()
orchestrator.register_agent("file-agent", agent)

response = orchestrator.send_message("file-agent", {"task": "write_file"})
# Tool will be executed automatically
```

## Intelligence Configuration

DACP supports multiple LLM providers through the `invoke_intelligence` function. Configure different providers using a configuration dictionary:

### OpenAI

```python
import dacp

openai_config = {
    "engine": "openai",
    "model": "gpt-4",  # or "gpt-3.5-turbo", "gpt-4-turbo", etc.
    "api_key": "your-openai-key",  # or set OPENAI_API_KEY env var
    "endpoint": "https://api.openai.com/v1",  # optional, uses default
    "temperature": 0.7,  # optional, default 0.7
    "max_tokens": 150   # optional, default 150
}

response = dacp.invoke_intelligence("Explain quantum computing", openai_config)
```

### Anthropic (Claude)

```python
anthropic_config = {
    "engine": "anthropic", 
    "model": "claude-3-haiku-20240307",  # or other Claude models
    "api_key": "your-anthropic-key",  # or set ANTHROPIC_API_KEY env var
    "endpoint": "https://api.anthropic.com",  # optional, uses default
    "temperature": 0.7,
    "max_tokens": 150
}

response = dacp.invoke_intelligence("Write a poem about AI", anthropic_config)
```

### Azure OpenAI

```python
azure_config = {
    "engine": "azure",
    "model": "gpt-4",  # Your deployed model name
    "api_key": "your-azure-key",  # or set AZURE_OPENAI_API_KEY env var  
    "endpoint": "https://your-resource.openai.azure.com",  # or set AZURE_OPENAI_ENDPOINT env var
    "api_version": "2024-02-01"  # optional, default provided
}

response = dacp.invoke_intelligence("Analyze this data", azure_config)
```

### Local LLMs (Ollama, etc.)

```python
# For Ollama (default local setup)
local_config = {
    "engine": "local",
    "model": "llama2",  # or any model available in Ollama
    "endpoint": "http://localhost:11434/api/generate",  # Ollama default
    "temperature": 0.7,
    "max_tokens": 150
}

# For custom local APIs
custom_local_config = {
    "engine": "local", 
    "model": "custom-model",
    "endpoint": "http://localhost:8080/generate",  # Your API endpoint
    "temperature": 0.7,
    "max_tokens": 150
}

response = dacp.invoke_intelligence("Tell me a story", local_config)
```

### Configuration from OAS YAML

You can load configuration from OAS (Open Agent Specification) YAML files:

```python
import yaml
import dacp

# Load config from YAML file
with open('agent_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

intelligence_config = config.get('intelligence', {})
response = dacp.invoke_intelligence("Hello, AI!", intelligence_config)
```

### Installation for Different Providers

Install optional dependencies for the providers you need:

```bash
# For OpenAI
pip install dacp[openai]

# For Anthropic  
pip install dacp[anthropic]

# For all providers
pip install dacp[all]

# For local providers (requests is already included in base install)
pip install dacp[local]
```

## Built-in Tools

### file_writer

The `file_writer` tool automatically creates parent directories and writes content to files:

```python
import dacp

# This will create the ./output/ directory if it doesn't exist
result = dacp.file_writer("./output/file.txt", "Hello, World!")

if result["success"]:
    print(f"File written: {result['path']}")
    print(f"Message: {result['message']}")
else:
    print(f"Error: {result['error']}")
```

**Features:**
- ✅ Automatically creates parent directories
- ✅ Handles Unicode content properly
- ✅ Returns detailed success/error information
- ✅ Safe error handling

## Logging

DACP includes comprehensive logging to help you monitor agent operations, tool executions, and intelligence calls.

### Quick Setup

```python
import dacp

# Enable info-level logging with emoji format (recommended for production)
dacp.enable_info_logging()

# Enable debug logging for development (shows detailed information)
dacp.enable_debug_logging()

# Enable quiet logging (errors only)
dacp.enable_quiet_logging()
```

### Custom Configuration

```python
# Full control over logging configuration
dacp.setup_dacp_logging(
    level="INFO",                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format_style="emoji",            # "simple", "detailed", "emoji"
    include_timestamp=True,          # Include timestamps
    log_file="dacp.log"              # Optional: also log to file
)

# Change log level dynamically
dacp.set_dacp_log_level("DEBUG")

# Disable/enable logging
dacp.disable_dacp_logging()
dacp.enable_dacp_logging()
```

### What Gets Logged

With logging enabled, you'll see:

- **🎭 Agent Registration**: When agents are registered/unregistered
- **📨 Message Routing**: Messages sent to agents and broadcast operations  
- **🔧 Tool Execution**: Tool calls, execution time, and results
- **🧠 Intelligence Calls**: LLM provider calls, configuration, and performance
- **❌ Errors**: Detailed error information with context
- **📊 Performance**: Execution times for operations

### Log Format Examples

**Emoji Format** (clean, production-friendly):
```
2025-07-02 09:54:58 - 🎭 Orchestrator initialized with session ID: session_1751414098
2025-07-02 09:54:58 - ✅ Agent 'demo-agent' registered successfully (type: MyAgent)
2025-07-02 09:54:58 - 📨 Sending message to agent 'demo-agent'
2025-07-02 09:54:58 - 🔧 Agent 'demo-agent' requested tool execution
2025-07-02 09:54:58 - 🛠️  Executing tool: 'file_writer' with args: {...}
2025-07-02 09:54:58 - ✅ Tool 'file_writer' executed successfully in 0.001s
```

**Detailed Format** (development/debugging):
```
2025-07-02 09:54:58 - dacp.orchestrator:89 - INFO - 📨 Sending message to agent 'demo-agent'
2025-07-02 09:54:58 - dacp.orchestrator:90 - DEBUG - 📋 Message content: {'task': 'greet'}
2025-07-02 09:54:58 - dacp.tools:26 - DEBUG - 🛠️  Executing tool 'file_writer' with args: {...}
```

### Example Usage

```python
import dacp

# Enable logging
dacp.enable_info_logging()

# Create and use components - logging happens automatically
orchestrator = dacp.Orchestrator()
agent = MyAgent()
orchestrator.register_agent("my-agent", agent)

# This will log the message sending, tool execution, etc.
response = orchestrator.send_message("my-agent", {"task": "process"})
```

## Usage Patterns: Open Agent Spec vs Independent Client Usage

DACP supports two primary usage patterns: integration with Open Agent Specification (OAS) projects and independent client usage. Both provide full access to DACP's capabilities but with different integration approaches.

### Open Agent Specification (OAS) Integration

**For OAS developers:** DACP integrates seamlessly with generated agents through YAML configuration and automatic setup.

#### YAML Configuration Pattern

```yaml
# agent_config.yaml (Open Agent Specification)
apiVersion: "v1"
kind: "Agent"
metadata:
  name: "data-analysis-agent"
  type: "smart_analysis"

# DACP automatically configures logging
logging:
  enabled: true
  level: "INFO"
  format_style: "emoji"
  log_file: "./logs/agent.log"
  env_overrides:
    level: "DACP_LOG_LEVEL"

# Multi-provider intelligence configuration
intelligence:
  engine: "anthropic"
  model: "claude-3-haiku-20240618"
  # API key from environment: ANTHROPIC_API_KEY

# Define agent capabilities
capabilities:
  - name: "analyze_data"
    description: "Analyze datasets and generate insights"
  - name: "generate_report"
    description: "Generate analysis reports"
```

#### Generated Agent Code (OAS Pattern)

```python
# Generated by OAS with DACP integration
import dacp
import yaml

class DataAnalysisAgent(dacp.Agent):
    def __init__(self, config_path="agent_config.yaml"):
        # DACP auto-configures logging from YAML
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Automatic logging setup
        self.setup_logging()
        
        # Load intelligence configuration
        self.intelligence_config = self.config.get('intelligence', {})
    
    def setup_logging(self):
        """Auto-configure DACP logging from YAML config."""
        logging_config = self.config.get('logging', {})
        if logging_config.get('enabled', False):
            dacp.setup_dacp_logging(
                level=logging_config.get('level', 'INFO'),
                format_style=logging_config.get('format_style', 'emoji'),
                log_file=logging_config.get('log_file')
            )
    
    def handle_message(self, message):
        """Handle capabilities defined in YAML."""
        task = message.get("task")
        
        if task == "analyze_data":
            return self.analyze_data(message)
        elif task == "generate_report":
            return self.generate_report(message)
        else:
            return {"error": f"Unknown task: {task}"}
    
    def analyze_data(self, message):
        """Analyze data using configured intelligence provider."""
        data = message.get("data", "No data provided")
        
        try:
            result = dacp.invoke_intelligence(
                f"Analyze this data and provide insights: {data}",
                self.intelligence_config
            )
            return {"response": result}
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def generate_report(self, message):
        """Generate reports using DACP's file_writer tool."""
        subject = message.get("subject", "report")
        data = message.get("data", "No data")
        
        return {
            "tool_request": {
                "name": "file_writer", 
                "args": {
                    "path": f"./reports/{subject}.txt",
                    "content": f"# Analysis Report: {subject}\n\nData: {data}\n"
                }
            }
        }

# Auto-generated main function
def main():
    # Zero-configuration setup
    orchestrator = dacp.Orchestrator()
    agent = DataAnalysisAgent()
    orchestrator.register_agent("data-analysis-agent", agent)
    
    print("🚀 OAS Agent running with DACP integration!")
    # Agent ready for messages via orchestrator

if __name__ == "__main__":
    main()
```

#### OAS Benefits

- ✅ **Zero Configuration**: Logging and intelligence work out of the box
- ✅ **YAML-Driven**: All configuration in standard OAS YAML format  
- ✅ **Auto-Generated**: Complete agents generated from specifications
- ✅ **Environment Overrides**: Runtime configuration via environment variables
- ✅ **Standardized**: Consistent interface across all OAS agents

### Independent Client Usage

**For independent developers:** Use DACP directly as a flexible agent router and orchestration platform.

#### Direct Integration Pattern

```python
import dacp
import os

class MyCustomAgent(dacp.Agent):
    """Independent client's custom agent."""
    
    def __init__(self):
        # Manual setup - full control
        self.setup_intelligence()
        self.setup_logging()
        
    def setup_intelligence(self):
        """Configure intelligence providers manually."""
        self.intelligence_configs = {
            "research": {
                "engine": "openai",
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY")
            },
            "analysis": {
                "engine": "anthropic", 
                "model": "claude-3-sonnet-20240229",
                "api_key": os.getenv("ANTHROPIC_API_KEY")
            },
            "local": {
                "engine": "local",
                "model": "llama2",
                "endpoint": "http://localhost:11434/api/generate"
            }
        }
    
    def setup_logging(self):
        """Configure logging manually."""
        dacp.enable_info_logging(log_file="./logs/custom_agent.log")
    
    def handle_message(self, message):
        """Custom business logic."""
        task = message.get("task")
        
        if task == "research_topic":
            return self.research_with_multiple_llms(message)
        elif task == "process_data":
            return self.multi_step_processing(message)
        elif task == "custom_workflow":
            return self.handle_custom_workflow(message)
        else:
            return {"error": f"Unknown task: {task}"}
    
    def research_with_multiple_llms(self, message):
        """Use multiple LLM providers for comprehensive research."""
        topic = message.get("topic", "AI Research")
        
        # Use different LLMs for different aspects
        research_prompt = f"Research the topic: {topic}"
        analysis_prompt = f"Analyze research findings for: {topic}"
        
        try:
            # Research with GPT-4
            research = dacp.invoke_intelligence(
                research_prompt, 
                self.intelligence_configs["research"]
            )
            
            # Analysis with Claude
            analysis = dacp.invoke_intelligence(
                f"Analyze: {research}",
                self.intelligence_configs["analysis"]
            )
            
            return {
                "research": research,
                "analysis": analysis,
                "status": "completed"
            }
        except Exception as e:
            return {"error": f"Research failed: {e}"}
    
    def multi_step_processing(self, message):
        """Multi-step workflow with tool chaining."""
        data = message.get("data", "sample data")
        
        # Step 1: Process and save data
        return {
            "tool_request": {
                "name": "file_writer",
                "args": {
                    "path": "./processing/input_data.txt",
                    "content": f"Raw data: {data}\nProcessed at: {dacp.time.time()}"
                }
            }
        }
        # In real implementation, would continue workflow in subsequent messages

# Independent client setup
def main():
    # Manual orchestrator setup
    orchestrator = dacp.Orchestrator()
    
    # Register multiple custom agents
    research_agent = MyCustomAgent()
    data_agent = MyCustomAgent()
    workflow_agent = MyCustomAgent()
    
    orchestrator.register_agent("researcher", research_agent)
    orchestrator.register_agent("processor", data_agent)  
    orchestrator.register_agent("workflow", workflow_agent)
    
    # Direct control over routing
    print("🚀 Independent client agents running!")
    
    # Example: Route complex task across multiple agents
    research_result = orchestrator.send_message("researcher", {
        "task": "research_topic",
        "topic": "Multi-Agent Systems"
    })
    
    processing_result = orchestrator.send_message("processor", {
        "task": "process_data", 
        "data": research_result
    })
    
    # Broadcast updates to all agents
    orchestrator.broadcast_message({
        "task": "status_update",
        "message": "Workflow completed"
    })

if __name__ == "__main__":
    main()
```

#### Advanced Independent Usage

```python
# Register custom tools for specialized business logic
def custom_data_processor(args):
    """Client's proprietary data processing tool."""
    data = args.get("data", [])
    algorithm = args.get("algorithm", "default")
    
    # Custom processing logic
    processed = [item * 2 for item in data if isinstance(item, (int, float))]
    
    return {
        "success": True,
        "processed_data": processed,
        "algorithm_used": algorithm,
        "count": len(processed)
    }

# Register with DACP
dacp.register_tool("custom_processor", custom_data_processor)

# Use in agents
class SpecializedAgent(dacp.Agent):
    def handle_message(self, message):
        if message.get("task") == "process_with_custom_tool":
            return {
                "tool_request": {
                    "name": "custom_processor",
                    "args": {
                        "data": message.get("data", []),
                        "algorithm": "proprietary_v2"
                    }
                }
            }
```

#### Independent Client Benefits

- ✅ **Full Control**: Manual configuration of all components
- ✅ **Flexible Architecture**: Design your own agent interactions
- ✅ **Custom Tools**: Register proprietary business logic tools
- ✅ **Multi-Provider**: Use different LLMs for different tasks
- ✅ **Direct API Access**: Call DACP functions directly when needed
- ✅ **Complex Workflows**: Build sophisticated multi-agent orchestrations

### Choosing Your Pattern

| Feature | OAS Integration | Independent Client |
|---------|----------------|-------------------|
| **Setup Complexity** | Minimal (auto-generated) | Manual (full control) |
| **Configuration** | YAML-driven | Programmatic |
| **Agent Generation** | Automatic from spec | Manual implementation |
| **Customization** | Template-based | Unlimited flexibility |
| **Best For** | Rapid prototyping, standard agents | Complex workflows, custom logic |
| **Learning Curve** | Low | Medium |

### Getting Started

**For OAS Integration:**
1. Add DACP logging section to your YAML spec
2. Generate agents with DACP base class
3. Agents work with zero additional configuration

**For Independent Usage:**
1. `pip install dacp` 
2. Create agents inheriting from `dacp.Agent`
3. Register with `dacp.Orchestrator()`
4. Build your custom workflows

Both patterns provide full access to DACP's capabilities: multi-provider LLM routing, tool execution, comprehensive logging, conversation history, and multi-agent orchestration.

## Development

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## License

MIT License

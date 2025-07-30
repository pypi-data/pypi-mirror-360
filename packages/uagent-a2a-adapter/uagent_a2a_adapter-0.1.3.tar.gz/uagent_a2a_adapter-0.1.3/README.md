## uAgent A2A Adapter

A powerful adapter for integrating A2A (Agent-to-Agent) frameworks with uAgents, enabling seamless communication between different AI agent ecosystems.

## Features

- 🔗 **Seamless Integration**: Connects A2A agents with the uAgents framework.
- 🚀 **Easy Setup**: Simple configuration and deployment process.
- 💬 **Chat Protocol**: Built-in support for agent-to-agent communication.
- 🔄 **Bidirectional Communication**: Supports full-duplex communication between agents.
- 🛡️ **Error Handling**: Robust error handling with fallback mechanisms.
<<<<<<< HEAD


=======
>>>>>>> 3b8a7593c050c8f4b9fff434a5439eaaf1465d0d


```
## Installation

### Basic Installation

```bash
pip install uagent-a2a-adapter
```
<<<<<<< HEAD


### With A2A Support

=======

### With A2A Support
>>>>>>> 3b8a7593c050c8f4b9fff434a5439eaaf1465d0d
```bash
pip install uagent-a2a-adapter[a2a]
```

### With All Optional Dependencies
<<<<<<< HEAD

=======
>>>>>>> 3b8a7593c050c8f4b9fff434a5439eaaf1465d0d
```bash
pip install uagent-a2a-adapter[all]
```

## Quick Start

Here's a simple example to get started:

```python
from dotenv import load_dotenv
from your_agent_executor import YourAgentExecutor  # Replace with your executor
from uagent_a2a_adapter import A2AAdapter

# Load environment variables
load_dotenv()

def main():
    # Initialize your agent executor
    executor = YourAgentExecutor()
    
    # Create the adapter
    adapter = A2AAdapter(
        agent_executor=executor,
        name="my_a2a_agent",
        description="My A2A agent with uAgents integration",
        port=8082,
        a2a_port=9997,
        mailbox=True,
        seed="my_agent_seed"
    )
    
    print("🚀 Starting A2A Agent...")
    adapter.run()

if __name__ == "__main__":
    main()
```

## Configuration

### A2AAdapter Parameters

- `agent_executor`: Your A2A agent executor instance.
- `name`: Name of your agent.
- `description`: Description of your agent's capabilities.
- `port`: Port for the uAgent (default: 8000).
- `a2a_port`: Port for the A2A server (default: 9999).
- `mailbox`: Enable mailbox functionality (default: True).
- `seed`: Seed for agent address generation (optional).

## Advanced Usage

### Using the Register Tool

```python
from uagent_a2a_adapter import A2ARegisterTool

tool = A2ARegisterTool()
result = tool.invoke({
    "agent_executor": your_executor,
    "name": "advanced_agent",
    "description": "An advanced A2A agent",
    "port": 8083,
    "a2a_port": 9998,
    "return_dict": True
})

print(f"Agent created: {result}")
```


## Supported Frameworks

The adapter supports integration with various AI frameworks through optional dependencies:

- **A2A**: Core A2A (Agent2Agent Protocol (A2A)) framework support.


## Communication Protocol

The adapter uses the uAgents chat protocol for communication:

1. **Message Reception**: Receives messages via uAgents chat protocol.
2. **A2A Processing**: Forwards messages to A2A agent for processing.
3. **Response Handling**: Returns processed responses through uAgents.
4. **Acknowledgments**: Automatically handles message acknowledgments.

## Error Handling

The adapter includes robust error handling:

- **Connection Failures**: Automatically falls back to direct executor calls.
- **Timeout Handling**: Configurable timeouts for HTTP requests.
- **Error Messages**: Detailed error messages for debugging.
- **Graceful Degradation**: Continues operation during partial failures.

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/gautammanak1/uagent-a2a-adapter.git
cd uagent-a2a-adapter

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy uagent_a2a_adapter
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=uagent_a2a_adapter

# Run specific test file
pytest tests/test_adapter.py
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Add tests.
5. Submit a pull request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Support

- **Issues**: [GitHub Issues](https://github.com/gautammanak1/uagent-a2a-adapter/issues)
<!-- - **Discussions**: [GitHub Discussions](https://github.com/gautammanak1/uagent-a2a-adapter/discussions) -->
- **Email**: gautam.kumar@fetch.ai

## Acknowledgments

- [uAgents](https://github.com/fetchai/uAgents) - The underlying agent framework.
- [A2A](https://github.com/a2aproject/a2a-python) - Agent-to-Agent communication protocol.
- [Fetch.ai](https://fetch.ai) - For foundational agent technologies.
```

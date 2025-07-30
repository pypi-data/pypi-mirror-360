# Agent Interface Protocol (AIP)

**Direct agent-to-component communication for conversational AI applications**

## Overview

The Agent Interface Protocol (AIP) enables AI agents to directly select and render UI components based on conversational context through structured JSON communication.

### Key Innovation

Instead of predetermined tool mappings, agents reason about optimal UI presentation and output structured data that frontends render directly:

```json
{
  "component": "timeline", 
  "data": {"events": [...]}
}
```

### Why This Matters

- **Vercel AI SDK**: Tool calls → predetermined components (1:1 mapping)
- **Agent Interface Protocol**: Conversational reasoning → dynamic component selection → structured rendering
- **Result**: More intuitive, context-aware interfaces that adapt to conversational flow

## Quick Start

```python
from agentinterface import ComponentRegistry, AgentInterfaceRenderer

# Coming soon - full implementation
# This is a namespace reservation package
```

## Development Status

🚧 **Alpha Release** - This package reserves the `agentinterface` namespace on PyPI. 

The full implementation is under active development at [tysonchan.com](https://tysonchan.com) and will be open-sourced as the Agent Interface Protocol.

## Learn More

- **Live Demo**: [tysonchan.com](https://tysonchan.com) - Conversational portfolio showcasing AIP
- **Documentation**: [agentinterface.dev](https://agentinterface.dev) *(coming soon)*
- **GitHub**: [github.com/iteebz/agentinterface](https://github.com/iteebz/agentinterface) *(coming soon)*

## License

MIT License - See LICENSE file for details.

## Author

Tyson Chan - [itsteebz@gmail.com](mailto:itsteebz@gmail.com)
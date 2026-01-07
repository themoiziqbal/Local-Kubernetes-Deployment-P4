# MCP Contracts Directory

This directory contains JSON Schema definitions for all MCP tools and resources used in the AI-Powered Multilingual Voice-Enabled Todo Chatbot.

## Purpose

These contracts define the input/output interfaces for all agents and resources, enabling:
1. **Contract testing**: Validate agent implementations conform to schemas
2. **Documentation**: Self-documenting API contracts for all agents
3. **Type safety**: Generate TypeScript/Python types from schemas (future)
4. **Interoperability**: MCP protocol compliance for potential multi-client scenarios

## Contracts Overview

### Resources

| File | Description | URI Pattern |
|------|-------------|-------------|
| `task-resource.json` | Task entity CRUD operations via SQLite MCP resource | `task://list`, `task://get/{id}`, `task://schema` |

### Agent Tools

| File | Tool Name | Agent | Purpose |
|------|-----------|-------|---------|
| `master-chat-agent.json` | `orchestrate_workflow` | Master Chat Agent | Coordinates multi-agent workflows |
| `intent-classifier-agent.json` | `classify_intent` | Intent Classifier Agent | Classifies user intent (CRUD operations) |
| `language-detector-agent.json` | `detect_language` | Language Detector Agent | Detects input language (ISO 639-1) |
| `translator-agent.json` | `translate_text` | Translator Agent | Bidirectional translation |
| `voice-processor-agent.json` | `process_voice_input` | Voice Processor Agent | STT (Whisper) coordination |
| `voice-processor-agent.json` | `generate_voice_output` | Voice Processor Agent | TTS coordination |
| `task-add-agent.json` | `add_task` | Task Add Agent | Create new task |
| `task-read-agent.json` | `read_tasks` | Task Read Agent | List/search/filter tasks |
| `task-update-agent.json` | `update_task` | Task Update Agent | Replace entire task |
| `task-patch-agent.json` | `patch_task` | Task Patch Agent | Modify specific task fields |
| `task-delete-agent.json` | `delete_task` | Task Delete Agent | Delete task (with confirmation) |

## Implementation Status

✅ **Complete**:
- `task-resource.json` - Task resource MCP schema
- `intent-classifier-agent.json` - Intent classification tool
- `task-add-agent.json` - Task creation tool

🚧 **To be created** (follow same pattern):
- `master-chat-agent.json`
- `language-detector-agent.json`
- `translator-agent.json`
- `voice-processor-agent.json`
- `task-read-agent.json`
- `task-update-agent.json`
- `task-patch-agent.json`
- `task-delete-agent.json`

## Schema Structure

All MCP tool schemas follow this structure:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Agent Name Tool Schema",
  "description": "Description of agent functionality",
  "tool_name": "function_name",
  "input_schema": { /* JSON Schema for input parameters */ },
  "output_schema": { /* JSON Schema for output structure */ },
  "examples": [ /* Example invocations */ ]
}
```

All MCP resource schemas follow this structure:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Resource Name Schema",
  "description": "Description of resource",
  "resource_uri_template": "resource://pattern/{param}",
  "actions": { /* GET/POST/PUT/DELETE operations */ },
  "definitions": { /* Reusable schema definitions */ }
}
```

## Validation

Contract tests (see `tests/contract/test_mcp_schemas.py`) validate:
1. All schemas are valid JSON Schema Draft 2020-12
2. All tool implementations conform to input/output schemas
3. All resource URIs match template patterns
4. Examples in schemas pass validation

## Usage

### Loading a schema in Python:

```python
import json
from jsonschema import validate

with open('contracts/intent-classifier-agent.json') as f:
    schema = json.load(f)

# Validate input against schema
input_data = {"user_input": "add a task to buy milk"}
validate(instance=input_data, schema=schema['input_schema'])

# Validate output against schema
output_data = {"intent": "create", "confidence": 0.95, ...}
validate(instance=output_data, schema=schema['output_schema'])
```

### Registering MCP tool from schema:

```python
from mcp import MCPServer

server = MCPServer()

@server.tool(schema=load_schema('contracts/task-add-agent.json'))
async def add_task(description: str, due_date: str = None, priority: str = None, tags: list = []):
    # Implementation
    pass
```

## Next Steps

1. **Phase 2**: Implement remaining contract files (copy pattern from existing ones)
2. **Testing**: Create contract tests using these schemas
3. **Code Generation**: Optionally generate Python dataclasses or Pydantic models from schemas
4. **Documentation**: Auto-generate API documentation from schemas

## References

- [JSON Schema 2020-12 Specification](https://json-schema.org/draft/2020-12/json-schema-core.html)
- [MCP Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Tool Registration](https://github.com/jlowin/fastmcp)

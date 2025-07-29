# maxs

minimalist ai agent

## install

```bash
pipx install maxs
maxs
```

## prerequisites

choose your ai provider:

**local (ollama)**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen3:4b
```

**cloud providers**
- bedrock: aws credentials configured
- anthropic: `ANTHROPIC_API_KEY` environment variable  
- openai: `OPENAI_API_KEY` environment variable
- github: `GITHUB_TOKEN` environment variable
- litellm: `LITELLM_API_KEY` environment variable
- llamaapi: `LLAMAAPI_API_KEY` environment variable
- mistral: `MISTRAL_API_KEY` environment variable

## usage

```bash
# basic (uses ollama by default)
maxs

# direct query mode
maxs "analyze this file" file.txt

# shell command execution
maxs "!ls -la"  # executes shell commands with !

# different providers
MODEL_PROVIDER=bedrock maxs
MODEL_PROVIDER=anthropic maxs  
MODEL_PROVIDER=openai maxs
MODEL_PROVIDER=mistral maxs

# custom model
MODEL_PROVIDER=ollama STRANDS_MODEL_ID=llama3.2:3b maxs

# custom host
OLLAMA_HOST=http://192.168.1.100:11434 maxs
```

## built-in tools

maxs comes with powerful built-in tools:

| tool | description | examples |
|------|-------------|----------|
| **bash** | execute shell commands safely | `run ls -la`, `check system status` |
| **scraper** | web scraping with beautifulsoup4 | `scrape https://example.com`, `parse html content` |
| **use_computer** | control mouse, keyboard, screenshots | `take screenshot`, `click at 100,200` |
| **use_agent** | spawn nested agents with different models | `use bedrock to analyze this` |
| **tcp** | network communication server/client | `start tcp server on port 8080` |
| **tasks** | background task management | `create task to monitor logs` |
| **environment** | manage environment variables | `set DEBUG=true`, `list all vars` |
| **dialog** | interactive ui dialogs | `show input dialog`, `create form` |

## model providers

| provider | models | setup |
|----------|--------|-------|
| ollama | qwen3:4b, llama3.2:3b, mistral:7b | `ollama pull model_name` |
| bedrock | us.anthropic.claude-sonnet-4-20250514-v1:0, us.anthropic.claude-opus-4-20250514-v1:0 | aws configure |
| anthropic | claude-sonnet-4-20250514, claude-opus-4-20250514 | `ANTHROPIC_API_KEY` |
| openai | o4-mini, o4-mini | `OPENAI_API_KEY` |
| github | openai/o4-mini, meta/llama3 | `GITHUB_TOKEN` |
| litellm | anthropic/claude-sonnet-4-20250514 | `LITELLM_API_KEY` |
| llamaapi | llama3.1-405b | `LLAMAAPI_API_KEY` |
| mistral | mistral-large-latest, mistral-medium-latest | `MISTRAL_API_KEY` |

## features

### chat interface
- **conversation history**: maintains context across sessions
- **shell integration**: execute commands with `!command` syntax
- **auto-completion**: command and history completion
- **session persistence**: messages saved to `/tmp/.maxs/`

### conversation memory
maxs remembers your recent conversations:
```bash
# conversations are automatically saved and loaded
maxs  # continues from where you left off
```

### multi-model workflows
dynamic model switching within conversations:
```
"use bedrock to analyze this complex data"
"switch to anthropic for creative writing" 
"use local ollama for quick calculations"
```

### background tasks
run long-running tasks in parallel:
```
"create a background task to monitor system logs"
"start task to download and process data"
"check status of running tasks"
```

### system integration
- web scraping with beautifulsoup4
- computer control (mouse, keyboard, screenshots)  
- tcp networking for service communication
- interactive dialogs and forms
- environment variable management

## custom tools

create python files in `./tools/`:

```python
# ./tools/tip.py
from strands import tool

@tool
def calculate_tip(amount: float, percentage: float = 15.0) -> dict:
    tip = amount * (percentage / 100)
    return {
        "status": "success",
        "content": [{"text": f"tip: ${tip:.2f}, total: ${amount + tip:.2f}"}]
    }
```

tools are immediately available.

## configuration

| variable | default | description |
|----------|---------|-------------|
| MODEL_PROVIDER | ollama | ai provider |
| STRANDS_MODEL_ID | qwen3:4b | model identifier |
| STRANDS_MAX_TOKENS | 1000 | max response tokens |
| STRANDS_TEMPERATURE | 1 | response creativity (0-2) |
| STRANDS_TOOLS | ALL | comma-separated tool filter |
| MAXS_LAST_MESSAGE_COUNT | 10 | conversation history length |
| MAXS_RESPONSE_SUMMARY_LENGTH | 200 | response summary length |
| BYPASS_TOOL_CONSENT | false | skip tool confirmation prompts |
| DEV | false | development mode |
| OLLAMA_HOST | http://localhost:11434 | ollama server url |

## session management

maxs automatically saves your conversations:
- **history file**: `/tmp/.maxs_history` (shell-compatible format)
- **session files**: `/tmp/.maxs/YYYY-MM-DD-sessionid.json`
- **conversation context**: last 10 messages loaded automatically

## advanced usage

**tool filtering**
```bash
# only enable specific tools
STRANDS_TOOLS="bash,scraper,use_agent" maxs

# json array format
STRANDS_TOOLS='["bash","scraper"]' maxs
```

**development mode**
```bash
# bypass tool confirmation prompts
BYPASS_TOOL_CONSENT=true maxs
```

**multi-model workflows**
```python
# different models for different tasks
from maxs import create_agent

# fast local model for quick tasks
quick_agent = create_agent("ollama")

# powerful cloud model for complex analysis  
analysis_agent = create_agent("bedrock")

# multilingual tasks with mistral
multilingual_agent = create_agent("mistral")
```

**environment switching**
```bash
# development with local models
MODEL_PROVIDER=ollama maxs

# production with cloud models
MODEL_PROVIDER=bedrock STRANDS_MODEL_ID=us.anthropic.claude-sonnet-4-20250514-v1:0 maxs

# multilingual production tasks
MODEL_PROVIDER=mistral STRANDS_MODEL_ID=mistral-large-latest maxs

## examples

**web scraping**
```
maxs "scrape the latest news from https://news.ycombinator.com"
```

**system administration**
```
maxs "check disk usage and running processes"
maxs "!df -h && ps aux | head -20"
```

**automation**
```
maxs "take a screenshot and analyze what's on screen"
maxs "create a background task to monitor /var/log/system.log"
```

**development**
```
maxs "format all python files in current directory"
maxs "run tests and show coverage report"
```

## build binary

```bash
pip install maxs[binary]
pyinstaller --onefile --name maxs -m maxs.main
```

binary in `./dist/maxs`

## license

mit

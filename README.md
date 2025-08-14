# Private Assistant Intent Engine

## Overview
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Owner: stkr22

The `private-assistant-intent-engine` is a **Natural Language Processing (NLP) component** that serves as the intent analysis backbone for the Private Assistant ecosystem. It processes natural language commands from voice interfaces, extracts meaningful linguistic elements, and publishes structured analysis results for downstream skills to consume.

> **Note**: This is currently a preliminary text analysis engine. Future versions will evolve into a comprehensive intent classification system with structured intents (e.g., `turn_on`, `play_music`, `set_temperature`) and entity extraction capabilities.

## Features

- **Natural Language Processing**: Uses SpaCy NLP models to extract linguistic elements (verbs, nouns, numbers) from natural language commands
- **Number Context Analysis**: Captures contextual information around numbers for better understanding (e.g., "Set temperature to **16**", "Play playlist **5**")
- **Room Detection**: Identifies room names mentioned in commands, supporting both specific rooms and "all rooms"
- **Command Splitting**: Handles compound commands with separators like "in addition" and "besides"
- **MQTT Event-Driven Architecture**: Async MQTT integration with automatic reconnection and error handling
- **Configurable**: Flexible YAML-based configuration for MQTT settings, SpaCy models, and available rooms
- **Robust Error Handling**: Graceful handling of connection failures with exponential backoff

## Architecture

### Message Flow

```
Voice Interface → MQTT → Intent Engine → MQTT → Skills
     ↓              ↓           ↓           ↓        ↓
 User Speech → Transcribed → Analyzed → Results → Actions
              Text       Text       Published
```

1. **Input**: Voice interfaces publish transcribed text to `assistant/comms_bridge/+/+/input`
2. **Processing**: Intent Engine analyzes text using SpaCy NLP
3. **Output**: Structured analysis results published to `assistant/intent_engine/result`
4. **Consumption**: Skills consume results to determine if commands match their capabilities

### Current Analysis Output

The engine currently extracts:
- **Verbs**: Action words (lemmatized)
- **Nouns**: Objects and entities (lowercase)
- **Numbers**: Numerical values with context (previous/next tokens)
- **Rooms**: Detected room names from configurable list

## Getting Started

### Prerequisites

- Python 3.12+
- MQTT broker accessible to the intent engine
- SpaCy English model (`en_core_web_md`)

### Installation

#### From PyPI
```bash
pip install private-assistant-intent-engine
```

#### For Development
```bash
git clone https://github.com/stkr22/private-assistant-intent-engine-py
cd private-assistant-intent-engine-py
uv sync --group dev
```

### Configuration

Create a YAML configuration file:

```yaml
# config.yaml
mqtt_server_host: "localhost"
mqtt_server_port: 1883
client_id: "intent_engine"
client_request_subscription: "assistant/comms_bridge/+/+/input"
intent_result_topic: "assistant/intent_engine/result"
spacy_model: "en_core_web_md"
available_rooms:
  - "living room"
  - "kitchen"
  - "bathroom"
  - "bedroom"
```

### Usage

#### Command Line
```bash
# Set config path via environment variable
export PRIVATE_ASSISTANT_CONFIG_PATH=/path/to/config.yaml
private-assistant-intent-engine

# Or pass directly
private-assistant-intent-engine /path/to/config.yaml
```

#### Programmatic Usage
```python
import asyncio
import pathlib
from private_assistant_intent_engine.main import start_intent_engine

# Run the intent engine
asyncio.run(start_intent_engine(pathlib.Path("config.yaml")))
```

## Example Analysis

### Input Command
```json
{
  "text": "Set temperature to 20 degrees in the living room",
  "client_id": "voice_client_1",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Output Analysis
```json
{
  "client_request": {
    "text": "Set temperature to 20 degrees in the living room",
    "client_id": "voice_client_1", 
    "timestamp": "2025-01-15T10:30:00Z"
  },
  "verbs": ["set"],
  "nouns": ["temperature", "degrees", "room"],
  "numbers": [
    {
      "number_token": 20,
      "previous_token": "to",
      "next_token": "degrees"
    }
  ],
  "rooms": ["living room"]
}
```

## Development

### Running Tests
```bash
uv run pytest
```

### Code Quality
```bash
uv run ruff check --fix .
uv run ruff format .
uv run mypy src/
```

### Building
```bash
uv build
```

## Future Roadmap

The intent engine will evolve to provide:

- **Intent Classification**: Structured intents like `turn_on`, `play_music`, `set_temperature`, `request_state`
- **Entity Recognition**: Clear entities like "desk lamp", "all lights", "spotify playlist"
- **Context Understanding**: Better handling of temporal references ("tomorrow morning", "in 15 minutes")
- **Multi-turn Conversations**: Support for follow-up questions and clarifications

### Example Future Output
```json
{
  "intent": "set_temperature",
  "entities": {
    "temperature": 20,
    "unit": "celsius", 
    "location": "living room"
  },
  "confidence": 0.95
}
```

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style (ruff, mypy)
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

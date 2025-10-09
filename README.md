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

The `private-assistant-intent-engine` is a **hybrid NLP component** that classifies user intents and extracts entities from natural language commands. Using rule-based pattern matching combined with SpaCy linguistic analysis, it provides structured intent classification for smart home skills in the Private Assistant ecosystem.

## Features

- **Intent Classification**: Recognizes 19 intent types (device control, media control, queries, scenes, scheduling, system)
- **Confidence Scoring**: Hierarchical scoring (1.0 to 0.3) based on keyword matches and contextual evidence
- **Entity Extraction**: Extracts 8 entity types (devices, rooms, numbers, durations, times, media IDs, scenes, modifiers)
- **Alternative Intents**: Provides ranked alternatives for ambiguous commands
- **Compound Command Support**: Splits and processes multiple commands in single utterance
- **Pattern Customization**: YAML-based intent pattern override system
- **Device Registry Integration**: Matches generic and specific device references
- **MQTT Event-Driven Architecture**: Async MQTT with automatic reconnection and error handling
- **Database Integration**: Loads rooms from shared database for consistent entity recognition

## Architecture

### Message Flow

```
Voice Interface → MQTT → Intent Engine → MQTT → Skills
     ↓              ↓           ↓           ↓        ↓
 User Speech → Transcribed → Analyzed → Results → Actions
              Text       Text       Published
```

1. **Input**: Voice interfaces publish ClientRequest to `assistant/comms_bridge/+/+/input`
2. **Classification**: Pattern matching identifies intent type with confidence score
3. **Extraction**: SpaCy NLP extracts entities (devices, rooms, numbers, etc.)
4. **Output**: IntentRequest messages published to `assistant/intent_engine/result`
5. **Consumption**: Skills evaluate intent relevance and execute appropriate actions

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

### Output: IntentRequest
```json
{
  "id": "uuid-v4",
  "classified_intent": {
    "intent_type": "device.set",
    "confidence": 0.9,
    "entities": {
      "number": [{
        "type": "number",
        "raw_text": "20",
        "normalized_value": 20.0,
        "metadata": {"unit": "celsius"}
      }],
      "room": [{
        "type": "room",
        "raw_text": "living room",
        "normalized_value": "living room"
      }]
    },
    "alternative_intents": [],
    "raw_text": "Set temperature to 20 degrees in the living room"
  },
  "client_request": {
    "text": "Set temperature to 20 degrees in the living room",
    "room": "kitchen",
    "output_topic": "assistant/comms_bridge/voice_client/response"
  }
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

## Documentation

For detailed documentation including:
- Confidence scoring system
- All 19 intent types and 8 entity types
- **Skill Integration Guide** with processing patterns
- Pattern customization
- API reference

See [docs/main.md](docs/main.md)

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style (ruff, mypy)
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.

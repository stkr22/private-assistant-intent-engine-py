# Private Assistant Intent Engine

## Overview

`private-assistant-intent-engine` is a core component designed to process natural language input within the Private Assistant ecosystem. This package leverages SpaCy for NLP, MQTT for messaging, and provides a streamlined way to analyze and handle user intents.

## Features

- **Intent Analysis**: Uses SpaCy to extract verbs, nouns, and numbers from text.
- **MQTT Integration**: Handles MQTT connections and messaging to interact with other components in the ecosystem.
- **Configurable**: Easily configurable through a provided configuration object.
- **Clean Shutdown**: Ensures clean disconnection from MQTT on shutdown.

## Getting Started

### Prerequisites

Ensure you have Python 3.11+ installed, as this library uses features available in Python 3.11 and later.

### Installation

To install `private-assistant-intent-engine`, you can use the following command:

```sh
pip install private-assistant-intent-engine
```

### Usage

Here is a basic example of how to use the `IntentEngine`:

```python
import spacy
import paho.mqtt.client as mqtt
from your_config_module import Config
from private_assistant_intent_engine import IntentEngine

# Load SpaCy model
nlp_model = spacy.load("en_core_web_md")

# Create an MQTT client
mqtt_client = mqtt.Client()

# Load your configuration
config_obj = Config()

# Initialize the IntentEngine
intent_engine = IntentEngine(config_obj, mqtt_client, nlp_model)

# Run the IntentEngine
intent_engine.run()
```

## Contributing

Contributions to `private-assistant-intent-engine` are welcome! Please read our contributing guidelines on how to propose bug fixes, improvements, or new features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

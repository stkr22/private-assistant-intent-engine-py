import pathlib

import pytest
import yaml
from pydantic import ValidationError

from private_assistant_intent_engine.config import (
    Config,
)

# Sample invalid YAML configuration (invalid type for spacy_model)
invalid_yaml = """
spacy_model: 12345  # invalid type - should be string
"""


def test_load_valid_config():
    data_directory = pathlib.Path(__file__).parent / "data" / "config.yaml"
    with data_directory.open("r") as file:
        config_data = yaml.safe_load(file)
    config = Config.model_validate(config_data)

    assert config.client_request_subscription == "test/+/+/input"
    assert config.intent_result_topic == "test/result"
    assert config.spacy_model == "en_core_web_sm"


def test_load_invalid_config():
    config_data = yaml.safe_load(invalid_yaml)
    with pytest.raises(ValidationError):
        Config(**config_data)

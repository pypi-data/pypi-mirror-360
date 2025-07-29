import json
from pathlib import Path

import requests
from loguru import logger


class TokenCostEstimator:
    SOURCE = "https://raw.githubusercontent.com/BerriAI/litellm/refs/heads/main/model_prices_and_context_window.json"

    def __init__(self):
        self.cache_folder = Path(__file__).parent / ".cache"
        self.cache_folder.mkdir(parents=True, exist_ok=True)
        self.cache_path = self.cache_folder / "model_prices_cache.json"
        self.model_data = self._load_model_data()

    def _load_model_data(self):
        if self.cache_path.exists():
            return json.loads(self.cache_path.read_text())

        # Download the data if cache doesn't exist or is invalid
        logger.info(f"Downloading model pricing data from '{self.SOURCE}'")
        response = requests.get(self.SOURCE, timeout=20)
        response.raise_for_status()
        model_data = response.json()

        # Cache the downloaded data
        self.cache_path.write_text(json.dumps(model_data))

        return model_data

    def calculate_cost(self, model_name, input_tokens, output_tokens):
        if model_name not in self.model_data:
            raise ValueError(f"Model '{model_name}' not found in the model data.")

        model_info = self.model_data[model_name]

        input_cost_per_token = model_info.get("input_cost_per_token", 0)
        output_cost_per_token = model_info.get("output_cost_per_token", 0)

        input_cost = input_tokens * input_cost_per_token
        output_cost = output_tokens * output_cost_per_token
        total_cost = input_cost + output_cost

        return {
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost,
            "model_info": {
                "model_name": model_name,
                "input_cost_usd_per_token": input_cost_per_token,
                "output_cost_usd_per_token": output_cost_per_token,
            },
        }


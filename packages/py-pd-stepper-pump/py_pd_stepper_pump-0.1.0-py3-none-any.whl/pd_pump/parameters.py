import json
import importlib.resources as pkg_resources
from typing import Any
from dataclasses import dataclass, field
import pd_pump
import os

@dataclass
class Parameters:
    steps_per_ml_pump: int = field(init=False)
    steps_per_ml_suck: int = field(init=False)

    def __post_init__(self):
        data = self._load_parameters()

        try:
            self.steps_per_ml_pump = data["steps_per_ml_pump"]
            self.steps_per_ml_suck = data["steps_per_ml_suck"]
        except KeyError as e:
            raise KeyError(f"Fehlender Schlüssel in parameters.json: {e}")

    def _load_parameters(self) -> dict[str, Any]:
        try:
            with pkg_resources.files(pd_pump).joinpath("parameters.json").open("r") as f:
                return json.load(f)
        except (FileNotFoundError, ModuleNotFoundError):
            pass
        
        dev_path = os.path.join(os.path.dirname(__file__), "parameters.json")
        if os.path.exists(dev_path):
            with open(dev_path, "r") as f:
                return json.load(f)

        raise FileNotFoundError("File not found")
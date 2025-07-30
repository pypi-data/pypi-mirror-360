from pydantic import BaseModel
import json
import re
from typing import Self


class InputConfig(BaseModel):

    @classmethod
    def load_from_file(cls, json_file) -> Self:
        with open(json_file, "r") as f:
            data = json.load(f)
        return cls.model_validate(data)


# Helper classes for inputs
class AdaptiveDataset(BaseModel):
    file: str


class AdaptivePreferenceDataset(AdaptiveDataset): ...


class AdaptiveMetricDataset(AdaptiveDataset): ...


class AdaptiveModel(BaseModel):
    path: str

    def __repr__(self) -> str:

        # Redact api_key in the path if present, show only last 3 chars
        def redact_api_key(match):
            key = match.group(2)
            if len(key) > 3:
                redacted = "<REDACTED>" + key[-3:]
            else:
                redacted = "<REDACTED>"
            return f"{match.group(1)}{redacted}"

        redacted_path = re.sub(r"(api_key=)([^&]+)", redact_api_key, self.path)
        return f"AdaptiveModel(path='{redacted_path}')"

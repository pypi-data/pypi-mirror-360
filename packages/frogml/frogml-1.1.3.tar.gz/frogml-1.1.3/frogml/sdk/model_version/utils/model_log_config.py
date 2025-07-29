from dataclasses import dataclass
from typing import Dict, Optional, List, Any


@dataclass
class ModelLogConfig:
    model_name: str
    target_dir: str
    model_flavor: str
    framework_version: str
    full_model_path: str
    serialization_format: str
    repository: str
    version: Optional[str] = None
    properties: Optional[Dict[str, str]] = None
    dependencies: Optional[List[str]] = None
    code_dir: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    predict_file: Optional[str] = None

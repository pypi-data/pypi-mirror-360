from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Main storage for runtime configuration params"""

    config_path = Path(__file__).parent.resolve()
    project_path = config_path.parent.parent.resolve()


global_config = Config()

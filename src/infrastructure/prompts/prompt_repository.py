import json
from pathlib import Path

from src.infrastructure.prompts.default_prompts import DEFAULT_PROMPTS

PROMPTS_FILE_PATH = Path("data/prompts.json")


class UnknownAgentError(ValueError):
    def __init__(self, agent_name: str) -> None:
        valid = ", ".join(sorted(DEFAULT_PROMPTS))
        super().__init__(f"No existe un agente llamado '{agent_name}'. Validos: {valid}")


class PromptRepository:
    def __init__(self, file_path: Path = PROMPTS_FILE_PATH) -> None:
        self._file_path = file_path
        if not self._file_path.exists():
            self._write(dict(DEFAULT_PROMPTS))

    def _read(self) -> dict[str, str]:
        with self._file_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write(self, prompts: dict[str, str]) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(prompts, file, ensure_ascii=False, indent=2)

    def get_all_prompts(self) -> dict[str, str]:
        return self._read()

    def get_prompt(self, agent_name: str) -> str:
        prompts = self._read()
        if agent_name not in prompts:
            raise UnknownAgentError(agent_name)
        return prompts[agent_name]

    def update_prompt(self, agent_name: str, new_prompt: str) -> None:
        prompts = self._read()
        if agent_name not in prompts:
            raise UnknownAgentError(agent_name)
        prompts[agent_name] = new_prompt
        self._write(prompts)

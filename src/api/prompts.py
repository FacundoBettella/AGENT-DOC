from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.infrastructure.prompts.prompt_repository import PromptRepository, UnknownAgentError

router = APIRouter(prefix="/prompts", tags=["prompts"])


class PromptResponse(BaseModel):
    agent_name: str
    system_prompt: str


class PromptUpdateRequest(BaseModel):
    system_prompt: str = Field(..., min_length=1)


@router.get("", response_model=list[PromptResponse])
def list_prompts() -> list[PromptResponse]:
    repository = PromptRepository()
    return [
        PromptResponse(agent_name=name, system_prompt=prompt)
        for name, prompt in repository.get_all_prompts().items()
    ]


@router.get("/{agent_name}", response_model=PromptResponse)
def get_prompt(agent_name: str) -> PromptResponse:
    repository = PromptRepository()
    try:
        prompt = repository.get_prompt(agent_name)
    except UnknownAgentError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return PromptResponse(agent_name=agent_name, system_prompt=prompt)


@router.put("/{agent_name}", response_model=PromptResponse)
def update_prompt(agent_name: str, payload: PromptUpdateRequest) -> PromptResponse:
    repository = PromptRepository()
    try:
        repository.update_prompt(agent_name, payload.system_prompt)
    except UnknownAgentError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return PromptResponse(agent_name=agent_name, system_prompt=payload.system_prompt)

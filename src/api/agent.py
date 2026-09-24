from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse

from src.agents.graph import agents_wrapper
from src.api.dependencies import AppDependencies, get_app_dependencies
from src.helpers.helpers import (
    delete_file,
    doc_to_markdown,
    generate_unique_filepath,
    save_file,
)
from src.models.models import AgentState

agent_router = APIRouter()


@agent_router.post("/agent_call")
async def agent_call(
    jd: Annotated[str, Form()],
    cv: Annotated[UploadFile, File()],
    deps: Annotated[
        AppDependencies,
        Depends(get_app_dependencies),
    ],
):
    file_path = generate_unique_filepath(cv.filename)
    await save_file(file_path, cv)
    resume = doc_to_markdown(file_path)
    delete_file(file_path)

    result = agents_wrapper(deps.graph, jd, resume)
    state = AgentState.model_validate(result)
    critique_history = " ".join(
        review.critique for review in state.critique_history if review.critique
    )

    return JSONResponse(
        content={
            "score": state.review.score if state.review else None,
            "optimization_summary": state.artifacts.optimization_summary,
            "critique_history": critique_history,
            "optimized_cv": state.final_cv or "",
        }
    )

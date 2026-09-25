from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.agents.graph import agents_wrapper
from src.api.dependencies import AppDependencies, get_app_dependencies
from src.helpers.helpers import (
    delete_file,
    generate_unique_filepath,
    get_cv_source_format,
    read_cv_text,
    save_file,
)
from src.models.models import AgentState, SourceFormat

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
    filename = cv.filename or ""
    if not filename:
        raise HTTPException(status_code=400, detail="The uploaded CV has no filename.")

    # Keep the existing MarkItDown behavior for other supported document
    # formats; only LaTeX extensions need the raw-source path below.
    source_format: SourceFormat = get_cv_source_format(filename) or "markdown"

    file_path = generate_unique_filepath(filename)
    try:
        await save_file(file_path, cv)
        resume = read_cv_text(file_path, filename)
    finally:
        delete_file(file_path)

    if not resume.strip():
        raise HTTPException(status_code=400, detail="The uploaded CV is empty.")

    result = agents_wrapper(
        deps.graph,
        jd,
        resume,
        source_format=source_format,
    )
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
            "source_format": source_format,
            "output_format": "latex",
        }
    )

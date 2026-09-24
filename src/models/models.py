from __future__ import annotations

from operator import add
from typing import Annotated

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class AgentInputs(BaseModel):
    """Validated source material shared by every agent in the workflow."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    job_description: str = Field(
        min_length=1,
        description="The complete target job description.",
        validation_alias=AliasChoices("job_description", "jd"),
    )
    source_cv: str = Field(
        min_length=1,
        description="The source CV converted to Markdown.",
        validation_alias=AliasChoices("source_cv", "cv"),
    )


class WorkflowConfig(BaseModel):
    """Controls when the optimizer and critic loop should stop."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    score_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Minimum ATS-alignment score required for approval.",
    )
    max_iterations: int = Field(
        default=3,
        ge=1,
        description="Maximum number of critic evaluations before finalizing.",
    )


class ResumeArtifacts(BaseModel):
    """Artifacts produced as the CV moves through the graph."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    analysis_report: str | None = Field(
        default=None,
        description="Evidence-based gaps and opportunities found by the analyser.",
    )
    optimization_summary: str | None = Field(
        default=None,
        description="Summary of the changes made by the optimizer.",
    )
    optimized_cv: str | None = Field(
        default=None,
        description="The latest optimized CV in Markdown format.",
    )
    parsed_cv: str | None = Field(
        default=None,
        description="The final, formatted CV in LaTeX format.",
    )


class CritiqueResult(BaseModel):
    """A single critic decision stored in the state and review history."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    iteration: int = Field(ge=1, description="One-based critic iteration number.")
    score: float = Field(ge=0.0, le=1.0, description="ATS-alignment score.")
    critique: str = Field(
        default="",
        description="Actionable feedback for the next optimizer pass.",
    )
    approved: bool = Field(
        description="Whether the CV has no major remaining gaps.",
    )

    @model_validator(mode="after")
    def require_critique_when_not_approved(self) -> CritiqueResult:
        if not self.approved and not self.critique.strip():
            raise ValueError("A rejected CV must include actionable critique.")
        return self


class AgentState(BaseModel):
    """The complete, typed state passed between LangGraph nodes.

    Source inputs, workflow controls, generated artifacts, and the latest
    review are separate concerns. This keeps node updates narrow and preserves
    every critic decision for observability and debugging.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    inputs: AgentInputs
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    artifacts: ResumeArtifacts = Field(default_factory=ResumeArtifacts)
    review: CritiqueResult | None = None
    critique_history: Annotated[list[CritiqueResult], add] = Field(
        default_factory=list,
        description="All critic decisions, appended once per critic pass.",
    )

    @property
    def should_finalize(self) -> bool:
        """Whether the current review should move to the parser node."""
        if self.review is None:
            return False

        return (
            self.review.approved
            or self.review.score >= self.workflow.score_threshold
            or self.review.iteration >= self.workflow.max_iterations
        )

    @property
    def final_cv(self) -> str | None:
        """Prefer parsed LaTeX, falling back to optimized Markdown."""
        return self.artifacts.parsed_cv or self.artifacts.optimized_cv


class LLMResponseModel(BaseModel):
    """Base contract for structured LLM responses."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class AnalyserResponseModel(LLMResponseModel):
    analysing_report: str = Field(
        min_length=1,
        description="A complete, evidence-based CV analysis report.",
    )


class OptimizerResponseModel(LLMResponseModel):
    optimized_cv: str = Field(
        min_length=1,
        description="Markdown for the optimized CV.",
    )
    optimization_summary: str = Field(
        min_length=1,
        description="A concise summary of the changes made.",
    )


class ParserResponseModel(LLMResponseModel):
    parsed_cv: str = Field(
        min_length=1,
        description="A complete LaTeX document for the parsed CV.",
    )


class CriticResponseModel(LLMResponseModel):
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="How well the optimized CV matches the target job, from 0 to 1.",
    )
    approved: bool = Field(
        description="True when the score passes and no major gaps remain.",
    )
    critique: str = Field(
        default="",
        description="Specific, actionable feedback; empty when approved.",
    )

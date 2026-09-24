from typing import Any

from src.agents.prompts.prompt_management import prompt_template_config
from src.models.models import AgentState, OptimizerResponseModel


class OptimizerNode:
    def __init__(self, llm_client: Any, model_name: str):
        self.llm_client = llm_client
        self.model_name = model_name
        self.template = prompt_template_config(
            "src/agents/prompts/optimizer_agent.yaml",
            "optimizer_agent",
        )

    def __call__(self, state: AgentState) -> dict[str, Any]:
        latest_cv = state.artifacts.optimized_cv or state.inputs.source_cv
        latest_critique = state.review.critique if state.review else "None (first pass)"
        prompt = self.template.render(
            jd=state.inputs.job_description,
            analysis_report=state.artifacts.analysis_report or "Not available",
            old_resume=latest_cv,
            critique=latest_critique,
        )

        response, _ = self.llm_client.chat.completions.create_with_completion(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user",
                    "content": "Proceed with the optimization based on the provided context.",
                },
            ],
            response_model=OptimizerResponseModel,
        )

        return {
            "artifacts": state.artifacts.model_copy(
                update={
                    "optimized_cv": response.optimized_cv,
                    "optimization_summary": response.optimization_summary,
                }
            )
        }

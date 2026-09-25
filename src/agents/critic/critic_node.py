from typing import Any

from jinja2 import Template

from src.agents.prompts.prompt_management import prompt_template_config
from src.models.models import AgentState, CriticResponseModel, CritiqueResult


class CriticNode:
    def __init__(self, llm_client: Any, model_name: str):
        self.llm_client = llm_client
        self.model_name = model_name
        self.template = prompt_template_config(
            "src/agents/prompts/critic_agent.yaml",
            "critic_agent",
        )

    def __call__(self, state: AgentState) -> dict[str, Any]:
        prompt = self.template.render()
        next_iteration = (state.review.iteration + 1) if state.review else 1
        previous_critique = (
            state.review.critique if state.review else "None (first pass)"
        )
        query = Template(
            """
            JOB DESCRIPTION:
            {{ jd }}

            OPTIMIZED CV:
            {{ optimized_cv }}

            ORIGINAL CV (for fabrication check):
            {{ cv }}

            Source format: {{ source_format }}
            Previous critique (if any): {{ previous_critique }}
            Iteration: {{ iteration }}/{{ max_iterations }}
            Score threshold: {{ threshold }}
            """
        ).render(
            jd=state.inputs.job_description,
            optimized_cv=state.artifacts.optimized_cv or "",
            cv=state.inputs.source_cv,
            source_format=state.inputs.source_format,
            previous_critique=previous_critique,
            iteration=next_iteration,
            max_iterations=state.workflow.max_iterations,
            threshold=state.workflow.score_threshold,
        )

        response, _ = self.llm_client.chat.completions.create_with_completion(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
            response_model=CriticResponseModel,
        )
        review = CritiqueResult(
            iteration=next_iteration,
            score=response.score,
            critique=response.critique,
            approved=response.approved,
        )

        return {
            "review": review,
            "critique_history": [review],
        }

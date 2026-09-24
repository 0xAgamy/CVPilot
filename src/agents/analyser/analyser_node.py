from typing import Any

from jinja2 import Template

from src.agents.prompts.prompt_management import prompt_template_config
from src.models.models import AgentState, AnalyserResponseModel


class AnalyserNode:
    def __init__(self, llm_client: Any, model_name: str):
        self.llm_client = llm_client
        self.model_name = model_name
        self.template = prompt_template_config(
            "src/agents/prompts/analyser_agent.yaml",
            "analyser_agent",
        )

    def __call__(self, state: AgentState) -> dict[str, Any]:
        prompt = self.template.render()
        query = Template(
            """
            ### job description
            {{ job_description }}

            ### markdown Resume
            {{ resume }}
            """
        ).render(
            job_description=state.inputs.job_description,
            resume=state.inputs.source_cv,
        )
        response, _ = self.llm_client.chat.completions.create_with_completion(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
            response_model=AnalyserResponseModel,
        )

        return {
            "artifacts": state.artifacts.model_copy(
                update={"analysis_report": response.analysing_report}
            )
        }

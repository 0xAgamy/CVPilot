from typing import Any

from src.agents.prompts.prompt_management import prompt_template_config
from src.helpers.helpers import validate_latex_output
from src.models.models import AgentState, ParserResponseModel


class ParserNode:
    def __init__(self, llm_client: Any, model_name: str):
        self.llm_client = llm_client
        self.model_name = model_name
        self.template = prompt_template_config(
            "src/agents/prompts/parser_agent.yaml",
            "parser_agent",
        )

    def __call__(self, state: AgentState) -> dict[str, Any]:
        # A LaTeX upload already contains the user's chosen template. The
        # optimizer has been instructed to edit that document in place, so do
        # not run the generic Markdown-to-LaTeX formatter over it.
        if state.inputs.source_format == "latex":
            optimized_cv = state.artifacts.optimized_cv
            if not optimized_cv:
                raise ValueError("The optimizer did not return a LaTeX CV.")
            validate_latex_output(state.inputs.source_cv, optimized_cv)

            return {
                "artifacts": state.artifacts.model_copy(
                    update={"parsed_cv": optimized_cv}
                )
            }

        prompt = self.template.render(
            optimized_cv=state.artifacts.optimized_cv or "",
        )

        response, _ = self.llm_client.chat.completions.create_with_completion(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Process the optimized CV now."},
            ],
            response_model=ParserResponseModel,
        )

        return {
            "artifacts": state.artifacts.model_copy(
                update={"parsed_cv": response.parsed_cv}
            )
        }

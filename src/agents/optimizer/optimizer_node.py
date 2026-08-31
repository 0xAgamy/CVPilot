from src.models.models import AgentState, OptimizerResponseModel
from src.agents.prompts.prompt_management import prompt_template_config
from typing import Any



class OptimizerNode:
    def __init__(self, llm_client:Any,model_name:str):
        self.llm_client= llm_client
        self.model_name= model_name
        self.template=prompt_template_config("src/agents/prompts/optimizer_agent.yaml","optimizer_agent")

    def __call__(self, state:AgentState):
        prompt=self.template.render(
            jd= state.jd,
            analysis_report=state.analysing_report,
            old_resume=state.cv,
            critique=state.critique
    
        )
    
        response, raw_response= self.llm_client.chat.completions.create_with_completion(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Proceed with the optimization based on the provided context."},
    
            ],
            response_model=OptimizerResponseModel,
        )
    
        return {
            "optimized_cv": response.optimized_cv,
            "optimization_summary":response.optimization_summary
        }
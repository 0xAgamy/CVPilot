
from src.models.models import AgentState,ParserResponseModel
from src.agents.prompts.prompt_management import prompt_template_config
from typing import Any


class ParserNode:
    def __init__(self, llm_client:Any,model_name:str):
        self.llm_client= llm_client
        self.model_name= model_name
    def __call__(self, state:AgentState):
        template= prompt_template_config("src/agents/prompts/parser_agent.yaml","parser_agent")
        prompt=template.render(
            optimized_cv= state.optimized_cv,
        )
    
        response, raw_response= self.llm_client.chat.completions.create_with_completion(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "help me please"},
    
            ],
            response_model=ParserResponseModel,
        )
        
        return{
            "optimized_cv":response.parsed_cv,
        }
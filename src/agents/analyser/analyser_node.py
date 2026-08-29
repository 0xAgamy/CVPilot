from src.models.models import AgentState, AnalyserResponseModel
from jinja2 import Template
from src.agents.prompts.prompt_management import prompt_template_config
from typing import Any

class AnalyserNode:
    def __init__(self, llm_client:Any,model_name:str):
        self.llm_client= llm_client
        self.model_name= model_name

    def __call__(self, state:AgentState):
        template=prompt_template_config("src/agents/prompts/analyser_agent.yaml","analyser_agent")
        prompt=template.render()
    
        query_template= """
        ### job description
        {{ job_description }}
    
    
        ### markdown Resume
        {{ resume }}
    
        """.strip()
    
        query_prompt= Template(query_template)
        
        query=query_prompt.render(
            job_description=state.jd,
            resume= state.cv
        )
        response, raw_response= self.llm_client.chat.completions.create_with_completion(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
    
            ],
            response_model=AnalyserResponseModel,
        )
    
        return {
            "analysing_report":response.analysing_report
        }
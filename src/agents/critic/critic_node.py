from openai import OpenAI
from src.models.models import AgentState, CriticResponseModel
from jinja2 import Template
from src.agents.prompts.prompt_management import prompt_template_config
from typing import Any

class CriticNode:
    def __init__(self, llm_client:Any,model_name:str):
        self.llm_client= llm_client
        self.model_name= model_name
    def __call__(self, state:AgentState):
        template= prompt_template_config("src/agents/prompts/critic_agent.yaml","critic_agent")
        prompt= template.render()
        temp="""
            JOB DESCRIPTION:
            {{ jd }}
    
            OPTIMIZED CV:
            {{ optimized_cv }}
    
            ORIGINAL CV (for fabrication check):
            {{ cv }}
    
            Previous critique (if any): {{ previous_critique }}
            Iteration: {{ iteration }}/{{ max_iterations }}
            Score threshold: {{ threshold }}""".strip()
        query_template= Template(temp)
        query= query_template.render(
            jd=state.jd,
            optimized_cv=state.optimized_cv,
            cv= state.cv,
            previous_critique=state.critique or "None (first pass)",
            iteration= state.iteration,
            max_iterations=state.max_iterations,
            threshold=state.score_threshold
    
        )
    
    
        response, raw_response= self.llm_client.chat.completions.create_with_completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
        
                ],
                response_model=CriticResponseModel,
            )
        return {
            "score": response.score,
            "critique": response.critique,
            "critique_history": [response.critique],
            "approved": response.approved,
            "iteration": state.iteration + 1,
        }
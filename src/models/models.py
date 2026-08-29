from pydantic import BaseModel, Field
from typing import List, Dict, Annotated, Any
from operator import add
class AgentState(BaseModel):
    jd:str= Field(description="a full of targeted Job description")
    cv:str= Field(description="Full Resume as markdown, that we will optimize")
    optimization_summary:str= ""
    analysing_report:str=""
    optimized_cv:str= ""
    
    score: float = 0.0
    score_threshold: float = 0.85
    iteration: int = 0
    max_iterations: int = 3
    critique: str = ""              
    critique_history: Annotated[List[str], add] = []
    approved: bool = False 

class AnalyserResponseModel(BaseModel):
    analysing_report:str= Field(description="a free text that contains a full Analysing Report")

class OptimizerResponseModel(BaseModel):
    optimized_cv:str= Field(description="Mardown for the optimized resume")
    optimization_summary:str= Field(description="Optimization Summary")

class ParserResponseModel(BaseModel):
    parsed_cv:str= Field(description="LaTex for the parsed resume")


class CriticResponseModel(BaseModel):
    score: float = Field(description="0-1 score of how well optimized_cv matches the JD")
    approved: bool = Field(description="True if score >= threshold and no major gaps remain")
    critique: str = Field(description="Specific, actionable feedback for the optimizer. Empty if approved.")

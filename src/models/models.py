from pydantic import BaseModel, Field
from typing import List, Dict, Annotated

class AgentState(BaseModel):
    jd:str= Field(description="a full of targeted Job description")
    cv:str= Field(description="Full Resume as markdown, that we will optimize")
    optimization_suggestion:str= ""

    optimized_cv:str= ""
    score:float=0 
    output_file_path:str=""

class AnalyserResponseModel(BaseModel):
    optimization_suggestion:str= Field(description="a free text that contains a full optimization suggestion")
    score:float=Field(description="a float number that indicate how relevent the Job description with the old Resume")

class OptimizerResponseModel(BaseModel):
    optimized_cv:str= Field(description="Mardown for the optimized resume")
    score:float=Field(description="a float number that indicate how relevent the Job description with the optimized version of Resume")


class ParserResponseModel(BaseModel):
    parsed_cv:str= Field(description="LaTex for the parsed resume")



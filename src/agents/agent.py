from openai import OpenAI
from models.models import AgentState, AnalyserResponseModel,OptimizerResponseModel, ParserResponseModel, CriticResponseModel
from jinja2 import Template
import instructor
from helpers.config import get_settings
from .prompts.prompt_management import prompt_template_config
st=get_settings()
MODEL_NAME=st.MODEL_NAME

gen_client= OpenAI(
    base_url=st.BASE_URL,
    api_key=st.API_KEY
)

client= instructor.from_openai(gen_client)

def Analyser_node(state: AgentState) -> dict:
    template=prompt_template_config("agents/prompts/analyser_agent.yaml","analyser_agent")
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
    response, raw_response= client.chat.completions.create_with_completion(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query}

        ],
        response_model=AnalyserResponseModel,
    )

    return {
        "analysing_report":response.analysing_report
    }


def Optimizer_node(state: AgentState) -> dict:
    template=prompt_template_config("agents/prompts/optimizer_agent.yaml","optimizer_agent")
    prompt=template.render(
        jd= state.jd,
        analysis_report=state.analysing_report,
        old_resume=state.cv,
        critique=state.critique

    )

    response, raw_response= client.chat.completions.create_with_completion(
        model=MODEL_NAME,
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



def Parser_node(state: AgentState)-> dict:

    template= prompt_template_config("agents/prompts/parser_agent.yaml","parser_agent")
    prompt=template.render(
        optimized_cv= state.optimized_cv,
    )

    response, raw_response= client.chat.completions.create_with_completion(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "help me please"},

        ],
        response_model=ParserResponseModel,
    )
    with open("../output/optimized_cv.tex", 'w', encoding="utf-8") as file:
        file.write(response.parsed_cv)
    return{
        "optimized_cv":response.parsed_cv,
        "output_file_path":"../output/optimized_cv.tex"
    }


def Critic_node(state:AgentState)->dict:
    template= prompt_template_config("agents/prompts/critic_agent.yaml","critic_agent")
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


    response, raw_response= client.chat.completions.create_with_completion(
            model=MODEL_NAME,
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
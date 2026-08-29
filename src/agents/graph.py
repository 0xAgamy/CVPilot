from langgraph.graph import START, StateGraph, END
from src.models.models import AgentState
from src.agents.analyser.analyser_node import AnalyserNode
from src.agents.optimizer.optimizer_node import OptimizerNode
from src.agents.parser.parser_node import ParserNode
from src.agents.critic.critic_node import CriticNode

def graph_builder(llm_client, model_name):
    def critic_conditional_node(state:AgentState):
        if state.approved or state.score >= state.score_threshold:
            return "parser"
        if state.iteration >= state.max_iterations:
            return "parser"
        return "optimizer"

    Analyser_node= AnalyserNode(llm_client, model_name)
    Optimizer_node= OptimizerNode(llm_client,model_name)
    Parser_node= ParserNode(llm_client,model_name)
    Critic_node= CriticNode(llm_client,model_name)

    wf= StateGraph(AgentState)

    wf.add_node("analyser",Analyser_node )
    wf.add_node("optimizer",Optimizer_node )
    wf.add_node("parser",Parser_node )
    wf.add_node("critic",Critic_node )


    wf.add_edge(START,"analyser")
    wf.add_edge("analyser","optimizer")

    wf.add_edge("optimizer","critic")

    wf.add_conditional_edges(
        "critic",
        critic_conditional_node,
        {
            "parser":"parser",
            "optimizer":"optimizer"
        }
    )

    wf.add_edge("parser",END)
    return wf.compile()


def agents_wrapper(graph,jd, cv) ->dict:
    return graph.invoke(
        {
            "jd":jd,
            "cv":cv
        }
        )



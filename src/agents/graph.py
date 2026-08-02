from helpers.helpers import doc_to_markdown
from langgraph.graph import START, StateGraph, END
from models.models import AgentState
from agents.agent import Analyser_node, Optimizer_node, Parser_node,Critic_node
from pprint import pprint


def critic_condtional_node(state:AgentState):
    if state.approved or state.score >= state.score_threshold:
        return "parser"
    if state.iteration >= state.max_iterations:
        return "parser"
    return "optimizer"


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
    critic_condtional_node,
    {
        "parser":"parser",
        "optimizer":"optimizer"
    }
)

wf.add_edge("parser",END)
graph= wf.compile()


def agents_wrapper(jd, cv) ->dict:
    return graph.invoke(
        {
            "jd":jd,
            "cv":cv
        }
        )



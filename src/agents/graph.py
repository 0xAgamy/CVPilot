from helpers.helpers import doc_to_markdown
from langgraph.graph import START, StateGraph, END
from models.models import AgentState
from agents.agent import Analyser_node, Optimizer_node, Parser_node
from pprint import pprint

wf= StateGraph(AgentState)

wf.add_node("analyser",Analyser_node )
wf.add_node("optimizer",Optimizer_node )
wf.add_node("parser",Parser_node )

wf.add_edge(START,"analyser")
wf.add_edge("analyser","optimizer")
wf.add_edge("optimizer","parser")


wf.add_edge("parser",END)
graph= wf.compile()


def agents_wrapper(jd, cv) ->dict:
    return graph.invoke(
        {
            "jd":jd,
            "cv":cv
        }
        )



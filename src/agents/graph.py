from typing import Any, Literal

from langgraph.graph import END, START, StateGraph

from src.agents.analyser.analyser_node import AnalyserNode
from src.agents.critic.critic_node import CriticNode
from src.agents.optimizer.optimizer_node import OptimizerNode
from src.agents.parser.parser_node import ParserNode
from src.models.models import AgentInputs, AgentState, SourceFormat


def critic_conditional_node(
    state: AgentState,
) -> Literal["parser", "optimizer"]:
    return "parser" if state.should_finalize else "optimizer"


def graph_builder(llm_client: Any, model_name: str):
    analyser_node = AnalyserNode(llm_client, model_name)
    optimizer_node = OptimizerNode(llm_client, model_name)
    parser_node = ParserNode(llm_client, model_name)
    critic_node = CriticNode(llm_client, model_name)

    workflow = StateGraph(AgentState)
    workflow.add_node("analyser", analyser_node)
    workflow.add_node("optimizer", optimizer_node)
    workflow.add_node("parser", parser_node)
    workflow.add_node("critic", critic_node)

    workflow.add_edge(START, "analyser")
    workflow.add_edge("analyser", "optimizer")
    workflow.add_edge("optimizer", "critic")
    workflow.add_conditional_edges(
        "critic",
        critic_conditional_node,
        {
            "parser": "parser",
            "optimizer": "optimizer",
        },
    )
    workflow.add_edge("parser", END)

    return workflow.compile()


def agents_wrapper(
    graph: Any,
    jd: str,
    cv: str,
    source_format: SourceFormat = "markdown",
) -> dict[str, Any]:
    initial_state = AgentState(
        inputs=AgentInputs(
            job_description=jd,
            source_cv=cv,
            source_format=source_format,
        ),
    )
    return graph.invoke(initial_state)

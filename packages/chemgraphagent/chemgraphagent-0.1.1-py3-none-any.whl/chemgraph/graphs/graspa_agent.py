from langgraph.graph import StateGraph, START, END
from langchain_core.messages import ToolMessage
import json
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from chemgraph.tools.graspa_tools import run_graspa
from chemgraph.models.agent_response import ResponseFormatter
from chemgraph.prompt.single_agent_prompt import (
    single_agent_prompt,
    formatter_prompt,
)
from chemgraph.utils.logging_config import setup_logger
from chemgraph.state.state import State

logger = setup_logger(__name__)


class BasicToolNode:
    """A node that executes tools requested in the last AIMessage.

    This class processes tool calls from AI messages and executes the corresponding
    tools, handling their results and any potential errors.

    Parameters
    ----------
    tools : list
        List of tool objects that can be called by the node

    Attributes
    ----------
    tools_by_name : dict
        Dictionary mapping tool names to their corresponding tool objects
    """

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: State) -> State:
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")

        outputs = []
        for tool_call in message.tool_calls:
            try:
                tool_name = tool_call.get("name")
                if not tool_name or tool_name not in self.tools_by_name:
                    raise ValueError(f"Invalid tool name: {tool_name}")

                tool_result = self.tools_by_name[tool_name].invoke(tool_call.get("args", {}))

                # Handle different types of tool results
                result_content = (
                    tool_result.dict()
                    if hasattr(tool_result, "dict")
                    else (tool_result if isinstance(tool_result, dict) else str(tool_result))
                )

                outputs.append(
                    ToolMessage(
                        content=json.dumps(result_content),
                        name=tool_name,
                        tool_call_id=tool_call.get("id", ""),
                    )
                )

            except Exception as e:
                outputs.append(
                    ToolMessage(
                        content=json.dumps({"error": str(e)}),
                        name=tool_name if tool_name else "unknown_tool",
                        tool_call_id=tool_call.get("id", ""),
                    )
                )
        return {"messages": outputs}


def route_tools(state: State):
    """Route to the 'tools' node if the last message has tool calls; otherwise, route to 'done'.

    Parameters
    ----------
    state : State
        The current state containing messages and remaining steps

    Returns
    -------
    str
        Either 'tools' or 'done' based on the state conditions
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "done"


def ChemGraphAgent(state: State, llm: ChatOpenAI, system_prompt: str, tools=None):
    """LLM node that processes messages and decides next actions.

    Parameters
    ----------
    state : State
        The current state containing messages and remaining steps
    llm : ChatOpenAI
        The language model to use for processing
    system_prompt : str
        The system prompt to guide the LLM's behavior
    tools : list, optional
        List of tools available to the agent, by default None

    Returns
    -------
    dict
        Updated state containing the LLM's response
    """

    # Load default tools if no tool is specified.
    if tools is None:
        tools = [run_graspa]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{state['messages']}"},
    ]
    llm_with_tools = llm.bind_tools(tools=tools)
    return {"messages": [llm_with_tools.invoke(messages)]}


def ResponseAgent(state: State, llm: ChatOpenAI, formatter_prompt: str):
    """An LLM agent responsible for formatting final messag

    Parameters
    ----------
    state : State
        The current state containing messages and remaining steps
    llm : ChatOpenAI
        The language model to use for formatting
    formatter_prompt : str
        The prompt to guide the LLM's formatting behavior

    Returns
    -------
    dict
        Updated state containing the formatted response
    """
    messages = [
        {"role": "system", "content": formatter_prompt},
        {"role": "user", "content": f"{state['messages']}"},
    ]
    llm_structured_output = llm.with_structured_output(ResponseFormatter)
    response = llm_structured_output.invoke(messages).model_dump_json()
    return {"messages": [response]}


def construct_graspa_graph(
    llm: ChatOpenAI,
    system_prompt: str = single_agent_prompt,
    structured_output: bool = False,
    formatter_prompt: str = formatter_prompt,
    tools: list = None,
):
    """Construct a geometry optimization graph.

    Parameters
    ----------
    llm : ChatOpenAI
        The language model to use for the graph
    system_prompt : str, optional
        The system prompt to guide the LLM's behavior, by default single_agent_prompt
    structured_output : bool, optional
        Whether to use structured output, by default False
    formatter_prompt : str, optional
        The prompt to guide the LLM's formatting behavior, by default formatter_prompt
    tool: list, optional
        The list of tools for the agent, by default None
    Returns
    -------
    StateGraph
        The constructed geometry optimization graph
    """
    try:
        logger.info("Constructing gRASPA graph")
        checkpointer = MemorySaver()
        if tools is None:
            tools = [run_graspa]
        tool_node = BasicToolNode(tools=tools)
        graph_builder = StateGraph(State)

        if not structured_output:
            graph_builder.add_node(
                "ChemGraphAgent",
                lambda state: ChemGraphAgent(state, llm, system_prompt=system_prompt, tools=tools),
            )
            graph_builder.add_node("tools", tool_node)
            graph_builder.add_conditional_edges(
                "ChemGraphAgent",
                route_tools,
                {"tools": "tools", "done": END},
            )
            graph_builder.add_edge("tools", "ChemGraphAgent")
            graph_builder.add_edge(START, "ChemGraphAgent")
            graph = graph_builder.compile(checkpointer=checkpointer)
            logger.info("gRASPA graph construction completed")
            return graph
        else:
            graph_builder.add_node(
                "ChemGraphAgent",
                lambda state: ChemGraphAgent(state, llm, system_prompt=system_prompt, tools=tools),
            )
            graph_builder.add_node("tools", tool_node)
            graph_builder.add_node(
                "ResponseAgent",
                lambda state: ResponseAgent(state, llm, formatter_prompt=formatter_prompt),
            )
            graph_builder.add_conditional_edges(
                "ChemGraphAgent",
                route_tools,
                {"tools": "tools", "done": "ResponseAgent"},
            )
            graph_builder.add_edge("tools", "ChemGraphAgent")
            graph_builder.add_edge(START, "ChemGraphAgent")
            graph_builder.add_edge("ResponseAgent", END)

            graph = graph_builder.compile(checkpointer=checkpointer)
            logger.info("gRASPA graph construction completed")
            return graph

    except Exception as e:
        logger.error(f"Error constructing graph: {str(e)}")
        raise
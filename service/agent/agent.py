import logging

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from typing import Annotated
from typing_extensions import TypedDict

# Load environment variables from .env file
load_dotenv()

# Define the state for our graph
class State(TypedDict):
    messages: Annotated[list, add_messages]

class chat_agent:
    def __init__(self, model, tools, checkpointer):
        if model is None or tools is None or checkpointer is None:
            raise ValueError("model, tools, and checkpointer can't be None")

        self.model = model
        self.tools = tools
        self.checkpointer = checkpointer

        # Create the custom graph
        self.agent = self._create_graph()

    def _create_graph(self):
        # Create a new graph
        workflow = StateGraph(State)

        # Add nodes
        workflow.add_node("start_node", self._start_node)
        workflow.add_node("agent_node", self._agent_node)
        workflow.add_node("end_node", self._end_node)

        # Add edges
        workflow.add_edge(START, "start_node")
        workflow.add_edge("start_node", "agent_node")
        workflow.add_edge("agent_node", "end_node")
        workflow.add_edge("end_node", END)

        # Compile the graph with checkpointer
        return workflow.compile(checkpointer=self.checkpointer)

    def _start_node(self, state: State):
        """Starting node - logs the incoming message"""
        messages = state["messages"]
        logging.info(f"Pipeline started with {len(messages)} message(s)")
        return state

    def _agent_node(self, state: State):
        """Agent node - processes the message with the LLM"""
        messages = state["messages"]

        # Get the latest human message
        human_message = messages[-1] if messages else None

        if human_message:
            # Call the LLM
            response = self.model.invoke(messages)

            # Return updated state with AI response
            return {"messages": [response]}

        return state

    def _end_node(self, state: State):
        """Ending node - logs completion"""
        messages = state["messages"]
        logging.info(f"Pipeline completed with {len(messages)} message(s)")
        return state

    def handle_message(self, message, thread_id):
        if not message or not thread_id:
            return None, ValueError("message and thread_id can't be None")

        result = self.agent.invoke(
            {"messages": [HumanMessage(content=message)]},
            {"configurable": {"thread_id": thread_id}},
        )

        return result, None
        


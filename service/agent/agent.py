from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

# Load environment variables from .env file
load_dotenv()

class chat_agent:
    def __init__(self, model, tools, checkpointer):
        if model is None or tools is None or checkpointer is None:
            raise ValueError("model, tools, and checkpointer can't be None")

        self.model = model
        self.tools = tools
        self.checkpointer = checkpointer

        self.agent = create_react_agent(
            model=model,
            tools=tools,
            checkpointer=checkpointer,
        )

    def handle_message(self, message, thread_id):
        if not message or not thread_id:
            return None, ValueError("message and thread_id can't be None")

        result = self.agent.invoke(
            {"messages": [HumanMessage(content=message)]},
            {"configurable": {"thread_id": thread_id}},
        )

        return result, None
        


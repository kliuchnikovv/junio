// version 2
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";
import { MemorySaver } from "@langchain/langgraph";
import { createReactAgent } from "@langchain/langgraph/prebuilt";
// import type { BaseTool } from "@langchain/core/tools";

function createAgent() {
    try {
        // Define the tools for the agent to use
        // const agentTools: Array<BaseTool> = [];

        const agentCheckpointer = new MemorySaver();
        const agentModel = new ChatGoogleGenerativeAI({
            model: "gemini-2.0-flash",
        });

        return createReactAgent({
            llm: agentModel,
            tools: [],
            checkpointSaver: agentCheckpointer,
        });
    } catch (e) {
        console.error("Error creating agent:", e);
        process.exit(1);
    }
}

export const agent = createAgent();

# Project Overview

This is a TypeScript project that uses the LangChain.js library to create a conversational AI agent. The agent is built using the `langgraph` module, specifically the `createReactAgent` function. It uses Google's Gemini model (`gemini-2.0-flash`) for language understanding and generation. The agent is designed to be conversational, maintaining memory of the interaction using `MemorySaver`.

# Building and Running

**1. Install Dependencies:**

```bash
npm install
```

**2. Run the Agent:**

To execute the agent, you can use `ts-node`:

```bash
npx ts-node agent.mts
```

# Development Conventions

*   **Modules:** The project uses ES Modules (`import`/`export`).
*   **API Keys:** API keys are managed as environment variables. It is recommended to use a `.env` file and a library like `dotenv` to manage environment variables securely.
*   **Language:** The project is written in TypeScript.

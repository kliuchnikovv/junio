process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

import express from 'express';
import bodyParser from 'body-parser';
import { HumanMessage } from '@langchain/core/messages';
import { agent } from './agent.mjs';

const app = express();
const port = 3000;

app.use(bodyParser.json());

app.post('/invoke', async (req, res) => {
    const { message, thread_id } = req.body;

    if (!message || !thread_id) {
        return res.status(400).json({ error: 'Message and thread_id are required' });
    }

    try {
        const agentFinalState = await agent.invoke(
            { messages: [new HumanMessage(message)] },
            { configurable: { thread_id } },
        );

        res.json(agentFinalState);
    } catch (e) {
        console.error(e);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});

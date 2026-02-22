"""
Chainlit UI for the Takhleeq chatbot. All chatbot logic lives in chatbot.py.
"""
from uuid import uuid4

import chainlit as cl

from chatbot import (
    SESSIONS_DB,
    SQLiteSession,
    stream_agent_response,
)


@cl.on_chat_start
async def on_chat_start():
    """Send welcome message and create SDK session for this chat."""
    session_id = str(uuid4())
    session = SQLiteSession(session_id, SESSIONS_DB)
    cl.user_session.set("session", session)
    cl.user_session.set("session_id", session_id)
    await cl.Message(
        content="👋 Welcome! I'm the **Takhleeq AI Assistant**. How can I help you today?"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Run the agent with streaming and SDK session memory."""
    session = cl.user_session.get("session")
    if session is None:
        session_id = str(uuid4())
        session = SQLiteSession(session_id, SESSIONS_DB)
        cl.user_session.set("session", session)
        cl.user_session.set("session_id", session_id)

    msg = cl.Message(content="")
    await msg.send()

    async for event_type, data in stream_agent_response(session, message.content):
        if event_type == "text":
            await msg.stream_token(data)
        elif event_type == "tool_call":
            await msg.stream_token("\n\n_Searching knowledge base..._\n\n")

    await msg.update()

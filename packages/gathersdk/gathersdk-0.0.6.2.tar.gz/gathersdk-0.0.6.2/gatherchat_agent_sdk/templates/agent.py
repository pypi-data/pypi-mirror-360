#!/usr/bin/env python3
"""
Pydantic AI Agent Example - A GatherChat agent powered by Pydantic AI
"""

import logging
from gatherchat_agent_sdk import MessageRouter
from gatherchat_agent_sdk.agent import AgentContext
from pydantic_ai import Agent as PydanticAgent, RunContext
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

# Create your GatherChat message router
router = MessageRouter()

# Initialize Pydantic AI agent with minimal configuration and deps_type
# You can set the model via environment variable PYDANTIC_AI_MODEL or default to OpenAI
pydantic_agent = PydanticAgent(
    "openai:gpt-4o",
    deps_type=AgentContext,  # Use AgentContext as dependency type
    instructions="You are a helpful AI assistant in a chat room. Be concise and friendly."
)

@pydantic_agent.instructions
def add_context_instructions(ctx: RunContext[AgentContext]) -> str:
    """
    Generate dynamic instructions based on the GatherChat context.
    This gives the AI rich information about the current conversation.
    """
    
    # Build context information
    context_parts = [
        f"You are chatting with {ctx.deps.user.display_name} in '{ctx.deps.chat.name}'.",
        f"There are {len(ctx.deps.chat.participants)} participants in this chat."
    ]
    
    # Add recent conversation history if available
    if ctx.deps.conversation_history:
        context_parts.append("Recent conversation history:")
        for msg in ctx.deps.conversation_history[-3:]:  # Last 3 messages for context
            sender = msg.username or msg.agent_name or "Unknown"
            context_parts.append(f"- {sender}: {msg.content}")
    
    return "\n".join(context_parts)

@router.on_message
async def reply(ctx: AgentContext) -> str:
    """
    Handle incoming messages using Pydantic AI with clean dependency injection.
    
    The AgentContext is passed as a dependency to the Pydantic AI agent,
    which automatically generates contextual instructions and processes the user's message.
    """
    user_name = ctx.user.display_name or ctx.user.username
    
    try:
        # Run the Pydantic AI agent with the full AgentContext as dependency
        # The @instructions decorator will automatically generate rich context
        result = await pydantic_agent.run(ctx.prompt, deps=ctx)
        return result.output
    except Exception as e:
        logging.error(f"Error running Pydantic AI: {e}")
        return f"Sorry {user_name}, I encountered an error processing your message."

if __name__ == "__main__":
    print("🤖 Starting message router...")
    print(f"📍 Using model: gpt")
    print("💡 Set PYDANTIC_AI_MODEL environment variable to use a different model")
    print("💡 Set OPENAI_API_KEY environment variable for OpenAI models")
    router.run()
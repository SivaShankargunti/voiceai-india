"""
India SME Voice AI Agent — Session 1 (Fixed)
Uses: Gemini (LLM) + Deepgram (STT + TTS)
"""

import os
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent
from livekit.plugins import openai, silero, deepgram

load_dotenv()


class IndiaSMEAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""You are a friendly AI voice assistant for Indian small businesses.

LANGUAGE RULES:
- You speak Hindi and English naturally
- If the user speaks Hindi, reply in Hindi
- If the user speaks English, reply in English
- You can mix Hindi-English (Hinglish) naturally
- Keep every response UNDER 25 words (this is voice, not text!)

BEHAVIOR:
- Be warm and polite
- You help with: booking appointments, answering FAQs, taking messages
- If unsure, say: Main aapko humari team se connect karta hoon
- If someone says stop or band karo — say goodbye politely

COMPLIANCE:
- Identify yourself as an AI assistant
- Never give medical, legal, or financial advice
"""
        )

    async def on_user_turn_completed(self, chat_ctx, new_message):
        if new_message.text_content:
            print(f"  User said: {new_message.text_content}")


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    print("Connected to LiveKit room!")

    session = AgentSession(
        stt=deepgram.STT(
            model="nova-3",
            language="hi",
        ),
        llm=openai.LLM(
            model="gemini-2.5-flash",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("GOOGLE_API_KEY"),
        ),
        tts=deepgram.TTS(),
        vad=silero.VAD.load(),
    )

    await session.start(
        room=ctx.room,
        agent=IndiaSMEAgent(),
    )

    print("Agent is ready!")


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )
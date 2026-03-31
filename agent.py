"""
India SME Voice AI Agent — V2
Now loads business config from backend + uses industry templates
"""

import os
import httpx
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent
from livekit.plugins import openai, silero, deepgram

from agent.templates import get_template

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class IndiaSMEAgent(Agent):
    """Voice AI agent that adapts per business using templates."""

    def __init__(self, business_config: dict):
        self.business = business_config
        template = get_template(business_config.get("industry", "general"))

        # Build the system prompt from template + business info
        system_prompt = template["system_prompt"].format(
            business_name=business_config.get("name", "our business"),
            language=business_config.get("language", "Hindi and English"),
        )

        # Add compliance rules to every agent
        system_prompt += """

COMPLIANCE (ALWAYS FOLLOW):
- You are an AI assistant — ALWAYS identify yourself as AI at the start
- If caller says "stop", "band karo", "ruko", "don't call" — say goodbye immediately
- Never give medical, legal, or financial advice
- Never share personal information of any caller
- If unsure about anything: offer to connect to a human
"""

        super().__init__(instructions=system_prompt)
        self.greeting = template["greeting"].format(
            business_name=business_config.get("name", "our business"),
        )

    async def on_user_turn_completed(self, chat_ctx, new_message):
        if new_message.text_content:
            text = new_message.text_content
            print(f"  User said: {text}")

            # Check for opt-out keywords
            opt_out_words = ["stop", "band karo", "ruko", "mat karo", "don't call"]
            if any(word in text.lower() for word in opt_out_words):
                print("  [COMPLIANCE] Opt-out detected!")

            # Log call to backend (non-blocking)
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"{BACKEND_URL}/api/business/{self.business.get('id', 'unknown')}/calls/log",
                        json={
                            "contact_phone": "unknown",
                            "duration_seconds": 0,
                            "outcome": "in_progress",
                            "call_type": "service",
                            "direction": "inbound",
                            "transcript": text,
                        },
                        timeout=2.0,
                    )
            except Exception:
                pass  # Don't break the call if logging fails


async def fetch_business_config(room_name: str) -> dict:
    """
    Fetch business config from backend based on room metadata.
    In production: room name maps to a business ID.
    For now: use a default config or fetch from backend.
    """
    # Try to extract business_id from room name
    # Format: "biz_xxxxx_room" or just use default
    try:
        async with httpx.AsyncClient() as client:
            # Try to get business list and use the first one
            resp = await client.get(f"{BACKEND_URL}/api/businesses", timeout=3.0)
            if resp.status_code == 200:
                businesses = resp.json()
                if businesses:
                    # Get full details of first business
                    biz_id = businesses[0]["id"]
                    detail_resp = await client.get(
                        f"{BACKEND_URL}/api/business/{biz_id}", timeout=3.0
                    )
                    if detail_resp.status_code == 200:
                        return detail_resp.json()
    except Exception as e:
        print(f"  Could not fetch from backend: {e}")

    # Fallback default config
    return {
        "id": "default",
        "name": "Demo Business",
        "industry": "general",
        "language": "Hindi and English",
    }


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()
    print("Connected to LiveKit room!")
    print(f"Room: {ctx.room.name}")

    # Fetch business config from backend
    business_config = await fetch_business_config(ctx.room.name)
    print(f"Loaded business: {business_config.get('name')} ({business_config.get('industry')})")

    # Create the agent with business-specific template
    india_agent = IndiaSMEAgent(business_config)

    session = AgentSession(
        stt=deepgram.STT(
            model="nova-3",
            language=business_config.get("language", "hi")[:2],  # "hi" or "en"
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
        agent=india_agent,
    )

    print(f"Agent ready! Template: {business_config.get('industry')}")


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(entrypoint_fnc=entrypoint)
    )
#!/usr/bin/env python3
import os
import asyncio
import argparse
from dotenv import load_dotenv

# Core Agents SDK
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions

# Plugins for each pipeline component
from livekit.plugins import deepgram, openai, silero, azure

# Load environment variables from .env or Kubernetes Secrets
load_dotenv()

class Assistant(Agent):
    def __init__(self):
        super().__init__(
            instructions=(
                "You are a voice assistant created by L7mp Technologies. "
                "Your interface with users is voice-only. Use short, clear replies."
            )
        )

async def entrypoint(ctx: agents.JobContext):
    # Connect to LiveKit
    await ctx.connect()

    # Configure the session with provider plugins
    session = AgentSession(
        stt=deepgram.STT(api_key=os.getenv("DEEPGRAM_API_KEY")),
        llm=openai.LLM(api_key=os.getenv("OPENAI_API_KEY")),
        tts=openai.TTS(api_key=os.getenv("OPENAI_API_KEY")),
        vad=silero.VAD.load(),
        # Optionally add Azure Speech:
        # stt=azure.STT(speech_key=os.getenv("AZURE_SPEECH_KEY"),
        #               speech_region=os.getenv("AZURE_SPEECH_REGION"))
    )

    # Start the conversational session
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions()
    )

if __name__ == "__main__":
    # Bake LiveKit credentials into WorkerOptions
    opts = agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
    )
    agents.cli.run_app(opts)

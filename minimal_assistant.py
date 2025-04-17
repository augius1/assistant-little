#!/usr/bin/env python3
import os
import logging
from dotenv import load_dotenv
import asyncio

# Core Agents SDK imports
from livekit.agents import (
    WorkerOptions,    # defines how the worker should run
    cli,              # provides the CLI entrypoint with start/dev/connect/download-files
    AutoSubscribe,    # for controlling which tracks to auto‑subscribe
    JobContext,       # runtime context passed to your entrypoint
    JobProcess,       # gives access to process-local userdata
)
from livekit.agents.pipeline import VoicePipelineAgent  # high‑level voice pipeline agent :contentReference[oaicite:1]{index=1}

# Plugins for VAD, STT, LLM, TTS
from livekit.plugins import deepgram, openai, silero, azure  # replace/extend as needed :contentReference[oaicite:2]{index=2}

# Load environment variables (API keys, LIVEKIT_URL, etc.)
load_dotenv()


logger = logging.getLogger("minimal-assistant")


def prewarm(proc: JobProcess):
    """
    Optional: pre-load any heavy model artifacts into JobProcess.userdata.
    Here we load the Silero VAD model once per process.
    """
    proc.userdata["vad"] = silero.VAD.load()  # VAD.load() is the recommended preload :contentReference[oaicite:3]{index=3}


async def entrypoint(ctx: JobContext):
    """
    This function is called whenever a new LiveKit job is assigned to your worker.
    You get a JobContext to connect to the room, wait for participants, and then
    run your VoicePipelineAgent.
    """
    # Build the initial chat context for the LLM
    initial_ctx = openai.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by L7mp Technologies. "
            "Your interface with users is voice-only. "
            "Use short, clear responses and avoid unpronounceable punctuation."
        )
    )

    # Ensure the process has VAD loaded (from prewarm)
    vad = ctx.proc.userdata["vad"]

    # Configure STT, LLM, TTS with API keys from env
    stt = deepgram.STT(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = openai.LLM(api_key=os.getenv("OPENAI_API_KEY"))
    tts = openai.TTS(api_key=os.getenv("OPENAI_API_KEY"))

    # Instantiate the voice pipeline agent
    agent = VoicePipelineAgent(
        vad=vad,
        stt=stt,
        llm=llm,
        tts=tts,
        chat_ctx=initial_ctx,
    )

    # Connect to the LiveKit room, subscribing only to audio tracks
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)  # default is SUBSCRIBE_ALL :contentReference[oaicite:4]{index=4}

    # Wait for a publisher (human) to join the room
    participant = await ctx.wait_for_participant()

    # Start the agent in that room for that participant
    agent.start(ctx.room, participant)

    # Greet the user
    await agent.say("Hello! How can I assist you today?", allow_interruptions=True)


if __name__ == "__main__":
    # Define how the worker should run: entrypoint + optional prewarm
    opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
    )

    # Launch the CLI, which gives you commands:
    #   * `python minimal_assistant.py start`  → production start
    #   * `python minimal_assistant.py dev`    → dev mode with reload & debug
    #   * `python minimal_assistant.py connect --room=<room>` → connect to specific room
    #   * `python minimal_assistant.py download-files` → download model assets
    cli.run_app(opts)  # entrypoint into the official CLI :contentReference[oaicite:5]{index=5}

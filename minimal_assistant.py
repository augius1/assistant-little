import os
import asyncio
import argparse
from dotenv import load_dotenv

# Correct imports from the dotted namespace:
from livekit.agents.runner import Runner
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero, azure


def create_agent():
    """
    Build and return a VoicePipelineAgent with VAD, STT, LLM, and TTS
    configured from environment variables.
    """
    initial_ctx = openai.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by L7mp Technologies. "
            "Your interface with users will be voice. "
            "You should use short and concise responses, avoiding unpronounceable punctuation."
        )
    )
    vad = silero.VAD()
    stt = deepgram.STT(api_key=os.getenv("DEEPGRAM_API_KEY"))
    llm = openai.LLM(api_key=os.getenv("OPENAI_API_KEY"))
    tts = openai.TTS(api_key=os.getenv("OPENAI_API_KEY"))
    return VoicePipelineAgent(
        vad=vad,
        stt=stt,
        llm=llm,
        tts=tts,
        chat_ctx=initial_ctx,
    )


def download_files():
    """
    Prefetch and cache all necessary model files for the agent.
    """
    agent = create_agent()
    agent.download_assets()
    print("✅ Assets downloaded successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="Minimal LiveKit Voice Agent"
    )
    parser.add_argument(
        'command',
        choices=['dev', 'start', 'download-files'],
        help="'download-files' to prefetch models, 'dev' or 'start' to run agent"
    )
    args = parser.parse_args()

    # Load .env or environment vars (e.g., Kubernetes secrets)
    load_dotenv()

    if args.command == 'download-files':
        download_files()
        return

    # Always prefetch models before running
    download_files()

    # Create and run the agent via the Runner class
    runner = Runner(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
        agent_factory=create_agent,
    )
    asyncio.run(runner.run())


if __name__ == '__main__':
    main()

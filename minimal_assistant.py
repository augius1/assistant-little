import os
import asyncio
import argparse
from dotenv import load_dotenv

from livekit_agents.runner import Runner
from livekit_agents.voice_pipeline import VoicePipelineAgent
from livekit_agents import deepgram, openai, silero, azure


def create_agent():
    # (unchanged) …
    initial_ctx = openai.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by L7mp Technologies. Your interface with users will be voice. "
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
    agent = create_agent()
    agent.download_assets()
    print("✅ Assets downloaded successfully.")


def main():
    parser = argparse.ArgumentParser(description="Minimal LiveKit Voice Agent")
    parser.add_argument('command', choices=['dev', 'start', 'download-files'],
                        help="'download-files' to prefetch models, 'dev' or 'start' to run agent")
    args = parser.parse_args()

    load_dotenv()  # load .env or env-vars from Kubernetes Secrets

    if args.command == 'download-files':
        download_files()
        return

    # **NEW**: always ensure assets are present before running
    download_files()

    runner = Runner(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
        agent_factory=create_agent,
    )
    asyncio.run(runner.run())


if __name__ == '__main__':
    main()

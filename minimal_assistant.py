import os
import asyncio
import argparse
from dotenv import load_dotenv

# LiveKit Agents imports
from livekit_agents.runner import Runner
from livekit_agents.voice_pipeline import VoicePipelineAgent
from livekit_agents import deepgram, openai, silero, azure


def create_agent():
    """
    Factory to create and configure the voice pipeline agent.
    """
    # Build initial system prompt for the LLM
    initial_ctx = openai.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by L7mp Technologies. Your interface with users will be voice. "
            "You should use short and concise responses, avoiding unpronounceable punctuation."
        )
    )

    # Select Voice Activity Detection (VAD) engine
    vad = silero.VAD()

    # Select Speech-to-Text (STT)
    stt = deepgram.STT(api_key=os.getenv("DEEPGRAM_API_KEY"))

    # Select Language Model (LLM)
    # Use OpenAI; switch to Azure by using openai.LLM.with_azure()
    llm = openai.LLM(api_key=os.getenv("OPENAI_API_KEY"))

    # Select Text-to-Speech (TTS)
    tts = openai.TTS(api_key=os.getenv("OPENAI_API_KEY"))

    # Assemble the voice pipeline agent
    agent = VoicePipelineAgent(
        vad=vad,
        stt=stt,
        llm=llm,
        tts=tts,
        chat_ctx=initial_ctx,
    )
    return agent


def download_files():
    """
    Pre-download any required models or assets at build time.
    """
    agent = create_agent()
    # This will trigger downloads for VAD, STT, TTS models
    agent.download_assets()
    print("✅ Assets downloaded successfully.")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Minimal LiveKit Voice Agent")
    parser.add_argument('command', choices=['dev', 'start', 'download-files'],
                        help="'download-files' to prefetch models, 'dev' or 'start' to run agent")
    args = parser.parse_args()

    # Load environment variables from .env (if present)
    load_dotenv()

    # Handle download step separately
    if args.command == 'download-files':
        download_files()
        return

    # For 'dev' or 'start', spin up the LiveKit Runner
    runner = Runner(
        url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
        agent_factory=create_agent,
    )

    # Run the agent event loop
    asyncio.run(runner.run())


if __name__ == '__main__':
    main()

# src/manager/manager_agent.py

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fix FFmpeg path for MoviePy
import imageio_ffmpeg as ffmpeg
os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg.get_ffmpeg_exe()

# Import all agents
from src.agents.trend_hunter import TrendHunter
from src.agents.content_strategist import ContentStrategist
from src.agents.script_writer import ScriptWriter
from src.agents.voice_agent import VoiceAgent
from src.agents.media_agent import MediaAgent
from src.agents.video_agent import VideoAgent
from src.agents.seo_agent import SEOAgent
from src.agents.upload_agent import UploadAgent
from src.agents.performance_agent import PerformanceAgent
from src.agents.learning_agent import LearningAgent

# Providers
from src.providers.pexels_provider import PexelsProvider
from src.providers.pixabay_provider import PixabayProvider


def run_pipeline():

    print("\n🚀 STARTING AI CONTENT FACTORY PIPELINE\n")

    try:
        # -----------------------------
        # Providers & Agents Setup
        # -----------------------------
        pexels_provider = PexelsProvider()
        pixabay_provider = PixabayProvider()

        providers = [pexels_provider, pixabay_provider]

        media_agent = MediaAgent(providers)
        video_agent = VideoAgent(media_agent)

        # -----------------------------
        # 1️⃣ TrendHunter
        # -----------------------------
        trend_agent = TrendHunter()
        trends = trend_agent.get_trends()

        if not trends or len(trends) == 0:
            print("⚠ No trends found, using fallback topic")
            trends = ["technology facts", "AI future", "space facts"]

        print("🔥 Trends:", trends)

        # -----------------------------
        # 2️⃣ Performance Monitoring
        # -----------------------------
        performance_agent = PerformanceAgent()
        performance_data = performance_agent.collect_metrics()

        # -----------------------------
        # 3️⃣ Content Strategist
        # -----------------------------
        strategist = ContentStrategist()

        selected_topic = strategist.select_topic(
            trends,
            performance_data
        )

        print("🎯 Selected Topic:", selected_topic)

        if not selected_topic:
            print("❌ No topic selected. Aborting.")
            return

        # -----------------------------
        # 4️⃣ Script Writer
        # -----------------------------
        script_writer = ScriptWriter()
        script = script_writer.generate_script(selected_topic)

        if not script or len(script.strip()) == 0:
            print("❌ Script generation failed")
            return

        print("📝 Script Generated")

        # -----------------------------
        # 5️⃣ Voice Agent
        # -----------------------------
        voice_agent = VoiceAgent()
        voice_file = voice_agent.text_to_speech(script)

        if not voice_file or not os.path.exists(voice_file):
            print("❌ Voice generation failed")
            return

        print("🎙 Voice Ready:", voice_file)

        # -----------------------------
        # 6️⃣ Video Agent
        # -----------------------------
        video_file = video_agent.create_video(
            script,
            voice_file
        )

        if not video_file or not os.path.exists(video_file):
            print("❌ Video creation failed")
            return

        print("🎬 Video Created:", video_file)

        # -----------------------------
        # 7️⃣ SEO / Caption Agent
        # -----------------------------
        seo_agent = SEOAgent()
        caption = seo_agent.generate_caption(selected_topic, script)

        if not caption:
            caption = f"{selected_topic} #shorts #viral"

        print("🏷 Caption:", caption)

        # -----------------------------
        # 8️⃣ Upload Agent
        # -----------------------------
        upload_agent = UploadAgent()
        upload_agent.upload(video_file, caption)

        print("📤 Upload Completed")

        # -----------------------------
        # 9️⃣ Learning Agent
        # -----------------------------
        learning_agent = LearningAgent()
        learning_agent.analyze_performance(selected_topic)

        print("📊 Learning Updated")

        print("\n✅ PIPELINE COMPLETED SUCCESSFULLY\n")

    except Exception as e:
        print("❌ PIPELINE ERROR:", e)


# ---------------------------------
# ENTRY POINT
# ---------------------------------
if __name__ == "__main__":
    run_pipeline()
     
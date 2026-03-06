# src/manager/manager_agent.py

import os
from datetime import datetime

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
from src.agents.scheduler_agent import SchedulerAgent
from src.agents.upload_agent import UploadAgent
from src.agents.performance_agent import PerformanceAgent
from src.agents.learning_agent import LearningAgent

def main():
    print("🚀 Starting AI Content Factory Pipeline")

    # 1️⃣ TrendHunter
    trend_agent = TrendHunter()
    trends = trend_agent.search_trends()
    print("✅ Trends Found:", trends)

    # 2️⃣ Performance Monitoring (Optional at start)
    performance_agent = PerformanceAgent()
    performance_data = performance_agent.collect_metrics()

    # 3️⃣ Content Strategist
    strategist = ContentStrategist()
    selected_topic = strategist.select_topic(trends, performance_data)
    print("✅ Selected Topic:", selected_topic)

    # 4️⃣ Script Writer
    script_writer = ScriptWriter()
    script = script_writer.generate_script(selected_topic)
    print("✅ Script Created")

    # 5️⃣ Voice Agent
    voice_agent = VoiceAgent()
    voice_file = voice_agent.text_to_speech(script)
    print("✅ Voice file created:", voice_file)

    # 6️⃣ Media Agent
    media_agent = MediaAgent()
    clips = media_agent.select_media(selected_topic)

    # 7️⃣ Video Agent
    video_agent = VideoAgent(media_agent)
    video_file = video_agent.create_video(
    topic=selected_topic,
    audio_file=voice_file,
    duration=60
    )
    
    print("✅ Video created:", video_file)

    # 8️⃣ SEO / Caption Agent
    seo_agent = SEOAgent()
    caption = seo_agent.generate_caption(selected_topic)
    print("✅ Caption generated:", caption)

    # 9️⃣ Scheduler Agent
    scheduler = SchedulerAgent()
    scheduler.check_schedule()
    print("⏰ Scheduler checked")

    # 🔟 Upload Agent
    upload_agent = UploadAgent()
    upload_agent.upload(video_file, caption)
    print("✅ Upload simulated successfully")

    # 1️⃣1️⃣ Learning Agent
    learning_agent = LearningAgent()
    learning_agent.analyze_performance(selected_topic)
    print("✅ Learning completed")

    print("🎉 Pipeline Completed")

if __name__ == "__main__":
    main()
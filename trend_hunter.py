import os
import random
import json
import re
from googleapiclient.discovery import build
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class TrendHunter:
    def __init__(self):
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.history_file = "data/history.txt"

    # ---------------------------
    # Avoid repetition
    # ---------------------------
    def is_used(self, topic):
        if not os.path.exists(self.history_file):
            return False

        with open(self.history_file, "r", encoding="utf-8") as f:
            return topic.lower() in f.read().lower()

    def save_topic(self, topic):
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(topic + "\n")

    # ---------------------------
    # Get YouTube Trending Titles
    # ---------------------------
    def get_youtube_trends(self):
        try:
            if not self.youtube_api_key:
                print("⚠ YOUTUBE_API_KEY not found in environment variables!")
                print("   Please set it in your .env file or system environment")
                return []

            youtube = build("youtube", "v3", developerKey=self.youtube_api_key)

            request = youtube.videos().list(
                part="snippet",
                chart="mostPopular",
                regionCode="IN",
                maxResults=25
            )

            response = request.execute()

            titles = [item["snippet"]["title"] for item in response["items"]]

            return titles

        except Exception as e:
            print("⚠ YouTube API failed:", e)
            return []

    # ---------------------------
    # Convert Titles → Viral Topics (OpenAI)
    # ---------------------------
    def generate_viral_topics(self, titles):

        prompt = f"""
You are a viral content strategist for YouTube Shorts.

Given these trending video titles:
{titles}

Generate 10 SHORT, VIRAL, HIGH-ENGAGEMENT topics.

Rules:
- Keep each topic under 10 words
- Make them curiosity-driven
- Avoid copying titles directly
- Make them suitable for YouTube Shorts
- Make them addictive and clickable

IMPORTANT: Return ONLY a valid JSON array of strings, like:
["topic 1", "topic 2", "topic 3"]
No other text, no explanations.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.choices[0].message.content

            # Try to parse as JSON first
            try:
                topics = json.loads(text)
            except json.JSONDecodeError:
                # Fallback: extract list items using regex
                # Look for patterns like ["item1", "item2"] or ['item1', 'item2']
                match = re.search(r'\[([^\]]+)\]', text)
                if match:
                    items = match.group(1)
                    # Parse each item
                    topics = []
                    for item in re.finditer(r'["\']([^"\']+)["\']', items):
                        topics.append(item.group(1))
                else:
                    # Last resort: split by newlines and clean
                    topics = [line.strip().lstrip('-•').strip() for line in text.split('\n') if line.strip()]

            return topics

        except Exception as e:
            print("⚠ OpenAI topic generation failed:", e)
            return []

    # ---------------------------
    # Main Function
    # ---------------------------
    def get_trends(self):

        print("🔍 Fetching YouTube trends...")

        titles = self.get_youtube_trends()

        if not titles:
            print("⚠ Using fallback topics")
            topics = [
                "Mind blowing space facts",
                "Hidden smartphone tricks",
                "Psychology hacks",
                "Future AI technology",
                "Things disappearing soon"
            ]
        else:
            topics = self.generate_viral_topics(titles)

        # Remove used topics
        topics = [t for t in topics if not self.is_used(t)]

        if not topics:
            print("⚠ Resetting topic history")
            open(self.history_file, "w").close()
            topics = self.generate_viral_topics(titles)

        selected = random.choice(topics)

        print("✅ Selected Topic:", selected)

        self.save_topic(selected)

        return selected
# src/agents/content_strategist.py

import os
import random
from openai import OpenAI
from src.utils.config import OPENAI_MODEL, TARGET_REGION


class ContentStrategist:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def select_topic(self, trends, performance_data=None):

        print("🧠 Selecting VIRAL topic...")

        # -----------------------------
        # STEP 1: Use best past performer
        # -----------------------------
        best_past = None
        if performance_data:
            try:
                best_past = max(performance_data, key=performance_data.get)
                print("📊 Best past topic:", best_past)
            except:
                pass

        # -----------------------------
        # STEP 2: AI Topic Generation
        # -----------------------------
        if self.client:
            try:
                trends_list = "\n".join([f"- {t}" for t in trends])

                context = ""
                if best_past:
                    context = f"\nPreviously high-performing topic:\n- {best_past}\n"

                prompt = f"""
You are a viral YouTube Shorts expert for {TARGET_REGION}.

Your job is to create a HIGHLY CLICKABLE topic.

Trending topics:
{trends_list}
{context}

STRICT RULES:
- Pick ONE topic
- Convert into emotional trigger:
  (fear / curiosity / shocking / controversial)
- Must feel personal ("you", "your")
- Max 10 words
- Must feel like viewer CANNOT ignore it

BAD examples:
- AI future
- Space facts

GOOD examples:
- Your phone is secretly tracking you
- This mistake is destroying your brain
- Will AI replace YOU in 2026?

OUTPUT ONLY FINAL TOPIC.
"""

                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=1.0,
                    max_tokens=50
                )

                topic = response.choices[0].message.content.strip()

                # Safety check
                if len(topic.split()) > 15:
                    raise ValueError("Topic too long")

                print("🔥 Viral Topic:", topic)
                return topic

            except Exception as e:
                print("⚠ AI failed:", e)

        # -----------------------------
        # STEP 3: SMART FALLBACK
        # -----------------------------
        fallback = random.choice(trends)

        # Convert fallback into better hook
        improved = f"You are ignoring this about {fallback}"

        print("⚠ Using fallback topic:", improved)
        return improved
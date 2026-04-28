# src/agents/seo_agent.py

import os
from openai import OpenAI
from src.utils.config import OPENAI_MODEL


class SEOAgent:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_caption(self, topic, script=None):

        print("📈 Generating VIRAL caption...")

        if self.client:
            try:
                prompt = f"""
Create a HIGH CTR YouTube Shorts caption.

Topic: {topic}

Rules:
- First line = curiosity hook
- Create urgency or fear
- Add CTA
- Add 6-8 hashtags
- Include #Shorts #Viral

Example:
"This is happening silently...

You won’t notice until it’s too late.

Follow for more.

#Shorts #Viral #Facts"
"""

                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=150
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                print("⚠ AI failed:", e)

        return f"{topic}\nFollow for more\n#Shorts #Viral"
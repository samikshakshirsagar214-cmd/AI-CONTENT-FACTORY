# src/agents/script_writer.py

import os
from openai import OpenAI
from src.utils.config import OPENAI_MODEL, SCRIPT_WORD_COUNT


class ScriptWriter:

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def generate_script(self, topic):

        print("✍ Generating VIRAL script...")

        if self.client:
            try:
                prompt = f"""
Create a HIGH-RETENTION YouTube Shorts script.

Topic: {topic}

GOAL:
Maximize watch time and prevent scrolling.

STRICT RULES:
- First line MUST shock or create tension
- NEVER start with "Did you know"
- Each line MUST be 5–8 words max
- Each line must create curiosity for next
- No explanations, only engaging statements
- Sound like talking to ONE person

STRUCTURE:
1. Pattern interrupt hook
2. Build curiosity (2–3 lines)
3. Reveal/twist
4. Strong CTA

PSYCHOLOGY:
Use at least one:
- Fear ("You’re doing this wrong")
- Curiosity ("Nobody is talking about this")
- Urgency ("This is happening right now")

EXAMPLE STYLE:
"You’re already being watched…

And you don’t even know it.

This is happening through your phone.

Most people ignore this.

That’s the mistake.

Follow for more."

Generate now.
"""
                
                


                response = self.client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9,
                    max_tokens=250
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                print("⚠ AI failed:", e)

        # fallback
        return f"""
This will shock you about {topic}...

Most people ignore this.

But it can change everything.

Follow for more.
""".strip()
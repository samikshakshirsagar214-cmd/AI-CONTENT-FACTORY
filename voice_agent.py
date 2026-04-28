# src/agents/voice_agent.py

import os
import sys
import subprocess
from openai import OpenAI


class VoiceAgent:

    def __init__(self):

        # 🔥 Control switch (important for cost)
        self.use_ai = True

        api_key = os.getenv("OPENAI_API_KEY")

        if self.use_ai and api_key:
            self.client = OpenAI(api_key=api_key)
            print("🤖 OpenAI TTS enabled")
        else:
            self.client = None
            print("⚠ OpenAI not configured. Using fallback voice.")

    def text_to_speech(self, text):

        print("🎙 VoiceAgent: Converting script to voice...")

        output_mp3 = "data/temp/voice.mp3"
        os.makedirs(os.path.dirname(output_mp3), exist_ok=True)

        # -----------------------------
        # 🤖 OpenAI TTS (BEST QUALITY)
        # -----------------------------
        if self.client:
            try:
                print("🎙 Using OpenAI TTS...")

                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice="nova",     # 🔥 Better for reels (clear female voice)
                    input=text,
                    speed=1.1
                )

                response.stream_to_file(output_mp3)

                if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 0:
                    print("✅ Voice created (OpenAI):", output_mp3)
                    return output_mp3

                raise RuntimeError("Empty OpenAI TTS output")

            except Exception as e:
                print(f"⚠ OpenAI TTS failed: {e}")

        # -----------------------------
        # 🔁 Fallback 1: gTTS
        # -----------------------------
        try:
            print("🎙 Using gTTS fallback...")
            from gtts import gTTS

            tts = gTTS(text=text, lang="en", slow=False)
            tts.save(output_mp3)

            if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 0:
                print("✅ Voice created (gTTS):", output_mp3)
                return output_mp3

        except Exception as e:
            print(f"⚠ gTTS failed: {e}")

        # -----------------------------
        # 🔁 Fallback 2: Windows TTS
        # -----------------------------
        if sys.platform == "win32":
            print("🎙 Using Windows TTS fallback...")
            output_wav = "data/temp/voice.wav"

            try:
                text_file = os.path.abspath("data/temp/voice_text.txt")

                with open(text_file, "w", encoding="utf-8") as f:
                    f.write(text)

                abs_wav = os.path.abspath(output_wav)

                command = [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"$text = Get-Content -Raw -Path '{text_file}'; "
                    f"Add-Type -AssemblyName System.Speech; "
                    f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    f"$synth.SetOutputToWaveFile('{abs_wav}'); "
                    "$synth.Speak($text); $synth.Dispose();"
                ]

                subprocess.run(command, check=True, capture_output=True, text=True)

                if os.path.exists(output_wav) and os.path.getsize(output_wav) > 0:
                    print("✅ Voice created (Windows):", output_wav)
                    return output_wav

            except subprocess.CalledProcessError as e:
                print("⚠ Windows TTS failed:", e)

        print("❌ All TTS methods failed")
        return None
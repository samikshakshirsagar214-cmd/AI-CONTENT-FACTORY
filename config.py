# ============================================================
# OpenAI Configuration
# Paste your API key here when you get it from platform.openai.com
# ============================================================


# Model to use — gpt-4o is best, gpt-3.5-turbo is cheaper
OPENAI_MODEL = "gpt-4o"

# ============================================================
# YouTube API Key Configuration
# Get your API key from: https://console.cloud.google.com/
# 1. Go to APIs & Services > Credentials
# 2. Click "Create Credentials" > "API Key"
# 3. Copy the key and set it as YOUTUBE_API_KEY environment variable
#    Or paste it below (not recommended for security)
# ============================================================

# YouTube API Key for fetching trending videos (TrendHunter)
# Set as environment variable: YOUTUBE_API_KEY
# Or uncomment and add your key here:
# YOUTUBE_API_KEY = "YOUR_API_KEY_HERE"

# Target audience region for trends/scripts
TARGET_REGION = "India"

# YouTube Shorts script length (words)
SCRIPT_WORD_COUNT = 80

# Caption max length
CAPTION_MAX_LENGTH = 150
import re

def extract_keywords(scene):

    scene = scene.lower()

    words = re.findall(r'\b[a-z]+\b', scene)

    stop_words = {
        "the","is","a","an","and","to","of","in","on",
        "for","with","that","this","it","are"
    }

    keywords = [w for w in words if w not in stop_words]

    # 🔥 Improve mapping
    if "space" in scene:
        return ["space", "galaxy", "planets"]
    if "ai" in scene or "technology" in scene:
        return ["ai", "technology", "robot"]
    if "future" in scene:
        return ["future", "innovation", "city"]

    return keywords[:3] if keywords else ["nature"]
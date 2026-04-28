SCENE_MAP = {

    "space": [
        "galaxy stars universe",
        "planet earth from space",
        "space nebula stars",
        "astronomy telescope sky"
    ],

    "ai": [
        "artificial intelligence robot",
        "futuristic technology computer",
        "robot working laboratory",
        "digital brain network"
    ],

    "technology": [
        "computer data center",
        "programming computer screen",
        "future technology interface"
    ],

    "ocean": [
        "deep ocean underwater",
        "sea waves aerial",
        "coral reef underwater"
    ],

    "nature": [
        "beautiful nature landscape",
        "forest river mountains",
        "sunrise nature aerial"
    ]
}


def map_scene(text):

    text = text.lower()

    for key in SCENE_MAP:
        if key in text:
            return SCENE_MAP[key]

    return ["nature landscape"]
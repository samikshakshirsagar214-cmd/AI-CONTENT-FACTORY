def split_script(script):

    scenes = script.split(".")
    scenes = [scene.strip() for scene in scenes if scene.strip()]

    return scenes
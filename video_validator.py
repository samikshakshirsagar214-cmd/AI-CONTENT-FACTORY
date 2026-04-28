from moviepy.video.io.VideoFileClip import VideoFileClip

def validate_videos(video_paths):

    valid = []

    for path in video_paths:

        try:

            clip = VideoFileClip(path)

            if clip.duration > 1:
                valid.append(path)

            clip.close()

        except Exception:

            print("Invalid video:", path)

    return valid
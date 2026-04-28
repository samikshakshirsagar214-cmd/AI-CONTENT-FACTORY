import os
import re
import time
import subprocess
import imageio_ffmpeg as ffmpeg
import PIL.Image
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip

# Pillow fix
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from src.utils.video_validator import validate_videos


class VideoAgent:

    def __init__(self, media_agent):
        self.media_agent = media_agent
        self.output_path = os.path.abspath("data/temp/final_video.mp4")

    def split_script(self, script):
        parts = re.split(r'[\.\?!]\s+|\n+', script)
        parts = [s.strip() for s in parts if s.strip()]

        if len(parts) == 1 and len(parts[0].split()) > 20:
            words = parts[0].split()
            parts = []
            chunk = []
            for word in words:
                chunk.append(word)
                if len(chunk) >= 12:
                    parts.append(" ".join(chunk))
                    chunk = []
            if chunk:
                parts.append(" ".join(chunk))

        return parts

    def create_video(self, script, audio_file, duration=15):

        print("[START] Starting video creation...")

        scenes = self.split_script(script)
        print(f"[INFO] Scene count: {len(scenes)}")

        max_clips = 3
        selected_scenes = scenes[:max_clips]
        print(f"[INFO] Using {len(selected_scenes)} scenes for shorter video")

        video_paths = []

        # 🎯 Step 1: Collect videos
        for i, scene in enumerate(selected_scenes):
            path = self.media_agent.select_media(scene, i)
            if path and os.path.exists(path):
                video_paths.append(os.path.abspath(path))

        print("[INFO] Clips:", video_paths)

        if not video_paths:
            print("[ERROR] No videos found")
            return None

        video_paths = validate_videos(video_paths)

        if not video_paths:
            print("[ERROR] No valid videos")
            return None

        ffmpeg_path = ffmpeg.get_ffmpeg_exe()
        processed_clips = []

        # [STEP 2] Normalize and trim all clips
        clip_duration = max(5, min(8, duration / len(video_paths)))
        print(f"[INFO] Trim each clip to up to {clip_duration:.1f} seconds")

        os.makedirs("data/temp", exist_ok=True)

        for i, path in enumerate(video_paths):
            out_path = f"data/temp/clip_{i}.mp4"

            subprocess.run([
                ffmpeg_path,
                "-y",
                "-i", path,
                "-t", str(clip_duration),
                "-vf", "scale=720:1280,fps=24",
                "-c:v", "libx264",
                "-preset", "fast",
                "-pix_fmt", "yuv420p",
                "-an",
                out_path
            ], check=True, capture_output=True, text=True)

            processed_clips.append(os.path.abspath(out_path))

        print("[OK] Clips normalized")

        # [STEP 3] Create concat file
        concat_file = "data/temp/concat.txt"

        with open(concat_file, "w", encoding="utf-8") as f:
            for path in processed_clips:
                safe_path = path.replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        temp_video = "data/temp/temp_video.mp4"
        final_output = self.output_path

        print("[INFO] Combining clips...")

        subprocess.run([
            ffmpeg_path,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-an",
            temp_video
        ], check=True, capture_output=True, text=True)

        if not os.path.exists(temp_video) or os.path.getsize(temp_video) == 0:
            print("[ERROR] Failed to create combined temp video")
            return None

        print("[OK] Video combined")

        # ─────────────────────────────────────────────
        # FIXED: proper file-based audio check using ffprobe
        # ─────────────────────────────────────────────
        def has_valid_audio(path):
            """Check if file exists, is non-empty, and contains an audio stream."""
            if not path or not os.path.exists(path) or os.path.getsize(path) < 100:
                return False
            result = subprocess.run(
                [ffmpeg_path, "-i", path],
                capture_output=True, text=True
            )
            return "Audio:" in result.stderr

        # ─────────────────────────────────────────────
        # FIXED: normalize audio to WAV for maximum compatibility
        # ─────────────────────────────────────────────
        def normalize_audio(path):
            normalized = "data/temp/voice_normalized.wav"
            try:
                subprocess.run([
                    ffmpeg_path,
                    "-y",
                    "-i", path,
                    "-ar", "44100",
                    "-ac", "2",
                    "-c:a", "pcm_s16le",
                    normalized
                ], check=True, capture_output=True, text=True)

                if os.path.exists(normalized) and os.path.getsize(normalized) > 100:
                    print("[OK] Audio normalized to WAV:", normalized)
                    return normalized
            except subprocess.CalledProcessError as e:
                print("[WARN] Audio normalization failed:", e.stderr or e)

            return path

        # ─────────────────────────────────────────────
        # FIXED: FFmpeg merge — reliable, stream-mapped
        # ─────────────────────────────────────────────
        def merge_audio_ffmpeg(video_path, audio_path, output_path):
            print("[INFO] Trying FFmpeg merge...")
            print(f"   Video: {video_path} ({os.path.getsize(video_path) if os.path.exists(video_path) else 'missing'})")
            print(f"   Audio: {audio_path} ({os.path.getsize(audio_path) if os.path.exists(audio_path) else 'missing'})")
            print(f"   Output: {output_path}")
            result = subprocess.run([
                ffmpeg_path,
                "-y",
                "-fflags", "+genpts",
                "-i", video_path,
                "-i", audio_path,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                output_path
            ], capture_output=True, text=True)

            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print("[OK] FFmpeg merge succeeded")
                print(f"   Output size: {os.path.getsize(output_path)}")
                return True

            print("[WARN] FFmpeg merge failed:")
            print("   Return code:", result.returncode)
            print("   Output exists:", os.path.exists(output_path))
            print("   Output size:", os.path.getsize(output_path) if os.path.exists(output_path) else "N/A")
            print("   Error output (last 500 chars):", (result.stderr[-500:] if result.stderr else result.stdout)[:500])
            return False

        # ─────────────────────────────────────────────
        # FIXED: MoviePy merge — handles both v1 and v2 API,
        #        with file-flush wait before validating output
        # ─────────────────────────────────────────────
        def merge_audio_moviepy(video_path, audio_path, output_path):
            print("[INFO] Trying MoviePy merge...")
            print(f"   Video: {video_path} ({os.path.getsize(video_path) if os.path.exists(video_path) else 'missing'})")
            print(f"   Audio: {audio_path} ({os.path.getsize(audio_path) if os.path.exists(audio_path) else 'missing'})")
            try:
                video_clip = VideoFileClip(video_path, audio=False)
                audio_clip = AudioFileClip(audio_path)
                print(f"[INFO] Video duration: {video_clip.duration:.2f}s")
                print(f"[INFO] Audio duration: {audio_clip.duration:.2f}s")

                # Trim audio to match video duration
                if audio_clip.duration > video_clip.duration:
                    audio_clip = audio_clip.subclip(0, video_clip.duration)
                    print(f"[INFO] Trimmed audio to {audio_clip.duration:.2f}s")

                # FIXED: support both MoviePy v1 (set_audio) and v2 (with_audio)
                try:
                    final_clip = video_clip.with_audio(audio_clip)   # v2
                    print("[OK] Using MoviePy v2 API (with_audio)")
                except AttributeError:
                    final_clip = video_clip.set_audio(audio_clip)    # v1
                    print("[OK] Using MoviePy v1 API (set_audio)")

                print(f"[INFO] Writing to: {output_path}")
                
                # FIXED: MoviePy v2 doesn't support 'verbose' parameter
                try:
                    final_clip.write_videofile(
                        output_path,
                        codec="libx264",
                        audio_codec="aac",
                        fps=24,
                        preset="fast",
                        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
                        verbose=False,
                        logger=None
                    )
                except TypeError as e:
                    if "verbose" in str(e):
                        print("   (MoviePy v2 detected, retrying without verbose parameter)")
                        final_clip.write_videofile(
                            output_path,
                            codec="libx264",
                            audio_codec="aac",
                            fps=24,
                            preset="fast",
                            ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"]
                        )
                    else:
                        raise

                audio_clip.close()
                final_clip.close()
                video_clip.close()

                # FIXED: wait for OS to flush file before validating
                time.sleep(0.5)

                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    print("[OK] MoviePy merge succeeded")
                    print(f"   Output size: {os.path.getsize(output_path)}")
                    return True

                print("⚠ MoviePy output file empty or missing")
                print(f"   Output exists: {os.path.exists(output_path)}")
                print(f"   Output size: {os.path.getsize(output_path) if os.path.exists(output_path) else 'N/A'}")
                return False

            except Exception as e:
                print("⚠ MoviePy merge failed:", e)
                import traceback
                print(traceback.format_exc())
                return False

        # ─────────────────────────────────────────────
        # FIXED: validate audio stream in output, not just file existence
        # ─────────────────────────────────────────────
        def validate_final_video_audio(video_path):
            try:
                # FIXED: wait for file flush before checking
                time.sleep(0.3)
                result = subprocess.run(
                    [ffmpeg_path, "-i", video_path],
                    capture_output=True, text=True
                )
                has_audio = "Audio:" in result.stderr
                print(f"   [INFO] Validation result: {'[OK] HAS AUDIO' if has_audio else '[ERROR] NO AUDIO'}")
                if not has_audio:
                    print("⚠ Output video has no audio stream")
                    print(f"   Output (last 300 chars): {result.stderr[-300:]}")
                return has_audio
            except Exception as e:
                print("⚠ Final audio validation failed:", e)
                return False

        # ─────────────────────────────────────────────
        # FIXED: clean merge attempt order with proper return values
        # ─────────────────────────────────────────────
        def merge_audio_attempts(video_path, audio_path, output_path):
            # Attempt 1: MoviePy
            if merge_audio_moviepy(video_path, audio_path, output_path):
                if validate_final_video_audio(output_path):
                    return True
                print("⚠ MoviePy output has no audio stream, falling back to FFmpeg")

            # Attempt 2: FFmpeg direct
            if merge_audio_ffmpeg(video_path, audio_path, output_path):
                if validate_final_video_audio(output_path):
                    return True
                print("⚠ FFmpeg output has no audio stream")

            return False

        # ─────────────────────────────────────────────
        # Main audio merge flow
        # ─────────────────────────────────────────────
        if has_valid_audio(audio_file):
            print("[INFO] Audio file found:", audio_file)
            print("[INFO] Audio file size:", os.path.getsize(audio_file))
            print(f"[INFO] Audio file exists: {os.path.exists(audio_file)}")
            print(f"[INFO] Temp video exists: {os.path.exists(temp_video)}")
            print(f"[INFO] Temp video size: {os.path.getsize(temp_video) if os.path.exists(temp_video) else 'N/A'}")

            audio_to_use = normalize_audio(audio_file)
            print(f"[INFO] Audio normalized to: {audio_to_use}")
            print(f"[INFO] Normalized audio exists: {os.path.exists(audio_to_use)}")
            print(f"[INFO] Normalized audio size: {os.path.getsize(audio_to_use) if os.path.exists(audio_to_use) else 'N/A'}")

            print("[INFO] Merging audio into video...")

            # Attempt with normalized audio
            print("[INFO] [ATTEMPT 1] Trying normalized audio...")
            if merge_audio_attempts(temp_video, audio_to_use, final_output):
                print("[OK] FINAL VIDEO CREATED with audio:", final_output)
                print(f"[OK] Final video size: {os.path.getsize(final_output)}")
                return final_output
            print("[ERROR] [ATTEMPT 1] failed")

            # Retry with original audio if normalization changed it
            if audio_to_use != audio_file:
                print("[INFO] [ATTEMPT 2] Retrying with original audio source...")
                if merge_audio_attempts(temp_video, audio_file, final_output):
                    print("[OK] FINAL VIDEO CREATED with original audio:", final_output)
                    print(f"[OK] Final video size: {os.path.getsize(final_output)}")
                    return final_output
                print("[ERROR] [ATTEMPT 2] failed")

            # WAV fallback
            print("[INFO] [ATTEMPT 3] Trying WAV fallback conversion...")
            wav_fallback = "data/temp/voice_fallback.wav"
            result = subprocess.run([
                ffmpeg_path,
                "-y",
                "-i", audio_file,
                "-ar", "44100",
                "-ac", "2",
                "-c:a", "pcm_s16le",
                wav_fallback
            ], check=False, capture_output=True, text=True)

            print(f"🔊 WAV fallback created: {os.path.exists(wav_fallback)}")
            if os.path.exists(wav_fallback):
                print(f"🔊 WAV fallback size: {os.path.getsize(wav_fallback)}")

            if os.path.exists(wav_fallback) and os.path.getsize(wav_fallback) > 100:
                print("🔊 WAV fallback created:", wav_fallback)
                print("🔊 [ATTEMPT 3a] Trying merge with WAV fallback...")
                if merge_audio_attempts(temp_video, wav_fallback, final_output):
                    print("✅ FINAL VIDEO CREATED with WAV fallback:", final_output)
                    print(f"✅ Final video size: {os.path.getsize(final_output)}")
                    return final_output
                print("❌ [ATTEMPT 3a] failed")

            # FIXED: return None instead of silently saving a silent video
            print("❌ All audio merge attempts failed — returning silent video")
            print(f"❌ Final output path: {final_output}")
            os.replace(temp_video, final_output)
            return None  # caller can handle/log this properly

        else:
            print("⚠ No valid audio stream found at:", audio_file)
            print(f"⚠ Audio file exists: {os.path.exists(audio_file)}")
            print(f"⚠ Audio file size: {os.path.getsize(audio_file) if os.path.exists(audio_file) else 'N/A'}")
            os.replace(temp_video, final_output)
            return None  # FIXED: return None so caller knows audio is missing
"""
Converts videos to vertical (9:16) format for YouTube Shorts, TikTok, Instagram Reels.
Handles various input formats and aspect ratios with intelligent padding/zooming.
"""

import os
import subprocess
import imageio_ffmpeg as ffmpeg
from pathlib import Path


class VerticalConverter:
    """Convert any video to vertical (9:16) format."""
    
    # Standard vertical output dimensions (9:16 aspect ratio)
    VERTICAL_WIDTH = 720
    VERTICAL_HEIGHT = 1280
    
    # Alternative resolutions (for backward compatibility / lower specs)
    RESOLUTIONS = {
        "1080p": (1080, 1920),  # 9:16
        "720p": (720, 1280),    # Default
        "480p": (480, 853),     # 9:16
    }
    
    # Scaling strategies
    SCALE_STRATEGIES = {
        "fit": "pad",          # Fit entire video, add padding (black bars)
        "fill": "crop_zoom",   # Fill screen, crop edges if needed
        "stretch": "scale",    # Stretch to fill (may distort)
    }
    
    def __init__(self, resolution="720p", scale_strategy="fit", output_fps=24):
        """
        Initialize vertical converter.
        
        Args:
            resolution: "1080p", "720p", or "480p"
            scale_strategy: "fit" (pad), "fill" (crop/zoom), "stretch"
            output_fps: Frames per second for output (default 24)
        """
        if resolution not in self.RESOLUTIONS:
            raise ValueError(f"Unknown resolution: {resolution}. Use: {list(self.RESOLUTIONS.keys())}")
        
        if scale_strategy not in self.SCALE_STRATEGIES:
            raise ValueError(f"Unknown strategy: {scale_strategy}. Use: {list(self.SCALE_STRATEGIES.keys())}")
        
        self.width, self.height = self.RESOLUTIONS[resolution]
        self.scale_strategy = self.SCALE_STRATEGIES[scale_strategy]
        self.output_fps = output_fps
        self.ffmpeg_path = ffmpeg.get_ffmpeg_exe()
    
    def get_video_info(self, video_path):
        """Get video dimensions and duration using ffprobe."""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=width,height,duration",
                 "-of", "default=noprint_wrappers=1:nokey=1:nokey=1",
                 video_path],
                capture_output=True, text=True, timeout=10
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                src_width = int(lines[0])
                src_height = int(lines[1])
                return {"width": src_width, "height": src_height}
        except Exception as e:
            print(f"[WARN] Could not get video info: {e}")
        
        return None
    
    def _calculate_fit_scale(self, src_width, src_height):
        """Calculate scaling to fit video into vertical canvas with padding."""
        src_aspect = src_width / src_height
        target_aspect = self.width / self.height
        
        if src_aspect > target_aspect:
            # Source is wider: scale by height
            scale_height = self.height
            scale_width = int(scale_height * src_aspect)
        else:
            # Source is taller: scale by width
            scale_width = self.width
            scale_height = int(scale_width / src_aspect)
        
        return scale_width, scale_height
    
    def _calculate_fill_scale(self, src_width, src_height):
        """Calculate scaling to fill vertical canvas (may crop edges)."""
        src_aspect = src_width / src_height
        target_aspect = self.width / self.height
        
        if src_aspect > target_aspect:
            # Source is wider: scale by width to fill height
            scale_width = self.width
            scale_height = int(scale_width / src_aspect)
        else:
            # Source is taller: scale by height to fill width
            scale_height = self.height
            scale_width = int(scale_height * src_aspect)
        
        return scale_width, scale_height
    
    def _build_ffmpeg_filter(self, src_width, src_height):
        """Build FFmpeg filter chain for scaling + padding/cropping."""
        if self.scale_strategy == "pad":
            scale_w, scale_h = self._calculate_fit_scale(src_width, src_height)
            x_offset = (self.width - scale_w) // 2
            y_offset = (self.height - scale_h) // 2
            
            filter_str = (
                f"scale={scale_w}:{scale_h},"
                f"pad={self.width}:{self.height}:{x_offset}:{y_offset}:black"
            )
        
        elif self.scale_strategy == "crop_zoom":
            scale_w, scale_h = self._calculate_fill_scale(src_width, src_height)
            x_offset = (scale_w - self.width) // 2
            y_offset = (scale_h - self.height) // 2
            
            filter_str = (
                f"scale={scale_w}:{scale_h},"
                f"crop={self.width}:{self.height}:{x_offset}:{y_offset}"
            )
        
        else:  # stretch
            filter_str = f"scale={self.width}:{self.height}"
        
        return filter_str
    
    def convert(self, input_path, output_path=None, keep_audio=True):
        """
        Convert video to vertical format.
        
        Args:
            input_path: Path to input video
            output_path: Path to output video (auto-generated if None)
            keep_audio: Whether to preserve audio
        
        Returns:
            Path to output video if successful, None otherwise
        """
        input_path = os.path.abspath(input_path)
        
        if not os.path.exists(input_path):
            print(f"[ERROR] Input video not found: {input_path}")
            return None
        
        if output_path is None:
            base = Path(input_path).stem
            output_path = f"data/output/{base}_vertical.mp4"
        
        output_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"\n[START] Converting to vertical format")
        print(f"  Input:  {input_path}")
        print(f"  Output: {output_path}")
        print(f"  Size:   {self.width}x{self.height}")
        print(f"  Strategy: {self.scale_strategy}")
        
        # Get source dimensions
        video_info = self.get_video_info(input_path)
        if not video_info:
            print("[ERROR] Could not read video dimensions")
            return None
        
        src_width, src_height = video_info["width"], video_info["height"]
        print(f"  Source: {src_width}x{src_height}")
        
        # Build FFmpeg filter
        filter_str = self._build_ffmpeg_filter(src_width, src_height)
        
        # Build FFmpeg command
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-i", input_path,
            "-vf", filter_str,
            "-r", str(self.output_fps),
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
        ]
        
        if keep_audio:
            cmd.extend(["-c:a", "aac", "-b:a", "192k"])
        else:
            cmd.append("-an")
        
        cmd.append(output_path)
        
        # Run conversion
        print("[INFO] Processing...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"[OK] Conversion complete!")
                print(f"  Output size: {size_mb:.2f} MB")
                return output_path
            else:
                print(f"[ERROR] Conversion failed (return code: {result.returncode})")
                if result.stderr:
                    print(f"  FFmpeg error: {result.stderr[-500:]}")
                return None
        
        except subprocess.TimeoutExpired:
            print("[ERROR] Conversion timeout (exceeded 5 minutes)")
            return None
        except Exception as e:
            print(f"[ERROR] Conversion error: {e}")
            return None
    
    def batch_convert(self, input_dir, output_dir=None, pattern="*.mp4"):
        """
        Convert all videos in a directory to vertical format.
        
        Args:
            input_dir: Directory containing videos
            output_dir: Output directory (default: input_dir/vertical/)
            pattern: File pattern to match (e.g., "*.mp4", "*.mov")
        
        Returns:
            List of successfully converted videos
        """
        input_dir = Path(input_dir)
        if not input_dir.exists():
            print(f"[ERROR] Input directory not found: {input_dir}")
            return []
        
        if output_dir is None:
            output_dir = input_dir / "vertical"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        videos = list(input_dir.glob(pattern))
        if not videos:
            print(f"[ERROR] No videos matching '{pattern}' in {input_dir}")
            return []
        
        print(f"\n[START] Batch converting {len(videos)} videos")
        
        successful = []
        for i, video_path in enumerate(videos, 1):
            print(f"\n[{i}/{len(videos)}] {video_path.name}")
            
            output_path = output_dir / f"{video_path.stem}_vertical.mp4"
            result = self.convert(str(video_path), str(output_path))
            
            if result:
                successful.append(result)
        
        print(f"\n[COMPLETE] {len(successful)}/{len(videos)} videos converted successfully")
        return successful


if __name__ == "__main__":
    # Example usage
    converter = VerticalConverter(resolution="720p", scale_strategy="fit")
    
    # Convert single video
    # output = converter.convert("input_video.mp4")
    
    # Batch convert
    # results = converter.batch_convert("videos/", pattern="*.mp4")

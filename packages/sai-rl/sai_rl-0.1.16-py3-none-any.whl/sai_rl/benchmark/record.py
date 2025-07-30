from typing import Callable, Optional
import gymnasium as gym
import imageio
import os
import subprocess
import time
from imageio_ffmpeg import get_ffmpeg_exe


class RecordingError(Exception):
    pass


def record_episode(
    env_creator: Callable[[str], gym.Env],
    render_mode: str,
    seed: int,
    actions: list[int],
    output_path: str,
    use_virtual_display: bool = False,
    max_steps: Optional[int] = None,
    ffmpeg_capture_size: str = "1280x720",
) -> None:
    env = env_creator(render_mode=render_mode)  # type: ignore
    env.reset(seed=seed)

    fps = env.metadata.get("render_fps", 60)
    render_mode = env.metadata.get("render_mode")

    os.makedirs(
        os.path.dirname(output_path) or ".",
        exist_ok=True,
    )

    writer = None
    ffmpeg_process = None
    original_sdl = os.environ.get("SDL_VIDEODRIVER")

    if use_virtual_display:
        os.environ["SDL_VIDEODRIVER"] = "dummy"

    try:
        if render_mode == "human":
            if "DISPLAY" not in os.environ:
                raise RecordingError("No DISPLAY for human mode recording.")
            ffmpeg_exe = get_ffmpeg_exe()
            cmd = [
                ffmpeg_exe,
                "-f",
                "x11grab",
                "-s",
                ffmpeg_capture_size,
                "-r",
                str(fps),
                "-i",
                os.environ["DISPLAY"],
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-pix_fmt",
                "yuv420p",
                "-y",
                output_path,
            ]
            ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            time.sleep(1.5)
            if ffmpeg_process.poll() is not None:
                out, err = ffmpeg_process.communicate()
                raise RecordingError(
                    f"FFmpeg error {ffmpeg_process.returncode}\n{out}\n{err}"
                )
        else:
            writer = imageio.get_writer(output_path, fps=fps)

        for i, action in enumerate(actions):
            if max_steps is not None and i >= max_steps:
                break

            _, _, terminated, truncated, _ = env.step(action)
            frame = env.render()
            if writer and frame is not None:
                writer.append_data(frame)
            if terminated or truncated:
                break

    except Exception:
        if ffmpeg_process and ffmpeg_process.poll() is None:
            ffmpeg_process.terminate()
            try:
                ffmpeg_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                ffmpeg_process.kill()
                ffmpeg_process.wait()
            ffmpeg_process.communicate()
        raise

    finally:
        if writer:
            writer.close()
        if ffmpeg_process:
            if ffmpeg_process.poll() is None:
                ffmpeg_process.terminate()
                try:
                    ffmpeg_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    ffmpeg_process.kill()
                    ffmpeg_process.wait()
            try:
                ffmpeg_process.communicate(timeout=5)
            except Exception:
                pass
        env.close()
        if use_virtual_display:
            if original_sdl is None:
                os.environ.pop("SDL_VIDEODRIVER", None)
            else:
                os.environ["SDL_VIDEODRIVER"] = original_sdl

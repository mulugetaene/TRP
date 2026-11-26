"""Stage: moving shots.
If a Wan 2.2 clip exists at outputs/clips/<id>.mp4 (made on Kaggle by kaggle/wan_shots.py) it is used.
Otherwise the shot falls back to a Ken Burns move over the keyframe, in both aspect ratios."""
import time
from common import OUT, Cache, input_hash, load_storyboard, log_call, ffmpeg

FPS = 24
SIZES = {"16x9": (1280, 720), "9x16": (720, 1280)}


def kenburns_filter(camera, frames, w, h):
    W, H = w * 2, h * 2  # upscale first so zoompan does not jitter
    z = {"push_in": "min(1+0.15*on/{f},1.15)", "pull_out": "max(1.15-0.15*on/{f},1)"}.get(camera, "1.12").format(f=frames)
    x = {"pan_left": "(iw-iw/zoom)*(1-on/{f})", "pan_right": "(iw-iw/zoom)*on/{f}"}.get(camera, "iw/2-(iw/zoom/2)").format(f=frames)
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={FPS},format=yuv420p")


def main():
    sb = load_storyboard()
    cache = Cache("shots")
    for s in sb["shots"]:
        kf = OUT / "keyframes" / f"{s['id']}.jpg"
        clip = OUT / "clips" / f"{s['id']}.mp4"
        src = clip if clip.exists() else kf
        h = input_hash(s["duration"], s["camera"], src.name, src.stat().st_mtime)
        for tag, (w, hgt) in SIZES.items():
            out = OUT / "shots" / tag / f"{s['id']}.mp4"
            out.parent.mkdir(parents=True, exist_ok=True)
            if cache.fresh(f"{s['id']}_{tag}", h, out):
                print(f"[shots] {s['id']} {tag} cached"); continue
            t0 = time.time()
            if clip.exists():
                # Trim the weak first 0.3s, loop if short, scale+crop to the target frame.
                ffmpeg("-stream_loop", "-1", "-ss", "0.3", "-i", clip, "-t", s["duration"],
                       "-vf", f"scale={w}:{hgt}:force_original_aspect_ratio=increase,crop={w}:{hgt},fps={FPS},format=yuv420p",
                       "-an", "-c:v", "libx264", "-preset", "veryfast", out)
                mode = "wan-clip"
            else:
                frames = int(s["duration"] * FPS)
                ffmpeg("-loop", "1", "-i", kf, "-vf", kenburns_filter(s["camera"], frames, w, hgt),
                       "-frames:v", frames, "-c:v", "libx264", "-preset", "veryfast", out)
                mode = "kenburns"
            log_call("shots", f"ffmpeg-{mode}", {"shot": s["id"], "aspect": tag}, time.time() - t0)
            cache.put(f"{s['id']}_{tag}", h)
            print(f"[shots] {s['id']} {tag} {mode}")


if __name__ == "__main__":
    main()

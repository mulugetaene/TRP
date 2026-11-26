"""Stage: music. The score is generated with ACE-Step 1.5 on Kaggle (kaggle/acestep_score.py), which writes
candidates to outputs/music/. The chosen one is set in storyboard.json -> music.chosen_file.
If it is missing, a quiet placeholder pad is synthesised so the radio cut can still be assembled."""
import time
from common import ROOT, OUT, load_storyboard, log_call, ffmpeg


def main():
    sb = load_storyboard()
    chosen = ROOT / sb["music"]["chosen_file"]
    if chosen.exists():
        print(f"[music] using {chosen.relative_to(ROOT)}"); return
    chosen.parent.mkdir(parents=True, exist_ok=True)
    total = sum(s["duration"] for s in sb["shots"]) + sb["end_card"]["duration"]
    t0 = time.time()
    ffmpeg("-f", "lavfi", "-i", f"sine=f=130.8:d={total}", "-f", "lavfi", "-i", f"sine=f=196:d={total}",
           "-filter_complex", "amix=inputs=2,volume=0.3,afade=t=in:d=2,afade=t=out:st=" + str(total - 3) + ":d=3",
           "-ar", "48000", chosen)
    log_call("music", "placeholder-sine-pad", {"duration": total}, time.time() - t0, note="ACE-Step score not yet present")
    print("[music] placeholder pad written (replace with ACE-Step output)")


if __name__ == "__main__":
    main()
